'''
NES CPU: Ricoh 2A05
'''

import numpy as np
import logging
import instructions
from addressmodes import *

f=open("cpu.log","w")

scanlines = 241

class CPU:
    '''
    CPU emulation
    '''
    class Memory:
        def __init__(self, nes):
            self._nes = nes
            self._memory = bytearray(0x10000)
            self._memory[0x100:0x200] = [0xff] * 0xff

        def read(self, addr):
            # The Zero Page, Stack, and RAM mirrored 4 times, we will only
            # use one copy rather than mirroring them all since we have a
            # mod operator
            if 0x0 <= addr < 0x2000:
                return self._memory[addr] & 0xff
            # I/O Registers, mirrored a bunch of times
            elif 0x2000 <= addr < 0x4000:
                offset = addr % 0x8
                return self._nes.ppu.read_register(0x2000 + offset)
            # Controller ports
            elif addr == 0x4016 or addr == 0x4017:
                return self._nes.cpu.controller.read(addr)
            # Unmirrored I/O registers, Expansion ROM, and Save RAM
            elif 0x4000 <= addr < 0x8000:
                return self._memory[addr] & 0xff
            # Cartridge ROM
            elif 0x8000 <= addr < 0x10000:
                # return the cartridge ROM value
                return (self._nes.rom.read_prg(addr) & 0xff)
            else:
                raise Exception("Out of memory bounds read at {:#06x}".format(addr))

        def write(self, addr, value):
            if addr < 0x0 or addr > 0xffff:
                raise Exception("Out of memory bounds write at {:#06x}".format(addr))
            # The Zero Page, Stack, and RAM mirrored 4 times, we will only
            # use one copy rather than mirroring them all since we have a
            # mod operator
            elif 0x0 <= addr < 0x2000:
                self._memory[addr] = value
            # I/O Registers, mirrored a bunch of times
            elif 0x2000 <= addr < 0x4000:
                offset = addr % 0x8
                self._nes.ppu.write_register(0x2000 + offset, value)
            # Unmirrored I/O registers
            elif addr == 0x4014:
                self._nes.ppu.write_register(0x4014, value)
            elif addr == 0x4016:
                self._nes.cpu.controller.write(value)
                # a write to 4016 writes to both 4016 and 4017
                self._memory[addr] = value
                self._memory[0x4017] = value
            elif 0x4000 <= addr < 0x4020:
                self._memory[addr] = value
            # Expansion ROM cannot be written to
            elif 0x4020 <= addr < 0x6000:
                raise Exception("Cannot write to Expansion ROM at address {:#06x}!".format(addr))
            # Save RAM
            elif 0x6000 <= addr < 0x8000:
                self._memory[addr] = value
            # Cartridge ROM
            elif 0x8000 <= addr < 0x10000:
                raise Exception("Cannot write to ROM at address {:#06x}!".format(addr))


    class Register:
        def __init__(self, size):
            self._size = size
            self._value = 0x00

        def read(self):
            return self._value

        def write(self, value):
            if self._size == 8:
                bits = 0xff
            else:
                bits = 0xffff
            self._value = value & bits

        def assign_bit(self, bit_number, set_it):
            if set_it:
                self._value |= 0x1 << bit_number
            else:
                self._value &= ~(0x1 << bit_number)

        def adjust(self, value=1):
            self.write(self._value + value)


    class Instruction:
        def __init__(self, cpu, instruction, addr_mode, cycles):
            self._cpu = cpu
            self._instruction = instruction
            self._addressing = addr_mode
            self._cycles = cycles

        def __call__(self, op1, op2):

            extra_cycles = self._instruction(self._cpu, self._addressing, op1, op2)
            return self._cycles + extra_cycles

    class Controller:
        def __init__(self):
            self._shiftreg = [0,0]
            self._controllerstatus = [0,0]
            # self._shift = [0,0]
            self._strobe = 0
            self.buttons = {
                'up': 4,
                'down': 5,
                'left': 6,
                'right': 7,
                'a': 0,
                'b': 1,
                'select': 2,
                'start': 3
            }
        def button_change(self, gamepad, button, updown):
            curr = self._controllerstatus[gamepad-1]
            curr &= ~(1<<self.buttons[button])  # clear button bit
            if updown:
                curr |= 1<<self.buttons[button]  # set button bit if pressed
            self._controllerstatus[gamepad-1] = curr

        def write(self, val):
            if self._strobe and not val&1:
                self._shiftreg[0] = ~0 & self._controllerstatus[0]
                self._shiftreg[1] = ~0 & self._controllerstatus[1]
            self._strobe = val&1

        def read(self, reg):
            reg -= 0x4016
            if self._strobe:
                return self._controllerstatus[reg] & 1
            else:
                ret = self._shiftreg[reg] & 1
                self._shiftreg[reg] >>= 1
                return ret


    def __init__(self, nes, cart):
        self._nes = nes
        self.memory = CPU.Memory(nes)
        self._cycles = 0
        self._cart = cart
        self.controller = CPU.Controller(self)

        # interrupt flags
        self.irq_requested = 0
        self.nmi_requested = 0

        # Create the CPU registers
        self.registers = {'pc': CPU.Register(16), 'sp': CPU.Register(8),
                          'a': CPU.Register(8), 'x': CPU.Register(8),
                          'y': CPU.Register(8), 'p': CPU.Register(8)}

        # Bit positions in the status register
        self.status = {'carry': 0, 'zero': 1, 'interrupt': 2, 'decimal': 3,
                       'break': 4, 'unused': 5, 'overflow': 6, 'negative': 7}

        self.opcodes = {
            0x00: CPU.Instruction(self, instructions.BRK, AddressingMode.Implied, 7),
            0x01: CPU.Instruction(self, instructions.ORA, AddressingMode.Indirect_X, 6),
            0x03: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Indirect_X, 8), # undocumented
            0x04: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 3),  # undocumented
            0x05: CPU.Instruction(self, instructions.ORA, AddressingMode.Zero_Page, 3),
            0x06: CPU.Instruction(self, instructions.ASL, AddressingMode.Zero_Page, 5),
            0x07: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Zero_Page, 5), # undocumented
            0x08: CPU.Instruction(self, instructions.PHP, AddressingMode.Implied, 3),
            0x09: CPU.Instruction(self, instructions.ORA, AddressingMode.Immediate, 2),
            0x0a: CPU.Instruction(self, instructions.ASL, AddressingMode.Accumulator, 2),
            0x0c: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute, 4),  # undocumented
            0x0d: CPU.Instruction(self, instructions.ORA, AddressingMode.Absolute, 4),
            0x0e: CPU.Instruction(self, instructions.ASL, AddressingMode.Absolute, 6),
            0x0f: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Absolute, 6), # undocumented

            0x10: CPU.Instruction(self, instructions.BPL, AddressingMode.Relative, 2),
            0x11: CPU.Instruction(self, instructions.ORA, AddressingMode.Indirect_Y, 5),
            0x13: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Indirect_Y, 8), # undocumented
            0x14: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 4),  # undocumented
            0x15: CPU.Instruction(self, instructions.ORA, AddressingMode.Zero_Page_X, 4),
            0x16: CPU.Instruction(self, instructions.ASL, AddressingMode.Zero_Page_X, 6),
            0x17: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Zero_Page_X, 6), # undocumented
            0x18: CPU.Instruction(self, instructions.CLC, AddressingMode.Implied, 2),
            0x19: CPU.Instruction(self, instructions.ORA, AddressingMode.Absolute_Y, 4),
            0x1a: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Implied, 2),
            0x1b: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Absolute_Y, 7), # undocumented
            0x1c: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute_X, 4),  # undocumented
            0x1d: CPU.Instruction(self, instructions.ORA, AddressingMode.Absolute_X, 4),
            0x1e: CPU.Instruction(self, instructions.ASL, AddressingMode.Absolute_X, 7),
            0x1f: CPU.Instruction(self, instructions.SLO_UNDOC, AddressingMode.Absolute_X, 7), # undocumented

            0x20: CPU.Instruction(self, instructions.JSR, AddressingMode.JMP_Absolute, 6),
            0x21: CPU.Instruction(self, instructions.AND, AddressingMode.Indirect_X, 6),
            0x23: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Indirect_X, 8), # undocumented
            0x24: CPU.Instruction(self, instructions.BIT, AddressingMode.Zero_Page, 3),
            0x25: CPU.Instruction(self, instructions.AND, AddressingMode.Zero_Page, 3),
            0x26: CPU.Instruction(self, instructions.ROL, AddressingMode.Zero_Page, 5),
            0x27: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Zero_Page, 5), # undocumented
            0x28: CPU.Instruction(self, instructions.PLP, AddressingMode.Implied, 4),
            0x29: CPU.Instruction(self, instructions.AND, AddressingMode.Immediate, 2),
            0x2a: CPU.Instruction(self, instructions.ROL, AddressingMode.Accumulator, 2),
            0x2c: CPU.Instruction(self, instructions.BIT, AddressingMode.Absolute, 4),
            0x2d: CPU.Instruction(self, instructions.AND, AddressingMode.Absolute, 4),
            0x2e: CPU.Instruction(self, instructions.ROL, AddressingMode.Absolute, 6),
            0x2f: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Absolute, 6), # undocumented

            0x30: CPU.Instruction(self, instructions.BMI, AddressingMode.Relative, 2),
            0x31: CPU.Instruction(self, instructions.AND, AddressingMode.Indirect_Y, 5),
            0x33: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Indirect_Y, 8), # undocumented
            0x34: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 4),  # undocumented
            0x35: CPU.Instruction(self, instructions.AND, AddressingMode.Zero_Page_X, 4),
            0x36: CPU.Instruction(self, instructions.ROL, AddressingMode.Zero_Page_X, 6),
            0x37: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Zero_Page_X, 6), # undocumented
            0x38: CPU.Instruction(self, instructions.SEC, AddressingMode.Implied, 2),
            0x39: CPU.Instruction(self, instructions.AND, AddressingMode.Absolute_Y, 4),
            0x3a: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Implied, 2),
            0x3b: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Absolute_Y, 7), # undocumented
            0x3c: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute_X, 4),  # undocumented
            0x3d: CPU.Instruction(self, instructions.AND, AddressingMode.Absolute_X, 4),
            0x3e: CPU.Instruction(self, instructions.ROL, AddressingMode.Absolute_X, 7),
            0x3f: CPU.Instruction(self, instructions.RLA_UNDOC, AddressingMode.Absolute_X, 7), # undocumented

            0x40: CPU.Instruction(self, instructions.RTI, AddressingMode.Implied, 6),
            0x41: CPU.Instruction(self, instructions.EOR, AddressingMode.Indirect_X, 6),
            0x43: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Indirect_X, 8),   # undocumented
            0x44: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 3),  # undocumented
            0x45: CPU.Instruction(self, instructions.EOR, AddressingMode.Zero_Page, 3),
            0x46: CPU.Instruction(self, instructions.LSR, AddressingMode.Zero_Page, 5),
            0x47: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Zero_Page, 5),   # undocumented
            0x48: CPU.Instruction(self, instructions.PHA, AddressingMode.Implied, 3),
            0x49: CPU.Instruction(self, instructions.EOR, AddressingMode.Immediate, 2),
            0x4a: CPU.Instruction(self, instructions.LSR, AddressingMode.Accumulator, 2),
            0x4c: CPU.Instruction(self, instructions.JMP, AddressingMode.JMP_Absolute, 3),
            0x4d: CPU.Instruction(self, instructions.EOR, AddressingMode.Absolute, 4),
            0x4e: CPU.Instruction(self, instructions.LSR, AddressingMode.Absolute, 6),
            0x4f: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Absolute, 6),   # undocumented

            0x50: CPU.Instruction(self, instructions.BVC, AddressingMode.Relative, 2),
            0x51: CPU.Instruction(self, instructions.EOR, AddressingMode.Indirect_Y, 5),
            0x53: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Indirect_Y, 8),   # undocumented
            0x54: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 4),  # undocumented
            0x55: CPU.Instruction(self, instructions.EOR, AddressingMode.Zero_Page_X, 4),
            0x56: CPU.Instruction(self, instructions.LSR, AddressingMode.Zero_Page_X, 6),
            0x57: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Zero_Page_X, 6),   # undocumented
            0x58: CPU.Instruction(self, instructions.CLI, AddressingMode.Implied, 2),
            0x59: CPU.Instruction(self, instructions.EOR, AddressingMode.Absolute_Y, 4),
            0x5a: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Implied, 2),
            0x5b: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Absolute_Y, 7),   # undocumented
            0x5c: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute_X, 4),  # undocumented
            0x5d: CPU.Instruction(self, instructions.EOR, AddressingMode.Absolute_X, 4),
            0x5e: CPU.Instruction(self, instructions.LSR, AddressingMode.Absolute_X, 7),
            0x5f: CPU.Instruction(self, instructions.SRE_UNDOC, AddressingMode.Absolute_X, 7),   # undocumented

            0x60: CPU.Instruction(self, instructions.RTS, AddressingMode.Implied, 6),
            0x61: CPU.Instruction(self, instructions.ADC, AddressingMode.Indirect_X, 6),
            0x63: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Indirect_X, 8), # undocumented
            0x64: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 3),  # undocumented
            0x65: CPU.Instruction(self, instructions.ADC, AddressingMode.Zero_Page, 3),
            0x66: CPU.Instruction(self, instructions.ROR, AddressingMode.Zero_Page, 5),
            0x67: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Zero_Page, 5), # undocumented
            0x68: CPU.Instruction(self, instructions.PLA, AddressingMode.Implied, 4),
            0x69: CPU.Instruction(self, instructions.ADC, AddressingMode.Immediate, 2),
            0x6a: CPU.Instruction(self, instructions.ROR, AddressingMode.Accumulator, 2),
            0x6c: CPU.Instruction(self, instructions.JMP, AddressingMode.Indirect, 5),
            0x6d: CPU.Instruction(self, instructions.ADC, AddressingMode.Absolute, 4),
            0x6e: CPU.Instruction(self, instructions.ROR, AddressingMode.Absolute, 6),
            0x6f: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Absolute, 6), # undocumented

            0x70: CPU.Instruction(self, instructions.BVS, AddressingMode.Relative, 2),
            0x71: CPU.Instruction(self, instructions.ADC, AddressingMode.Indirect_Y, 5),
            0x73: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Indirect_Y, 8), # undocumented
            0x74: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 4),  # undocumented
            0x75: CPU.Instruction(self, instructions.ADC, AddressingMode.Zero_Page_X, 4),
            0x76: CPU.Instruction(self, instructions.ROR, AddressingMode.Zero_Page_X, 6),
            0x77: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Zero_Page_X, 6), # undocumented
            0x78: CPU.Instruction(self, instructions.SEI, AddressingMode.Implied, 2),
            0x79: CPU.Instruction(self, instructions.ADC, AddressingMode.Absolute_Y, 4),
            0x7a: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Implied, 2),
            0x7b: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Absolute_Y, 7), # undocumented
            0x7c: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute_X, 4),  # undocumented
            0x7d: CPU.Instruction(self, instructions.ADC, AddressingMode.Absolute_X, 4),
            0x7e: CPU.Instruction(self, instructions.ROR, AddressingMode.Absolute_X, 7),
            0x7f: CPU.Instruction(self, instructions.RRA_UNDOC, AddressingMode.Absolute_X, 7), # undocumented

            0x80: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 2),
            0x81: CPU.Instruction(self, instructions.STA, AddressingMode.Indirect_X, 6),
            0x83: CPU.Instruction(self, instructions.SAX_UNDOC, AddressingMode.Indirect_X, 6),   # undocumented
            0x84: CPU.Instruction(self, instructions.STY, AddressingMode.Zero_Page, 3),
            0x85: CPU.Instruction(self, instructions.STA, AddressingMode.Zero_Page, 3),
            0x86: CPU.Instruction(self, instructions.STX, AddressingMode.Zero_Page, 3),
            0x87: CPU.Instruction(self, instructions.SAX_UNDOC, AddressingMode.Zero_Page, 3),   # undocumented
            0x88: CPU.Instruction(self, instructions.DEY, AddressingMode.Implied, 2),
            0x8a: CPU.Instruction(self, instructions.TXA, AddressingMode.Implied, 2),
            0x8c: CPU.Instruction(self, instructions.STY, AddressingMode.Absolute, 4),
            0x8d: CPU.Instruction(self, instructions.STA, AddressingMode.Absolute, 4),
            0x8e: CPU.Instruction(self, instructions.STX, AddressingMode.Absolute, 4),
            0x8f: CPU.Instruction(self, instructions.SAX_UNDOC, AddressingMode.Absolute, 4),   # undocumented

            0x90: CPU.Instruction(self, instructions.BCC, AddressingMode.Relative, 2),
            0x91: CPU.Instruction(self, instructions.STA, AddressingMode.Indirect_Y, 6),
            0x94: CPU.Instruction(self, instructions.STY, AddressingMode.Zero_Page_X, 4),
            0x95: CPU.Instruction(self, instructions.STA, AddressingMode.Zero_Page_X, 4),
            0x96: CPU.Instruction(self, instructions.STX, AddressingMode.Zero_Page_Y, 4),
            0x97: CPU.Instruction(self, instructions.SAX_UNDOC, AddressingMode.Zero_Page_Y, 4),   # undocumented
            0x98: CPU.Instruction(self, instructions.TYA, AddressingMode.Implied, 2),
            0x99: CPU.Instruction(self, instructions.STA, AddressingMode.Absolute_Y, 5),
            0x9a: CPU.Instruction(self, instructions.TXS, AddressingMode.Implied, 2),
            0x9d: CPU.Instruction(self, instructions.STA, AddressingMode.Absolute_X, 5),

            0xa0: CPU.Instruction(self, instructions.LDY, AddressingMode.Immediate, 2),
            0xa1: CPU.Instruction(self, instructions.LDA, AddressingMode.Indirect_X, 6),
            0xa2: CPU.Instruction(self, instructions.LDX, AddressingMode.Immediate, 2),
            0xa3: CPU.Instruction(self, instructions.LAX_UNDOC, AddressingMode.Indirect_X, 6),   # undocumented
            0xa4: CPU.Instruction(self, instructions.LDY, AddressingMode.Zero_Page, 3),
            0xa5: CPU.Instruction(self, instructions.LDA, AddressingMode.Zero_Page, 3),
            0xa6: CPU.Instruction(self, instructions.LDX, AddressingMode.Zero_Page, 3),
            0xa7: CPU.Instruction(self, instructions.LAX_UNDOC, AddressingMode.Zero_Page, 3),   # undocumented
            0xa8: CPU.Instruction(self, instructions.TAY, AddressingMode.Implied, 2),
            0xa9: CPU.Instruction(self, instructions.LDA, AddressingMode.Immediate, 2),
            0xaa: CPU.Instruction(self, instructions.TAX, AddressingMode.Implied, 2),
            0xad: CPU.Instruction(self, instructions.LDA, AddressingMode.Absolute, 4),
            0xac: CPU.Instruction(self, instructions.LDY, AddressingMode.Absolute, 4),
            0xae: CPU.Instruction(self, instructions.LDX, AddressingMode.Absolute, 4),
            0xaf: CPU.Instruction(self, instructions.LAX_UNDOC, AddressingMode.Absolute, 4),   # undocumented

            0xb0: CPU.Instruction(self, instructions.BCS, AddressingMode.Relative, 2),
            0xb1: CPU.Instruction(self, instructions.LDA, AddressingMode.Indirect_Y, 5),
            0xb3: CPU.Instruction(self, instructions.LAX_UNDOC, AddressingMode.Indirect_Y, 5),   # undocumented
            0xb4: CPU.Instruction(self, instructions.LDY, AddressingMode.Zero_Page_X, 4),
            0xb5: CPU.Instruction(self, instructions.LDA, AddressingMode.Zero_Page_X, 4),
            0xb6: CPU.Instruction(self, instructions.LDX, AddressingMode.Zero_Page_Y, 4),
            0xb7: CPU.Instruction(self, instructions.LAX_UNDOC, AddressingMode.Zero_Page_Y, 4),   # undocumented
            0xb8: CPU.Instruction(self, instructions.CLV, AddressingMode.Implied, 2),
            0xb9: CPU.Instruction(self, instructions.LDA, AddressingMode.Absolute_Y, 4),
            0xba: CPU.Instruction(self, instructions.TSX, AddressingMode.Implied, 2),
            0xbc: CPU.Instruction(self, instructions.LDY, AddressingMode.Absolute_X, 4),
            0xbd: CPU.Instruction(self, instructions.LDA, AddressingMode.Absolute_X, 4),
            0xbe: CPU.Instruction(self, instructions.LDX, AddressingMode.Absolute_Y, 4),
            0xbf: CPU.Instruction(self, instructions.LAX_UNDOC, AddressingMode.Absolute_Y, 4),   # undocumented

            0xc0: CPU.Instruction(self, instructions.CPY, AddressingMode.Immediate, 2),
            0xc1: CPU.Instruction(self, instructions.CMP, AddressingMode.Indirect_X, 6),
            0xc3: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Indirect_X, 8), # undocumented
            0xc4: CPU.Instruction(self, instructions.CPY, AddressingMode.Zero_Page, 3),
            0xc5: CPU.Instruction(self, instructions.CMP, AddressingMode.Zero_Page, 3),
            0xc6: CPU.Instruction(self, instructions.DEC, AddressingMode.Zero_Page, 5),
            0xc7: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Zero_Page, 5), # undocumented
            0xc8: CPU.Instruction(self, instructions.INY, AddressingMode.Implied, 2),
            0xc9: CPU.Instruction(self, instructions.CMP, AddressingMode.Immediate, 2),
            0xca: CPU.Instruction(self, instructions.DEX, AddressingMode.Implied, 2),
            0xcc: CPU.Instruction(self, instructions.CPY, AddressingMode.Absolute, 4),
            0xcd: CPU.Instruction(self, instructions.CMP, AddressingMode.Absolute, 4),
            0xce: CPU.Instruction(self, instructions.DEC, AddressingMode.Absolute, 6),
            0xcf: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Absolute, 6), # undocumented

            0xd0: CPU.Instruction(self, instructions.BNE, AddressingMode.Relative, 2),
            0xd1: CPU.Instruction(self, instructions.CMP, AddressingMode.Indirect_Y, 5),
            0xd3: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Indirect_Y, 8), # undocumented
            0xd4: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 4),  # undocumented
            0xd5: CPU.Instruction(self, instructions.CMP, AddressingMode.Zero_Page_X, 4),
            0xd6: CPU.Instruction(self, instructions.DEC, AddressingMode.Zero_Page_X, 6),
            0xd7: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Zero_Page_X, 6), # undocumented
            0xd8: CPU.Instruction(self, instructions.CLD, AddressingMode.Implied, 2),
            0xd9: CPU.Instruction(self, instructions.CMP, AddressingMode.Absolute_Y, 4),
            0xda: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Implied, 2),
            0xdb: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Absolute_Y, 7), # undocumented
            0xdc: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute_X, 4),  # undocumented
            0xdd: CPU.Instruction(self, instructions.CMP, AddressingMode.Absolute_X, 4),
            0xde: CPU.Instruction(self, instructions.DEC, AddressingMode.Absolute_X, 7),
            0xdf: CPU.Instruction(self, instructions.DCP_UNDOC, AddressingMode.Absolute_X, 7), # undocumented

            0xe0: CPU.Instruction(self, instructions.CPX, AddressingMode.Immediate, 2),
            0xe1: CPU.Instruction(self, instructions.SBC, AddressingMode.Indirect_X, 6),
            0xe3: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Indirect_X, 8), # undocumented
            0xe4: CPU.Instruction(self, instructions.CPX, AddressingMode.Zero_Page, 3),
            0xe5: CPU.Instruction(self, instructions.SBC, AddressingMode.Zero_Page, 3),
            0xe6: CPU.Instruction(self, instructions.INC, AddressingMode.Zero_Page, 5),
            0xe7: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Zero_Page, 5), # undocumented
            0xe8: CPU.Instruction(self, instructions.INX, AddressingMode.Implied, 2),
            0xe9: CPU.Instruction(self, instructions.SBC, AddressingMode.Immediate, 2),
            0xea: CPU.Instruction(self, instructions.NOP, AddressingMode.Implied, 2),
            0xeb: CPU.Instruction(self, instructions.SBC_UNDOC, AddressingMode.Immediate, 2), # undocumented
            0xec: CPU.Instruction(self, instructions.CPX, AddressingMode.Absolute, 4),
            0xed: CPU.Instruction(self, instructions.SBC, AddressingMode.Absolute, 4),
            0xee: CPU.Instruction(self, instructions.INC, AddressingMode.Absolute, 6),
            0xef: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Absolute, 6), # undocumented

            0xf0: CPU.Instruction(self, instructions.BEQ, AddressingMode.Relative, 2),
            0xf1: CPU.Instruction(self, instructions.SBC, AddressingMode.Indirect_Y, 5),
            0xf3: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Indirect_Y, 8), # undocumented
            0xf4: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Immediate, 4),  # undocumented
            0xf5: CPU.Instruction(self, instructions.SBC, AddressingMode.Zero_Page_X, 4),
            0xf6: CPU.Instruction(self, instructions.INC, AddressingMode.Zero_Page_X, 6),
            0xf7: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Zero_Page_X, 6), # undocumented
            0xf8: CPU.Instruction(self, instructions.SED, AddressingMode.Implied, 2),
            0xf9: CPU.Instruction(self, instructions.SBC, AddressingMode.Absolute_Y, 4),
            0xfa: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Implied, 2),
            0xfb: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Absolute_Y, 7), # undocumented
            0xfd: CPU.Instruction(self, instructions.SBC, AddressingMode.Absolute_X, 4),
            0xfc: CPU.Instruction(self, instructions.NOP_UNDOC, AddressingMode.Absolute_X, 4),  # undocumented
            0xfe: CPU.Instruction(self, instructions.INC, AddressingMode.Absolute_X, 7),
            0xff: CPU.Instruction(self, instructions.ISB_UNDOC, AddressingMode.Absolute_X, 7) # undocumented
        }

        self.registers['pc'].write(0xc000)
        self.registers['p'].write(0x24)
        self.registers['sp'].write(0xfd)
        self.memory._memory[0x0000:0x0800] = [0xff]
        self.memory._memory[0x0008] = 0xf7
        self.memory._memory[0x0009] = 0xef
        self.memory._memory[0x000a] = 0xdf
        self.memory._memory[0x000f] = 0xbf

    def execute(self, debug=True):
        global scanlines
        # fetch
        cycles = 0
        # check for interrupts
        if self.irq_requested:
            if not self.get_status('interrupt'):
                self.irq()
                self.interrupt_requested = 0
        elif self.nmi_requested:
            self.nmi()
            self.nmi_requested = 0
            cycles += 7

        pc = self.registers['pc'].read()
        opcode = self.memory.read(pc)

        # decode
        operands = self.opcodes[opcode]._addressing.byte_size
        ops = [None, None]

        for i in range(operands):
            if i == 0: continue # skip instruction opcode
            ops[i-1] = self.memory.read(pc + i) # fill in operands
        # update program counter
        self.registers['pc'].write(pc + operands)

        #execute
        if debug:
            f.write("{:04X}  {:02X} {} {} {}   A:{:02X} X:{:02X} Y:{:02X} P:{:02X} SP:{:02X} CYC:{:3} SL:{}\n".format(pc, opcode,
                                                            "  " if ops[0] == None else "{:02X}".format(ops[0]), "  " if ops[1] == None else "{:02X}".format(ops[1]),
                                                            self.opcodes[opcode]._instruction.__doc__,
                            self.registers['a'].read(), self.registers['x'].read(), self.registers['y'].read(),
                            self.registers['p'].read(), self.registers['sp'].read(), self._cycles, scanlines))
        cycles += self.opcodes[opcode](ops[0], ops[1])

        temp = self._cycles
        self._cycles = (self._cycles + cycles * 3) % 341 # times 3 for ppu multiplier
        if temp > self._cycles:
            scanlines += 1
            if scanlines == 261:
                scanlines = -1

        return cycles

    def run(self):
        global scanlines
        while True:
            self.execute()

    # status methods
    def get_status(self, flag):
        pos = self.status[flag]
        return (self.registers['p'].read() >> pos) & 0x1

    def set_status(self, flag, value):
        self.registers['p'].assign_bit(self.status[flag], value)

    # Stack methods
    def push_stack(self, value):
        self.memory.write(0x100 + self.registers['sp'].read(), value)
        self.registers['sp'].adjust(value=-1)

    def pop_stack(self):
        self.registers['sp'].adjust(value=1)
        result = self.memory.read(0x100 + self.registers['sp'].read())
        return result

    def set_reset_vector(self):
        high = self.memory.read(0xfffd)
        low = self.memory.read(0xfffc)

        self.registers['pc'].write((high << 8) + low)

    def reset(self):
        self.registers['x'].write(0)
        self.registers['y'].write(0)
        self.registers['a'].write(0)
        self.registers['p'].write(0x34)
        self.registers['sp'].write(0xfd)
        self.cycles = 0
        # self.set_reset_vector()

        # interrupt stuff?

    def irq(self):
        pc = self.registers['pc'].read()
        high = pc >> 8
        low = pc & 0xff

        self.push_stack(high)
        self.push_stack(low)
        self.push_stack(self.registers['p'].read())

        high = self.memory.read(0xffff)
        low = self.memory.read(0xfffe)

        self.registers['pc'].write((high << 8) + low)

    def nmi(self):
        pc = self.registers['pc'].read()
        high = pc >> 8
        low = pc & 0xff

        self.push_stack(high)
        self.push_stack(low)
        self.push_stack(self.registers['p'].read())

        high = self.memory.read(0xfffb)
        low = self.memory.read(0xfffa)
        self.registers['pc'].write((high << 8) + low)
