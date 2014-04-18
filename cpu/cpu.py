'''
NES CPU: Ricoh 2A05
'''

import numpy as np
from cpu import instructions
from cpu.addressmodes import *

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
                base_addr = addr % 0x800
                return self.memory[base_addr]
            # I/O Registers, mirrored a bunch of times
            elif 0x2000 <= addr < 0x4000:
                base_addr = (addr - 0x2000) % 0x8
                return self.memory[base_addr + 0x2000]
            # Unmirrored I/O registers, Expansion ROM, and Save RAM
            elif 0x4000 <= addr < 0x8000:
                return self.memory[addr]
            # Cartridge ROM
            elif 0x8000 <= addr < 0x10000:
                # return the cartridge ROM value

        def write(self, addr, value):
            if addr < 0x0 or addr > 0xffff:
                raise Exception("Out of memory bounds write at {:#06x}".format(addr))
            # The Zero Page, Stack, and RAM mirrored 4 times, we will only
            # use one copy rather than mirroring them all since we have a
            # mod operator
            elif 0x0 <= addr < 0x2000:
                base_addr = addr % 0x800
                self.memory[base_addr] = value
            # I/O Registers, mirrored a bunch of times
            elif 0x2000 <= addr < 0x4000:
                base_addr = (addr - 0x2000) % 0x8
                self.memory[base_addr + 0x2000] = value
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

            return self._cycles + extra_cycles


    ####
    def __init__(self, nes):
        self._nes = nes
        self.memory = CPU.Memory(nes)

        # Create the CPU registers
        self.registers = {'pc': CPU.Register(np.uint16), 'sp': CPU.Register(np.uint8),
                          'a': CPU.Register(np.uint8), 'x': CPU.Register(np.uint8),
                          'y': CPU.Register(np.uint8), 'p': CPU.Register(np.uint8)}

        # Bit positions in the status register
        self.status = {'carry': 0, 'zero': 1, 'interrupt': 2, 'decimal': 3,
                       'break': 4, 'overflow': 6, 'negative': 7}

        self.opcodes = {
            
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
