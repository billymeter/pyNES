'''
NES CPU: Ricoh 2A05
'''

import numpy as np
import instructions
from addressmodes import *


class CPU:
    '''
    CPU emulation
    '''
    class Memory:
        def __init__(self, nes):
            self._nes = nes
            self._memory = bytearray(0x10000)

        def read(self, addr):
            if addr < 0x0 or addr > 0xffff:
                raise Exception("Out of memory bounds read at {:#06x}".format(addr))
            # The Zero Page, Stack, and RAM mirrored 4 times, we will only
            # use one copy rather than mirroring them all since we have a
            # mod operator
            elif 0x0 <= addr < 0x2000:
                #base_addr = addr % 0x800
                #return self.memory[base_addr]
                return self.memory[addr]
            # I/O Registers, mirrored a bunch of times
            elif 0x2000 <= addr < 0x4000:
                #base_addr = (addr - 0x2000) % 0x8
                #return self.memory[base_addr + 0x2000]
                offset = addr % 0x8
                return self._nes.ppu.read_register(0x2000 + offset)
            # Unmirrored I/O registers, Expansion ROM, and Save RAM
            elif 0x4000 <= addr < 0x8000:
                return self.memory[addr]
            # Cartridge ROM
            elif 0x8000 <= addr < 0x10000:
                # return the cartridge ROM value
                self._nes.rom.read_prg(addr)

        def write(self, addr, value):
            if addr < 0x0 or addr > 0xffff:
                raise Exception("Out of memory bounds write at {:#06x}".format(addr))
            # The Zero Page, Stack, and RAM mirrored 4 times, we will only
            # use one copy rather than mirroring them all since we have a
            # mod operator
            elif 0x0 <= addr < 0x2000:
                #base_addr = addr % 0x800
                #self.memory[base_addr] = value
                self.memory[addr] = value
            # I/O Registers, mirrored a bunch of times
            elif 0x2000 <= addr < 0x4000:
                #base_addr = (addr - 0x2000) % 0x8
                #self.memory[base_addr + 0x2000] = value
                offset = addr % 0x8
                return self._nes.ppu.read_register(0x2000 + offset)
            # Unmirrored I/O registers
            elif 0x4000 <= addr < 0x4020:
                self.memory[addr] = value
            # Expansion ROM cannot be written to
            elif 0x4020 <= addr < 0x6000:
                raise Exception("Cannot write to Expansion ROM at address {:#06x}!".format(addr))
            # Save RAM
            elif 0x6000 <= addr < 0x8000:
                self.memory[addr] = value
            # Cartridge ROM
            elif 0x8000 <= addr < 0x10000:
                raise Exception("Cannot write to ROM at address {:#06x}!".format(addr))


    class Register:
        def __init__(self, typ):
            self._typ = typ
            self._value = 0xff

        def read(self):
            return self._typ(self._value)

        def write(self, value):
            self._value = self._typ(value)

        def assign_bit(self, bit_number, set_it):
            if set_it:
                self._value |= 0x1 << bit_number
            else:
                self._value &= ~(0x1 << bit_number)

        def adjust(self, value=1):
            self._value = self._typ(self._value + value)


    class Instruction:
        def __init__(self, cpu, instruction, addr_mode, cycles):
            self._cpu = cpu
            self._instruction = instruction
            self._addressing = addr_mode
            self._cycles = cycles

        def __call__(self, memory):
            # get the operands from memory:
            ops = [0, 0]
            for i in range(self._addressing.size):
                if i == 0: continue # skip over opcode to get operands
                ops[i-1] = mem[i]

            extra_cycles = self._instruction(self._cpu, self._addressing, ops[0], ops[1])

            #pc = self._cpu.registers['pc'].read()
            #self._cpu.registers['pc'].write(pc + self._addressing.byte_size)

            return self._cycles + extra_cycles


    ####
    def __init__(self, nes):
        self._nes = nes
        self.memory = CPU.Memory(nes)
        self.cycles = 0

        # Create the CPU registers
        self.registers = {'pc': CPU.Register(np.uint16), 'sp': CPU.Register(np.uint8),
                          'a': CPU.Register(np.uint8), 'x': CPU.Register(np.uint8),
                          'y': CPU.Register(np.uint8), 'p': CPU.Register(np.uint8)}

        # Bit positions in the status register
        self.status = {'carry': 0, 'zero': 1, 'interrupt': 2, 'decimal': 3,
                       'break': 4, 'overflow': 6, 'negative': 7}

        self.opcodes = {
            0x00: CPU.Instruction(self, instructions.BRK, AddressingMode.Implied, 7),
            0x01: CPU.Instruction(self, instructions.ORA, AddressingMode.Indirect_X, 6),
            0x05: CPU.Instruction(self, instructions.ORA, AddressingMode.Zero_Page, 3),
            0x06: CPU.Instruction(self, instructions.ASL, AddressingMode.Zero_Page, 5),
            0x08: CPU.Instruction(self, instructions.PHP, AddressingMode.Implied, 3),
            0x09: CPU.Instruction(self, instructions.ORA, AddressingMode.Immediate, 2),
            0x0a: CPU.Instruction(self, instructions.ASL, AddressingMode.Accumulator, 2),
            0x0d: CPU.Instruction(self, instructions.ORA, AddressingMode.Absolute, 4),
            0x0e: CPU.Instruction(self, instructions.ASL, AddressingMode.Absolute, 6),

            0x10: CPU.Instruction(self, instructions.BPL, AddressingMode.Relative, 2),
            0x11: CPU.Instruction(self, instructions.ORA, AddressingMode.Indirect_Y, 5),
            0x15: CPU.Instruction(self, instructions.ORA, AddressingMode.Zero_Page_X, 4),
            0x16: CPU.Instruction(self, instructions.ASL, AddressingMode.Zero_Page_X, 6),
            0x18: CPU.Instruction(self, instructions.CLC, AddressingMode.Implied, 2),
            0x19: CPU.Instruction(self, instructions.ORA, AddressingMode.Absolute_Y, 4),
            0x1d: CPU.Instruction(self, instructions.ORA, AddressingMode.Absolute_X, 4),
            0x1e: CPU.Instruction(self, instructions.ASL, AddressingMode.Absolute_X, 7),

            0x20: CPU.Instruction(self, instructions.JSR, AddressingMode.Absolute, 6),
            0x21: CPU.Instruction(self, instructions.AND, AddressingMode.Indirect_X, 6),
            0x24: CPU.Instruction(self, instructions.BIT, AddressingMode.Zero_Page, 3),
            0x25: CPU.Instruction(self, instructions.AND, AddressingMode.Zero_Page, 3),
            0x26: CPU.Instruction(self, instructions.ROL, AddressingMode.Zero_Page, 5),
            0x28: CPU.Instruction(self, instructions.PLP, AddressingMode.Implied, 4),
            0x29: CPU.Instruction(self, instructions.AND, AddressingMode.Immediate, 2),
            0x2a: CPU.Instruction(self, instructions.ROL, AddressingMode.Accumulator, 2),
            0x2c: CPU.Instruction(self, instructions.BIT, AddressingMode.Absolute, 4),
            0x2d: CPU.Instruction(self, instructions.AND, AddressingMode.Absolute, 4),
            0x2e: CPU.Instruction(self, instructions.ROL, AddressingMode.Absolute, 6),

            0x30: CPU.Instruction(self, instructions.BMI, AddressingMode.Relative, 2),
            0x31: CPU.Instruction(self, instructions.AND, AddressingMode.Indirect_Y, 5),
            0x35: CPU.Instruction(self, instructions.AND, AddressingMode.Zero_Page_X, 4),
            0x36: CPU.Instruction(self, instructions.ROL, AddressingMode.Zero_Page_X, 6),
            0x38: CPU.Instruction(self, instructions.SEC, AddressingMode.Implied, 2),
            0x39: CPU.Instruction(self, instructions.AND, AddressingMode.Absolute_Y, 4),
            0x3d: CPU.Instruction(self, instructions.AND, AddressingMode.Absolute_X, 4),
            0x3e: CPU.Instruction(self, instructions.ROL, AddressingMode.Absolute_X, 7),

            0x40: CPU.Instruction(self, instructions.RTI, AddressingMode.Implied, 6),
            0x41: CPU.Instruction(self, instructions.EOR, AddressingMode.Indirect_X, 6),
            0x45: CPU.Instruction(self, instructions.EOR, AddressingMode.Zero_Page, 3),
            0x46: CPU.Instruction(self, instructions.LSR, AddressingMode.Zero_Page, 5),
            0x48: CPU.Instruction(self, instructions.PHA, AddressingMode.Implied, 3),
            0x49: CPU.Instruction(self, instructions.EOR, AddressingMode.Immediate, 2),
            0x4a: CPU.Instruction(self, instructions.LSR, AddressingMode.Accumulator, 2),
            0x4c: CPU.Instruction(self, instructions.JMP, AddressingMode.Absolute, 3),
            0x4d: CPU.Instruction(self, instructions.EOR, AddressingMode.Absolute, 4),
            0x4e: CPU.Instruction(self, instructions.LSR, AddressingMode.Absolute, 6),

            0x50: CPU.Instruction(self, instructions.BVC, AddressingMode.Relative, 2),
            0x51: CPU.Instruction(self, instructions.EOR, AddressingMode.Indirect_Y, 5),
            0x55: CPU.Instruction(self, instructions.EOR, AddressingMode.Zero_Page_X, 4),
            0x56: CPU.Instruction(self, instructions.LSR, AddressingMode.Zero_Page_X, 6),
            0x58: CPU.Instruction(self, instructions.CLI, AddressingMode.Implied, 2),
            0x59: CPU.Instruction(self, instructions.EOR, AddressingMode.Absolute_Y, 4),
            0x5d: CPU.Instruction(self, instructions.EOR, AddressingMode.Absolute_X, 4),
            0x5e: CPU.Instruction(self, instructions.LSR, AddressingMode.Absolute_X, 7),

            0x60: CPU.Instruction(self, instructions.RTS, AddressingMode.Implied, 6),
            0x61: CPU.Instruction(self, instructions.ADC, AddressingMode.Indirect_X, 6),
            0x65: CPU.Instruction(self, instructions.ADC, AddressingMode.Zero_Page, 3),
            0x66: CPU.Instruction(self, instructions.ROR, AddressingMode.Zero_Page, 5),
            0x68: CPU.Instruction(self, instructions.PLA, AddressingMode.Implied, 4),
            0x69: CPU.Instruction(self, instructions.ADC, AddressingMode.Immediate, 2),
            0x6a: CPU.Instruction(self, instructions.ROR, AddressingMode.Accumulator, 2),
            0x6c: CPU.Instruction(self, instructions.JMP, AddressingMode.Indirect, 5),
            0x6d: CPU.Instruction(self, instructions.ADC, AddressingMode.Absolute, 4),
            0x6e: CPU.Instruction(self, instructions.ROR, AddressingMode.Absolute, 6),

            0x70: CPU.Instruction(self, instructions.BVS, AddressingMode.Relative, 2),
            0x71: CPU.Instruction(self, instructions.ADC, AddressingMode.Indirect_Y, 5),
            0x75: CPU.Instruction(self, instructions.ADC, AddressingMode.Zero_Page_X, 4),
            0x76: CPU.Instruction(self, instructions.ROR, AddressingMode.Zero_Page_X, 6),
            0x78: CPU.Instruction(self, instructions.SEI, AddressingMode.Implied, 2),
            0x79: CPU.Instruction(self, instructions.ADC, AddressingMode.Absolute_Y, 4),
            0x7d: CPU.Instruction(self, instructions.ADC, AddressingMode.Absolute_X, 4),
            0x7e: CPU.Instruction(self, instructions.ROR, AddressingMode.Absolute_X, 7),

            0x81: CPU.Instruction(self, instructions.STA, AddressingMode.Indirect_X, 6),
            0x84: CPU.Instruction(self, instructions.STY, AddressingMode.Zero_Page, 3),
            0x85: CPU.Instruction(self, instructions.STA, AddressingMode.Zero_Page, 3),
            0x86: CPU.Instruction(self, instructions.STX, AddressingMode.Zero_Page, 3),
            0x88: CPU.Instruction(self, instructions.DEY, AddressingMode.Implied, 2),
            0x8a: CPU.Instruction(self, instructions.TXA, AddressingMode.Implied, 2),
            0x8c: CPU.Instruction(self, instructions.STY, AddressingMode.Absolute, 4),
            0x8d: CPU.Instruction(self, instructions.STA, AddressingMode.Absolute, 4),
            0x8e: CPU.Instruction(self, instructions.STX, AddressingMode.Absolute, 4),

            0x90: CPU.Instruction(self, instructions.BCC, AddressingMode.Relative, 2),
            0x91: CPU.Instruction(self, instructions.STA, AddressingMode.Indirect_Y, 6),
            0x94: CPU.Instruction(self, instructions.STY, AddressingMode.Zero_Page_X, 4),
            0x95: CPU.Instruction(self, instructions.STA, AddressingMode.Zero_Page_X, 4),
            0x96: CPU.Instruction(self, instructions.STX, AddressingMode.Zero_Page_Y, 4),
            0x98: CPU.Instruction(self, instructions.TYA, AddressingMode.Implied, 2),
            0x99: CPU.Instruction(self, instructions.STA, AddressingMode.Absolute_Y, 5),
            0x9a: CPU.Instruction(self, instructions.TXS, AddressingMode.Implied, 2),
            0x9d: CPU.Instruction(self, instructions.STA, AddressingMode.Absolute_X, 5),

            0xa0: CPU.Instruction(self, instructions.LDY, AddressingMode.Immediate, 2),
            0xa1: CPU.Instruction(self, instructions.LDA, AddressingMode.Indirect_X, 6),
            0xa2: CPU.Instruction(self, instructions.LDX, AddressingMode.Immediate, 2),
            0xa4: CPU.Instruction(self, instructions.LDY, AddressingMode.Zero_Page, 3),
            0xa5: CPU.Instruction(self, instructions.LDA, AddressingMode.Zero_Page, 3),
            0xa6: CPU.Instruction(self, instructions.LDX, AddressingMode.Zero_Page, 3),
            0xa8: CPU.Instruction(self, instructions.TAY, AddressingMode.Implied, 2),
            0xa9: CPU.Instruction(self, instructions.LDA, AddressingMode.Immediate, 2),
            0xaa: CPU.Instruction(self, instructions.TAX, AddressingMode.Implied, 2),
            0xad: CPU.Instruction(self, instructions.LDA, AddressingMode.Absolute, 4),
            0xac: CPU.Instruction(self, instructions.LDY, AddressingMode.Absolute, 4),
            0xae: CPU.Instruction(self, instructions.LDX, AddressingMode.Absolute, 4),

            0xb0: CPU.Instruction(self, instructions.BCS, AddressingMode.Relative, 2),
            0xb1: CPU.Instruction(self, instructions.LDA, AddressingMode.Indirect_Y, 5),
            0xb4: CPU.Instruction(self, instructions.LDY, AddressingMode.Zero_Page_X, 4),
            0xb5: CPU.Instruction(self, instructions.LDA, AddressingMode.Zero_Page_X, 4),
            0xb6: CPU.Instruction(self, instructions.LDX, AddressingMode.Zero_Page_Y, 4),
            0xb8: CPU.Instruction(self, instructions.CLV, AddressingMode.Implied, 2),
            0xb9: CPU.Instruction(self, instructions.LDA, AddressingMode.Absolute_Y, 4),
            0xba: CPU.Instruction(self, instructions.TSX, AddressingMode.Implied, 2),
            0xbc: CPU.Instruction(self, instructions.LDY, AddressingMode.Absolute_X, 4),
            0xbd: CPU.Instruction(self, instructions.LDA, AddressingMode.Absolute_X, 4),
            0xbe: CPU.Instruction(self, instructions.LDX, AddressingMode.Absolute_Y, 4),

            0xc0: CPU.Instruction(self, instructions.CPY, AddressingMode.Immediate, 2),
            0xc1: CPU.Instruction(self, instructions.CMP, AddressingMode.Indirect_X, 6),
            0xc4: CPU.Instruction(self, instructions.CPY, AddressingMode.Zero_Page, 3),
            0xc5: CPU.Instruction(self, instructions.CMP, AddressingMode.Zero_Page, 3),
            0xc6: CPU.Instruction(self, instructions.DEC, AddressingMode.Zero_Page, 5),
            0xc8: CPU.Instruction(self, instructions.INY, AddressingMode.Implied, 2),
            0xc9: CPU.Instruction(self, instructions.CMP, AddressingMode.Immediate, 2),
            0xca: CPU.Instruction(self, instructions.DEX, AddressingMode.Implied, 2),
            0xcc: CPU.Instruction(self, instructions.CPY, AddressingMode.Absolute, 4),
            0xcd: CPU.Instruction(self, instructions.CMP, AddressingMode.Absolute, 4),
            0xce: CPU.Instruction(self, instructions.DEC, AddressingMode.Absolute, 6),

            0xd0: CPU.Instruction(self, instructions.BNE, AddressingMode.Relative, 2),
            0xd1: CPU.Instruction(self, instructions.CMP, AddressingMode.Indirect_Y, 5),
            0xd5: CPU.Instruction(self, instructions.CMP, AddressingMode.Zero_Page_X, 4),
            0xd6: CPU.Instruction(self, instructions.DEC, AddressingMode.Zero_Page_X, 6),
            0xd8: CPU.Instruction(self, instructions.CLD, AddressingMode.Implied, 2),
            0xd9: CPU.Instruction(self, instructions.CMP, AddressingMode.Absolute_Y, 4),
            0xdd: CPU.Instruction(self, instructions.CMP, AddressingMode.Absolute_X, 4),
            0xde: CPU.Instruction(self, instructions.DEC, AddressingMode.Absolute_X, 7),

            0xe0: CPU.Instruction(self, instructions.CPX, AddressingMode.Immediate, 2),
            0xe1: CPU.Instruction(self, instructions.SBC, AddressingMode.Indirect_X, 6),
            0xe4: CPU.Instruction(self, instructions.CPX, AddressingMode.Zero_Page, 3),
            0xe5: CPU.Instruction(self, instructions.SBC, AddressingMode.Zero_Page, 3),
            0xe6: CPU.Instruction(self, instructions.INC, AddressingMode.Zero_Page, 5),
            0xe8: CPU.Instruction(self, instructions.INX, AddressingMode.Implied, 2),
            0xe9: CPU.Instruction(self, instructions.SBC, AddressingMode.Immediate, 2),
            0xea: CPU.Instruction(self, instructions.NOP, AddressingMode.Implied, 2),
            0xec: CPU.Instruction(self, instructions.CPX, AddressingMode.Absolute, 4),
            0xed: CPU.Instruction(self, instructions.SBC, AddressingMode.Absolute, 4),
            0xee: CPU.Instruction(self, instructions.INC, AddressingMode.Absolute, 6),

            0xf0: CPU.Instruction(self, instructions.BEQ, AddressingMode.Relative, 2),
            0xf1: CPU.Instruction(self, instructions.SBC, AddressingMode.Indirect_Y, 5),
            0xf5: CPU.Instruction(self, instructions.SBC, AddressingMode.Zero_Page_X, 4),
            0xf6: CPU.Instruction(self, instructions.INC, AddressingMode.Zero_Page_X, 6),
            0xf8: CPU.Instruction(self, instructions.SED, AddressingMode.Implied, 2),
            0xfd: CPU.Instruction(self, instructions.SBC, AddressingMode.Absolute_X, 4),
            0xfe: CPU.Instruction(self, instructions.INC, AddressingMode.Absolute_X, 7)
        }

    # status methods
    def get_status(self, flag):
        pos = self.status[flag]
        return (self.registers['p'].read() >> pos) & 0x1

    def set_status(self, flag, value):
        self.registers['p'].assign_bit(self.status[flag], value)

    # Stack methods
    def push_stack(self, value):
        self.registers['sp'].adjust(-1)
        self.memory.write(0x100 + self.registers['sp'].read(), value)

    def pop_stack(self):
        result = self.memory.read(self.registers['sp'].read())
        self.registers['sp'].adjust()
        return result

    def step(self):
        pass
