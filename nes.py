'''
The entry point for the emulator
'''


import cpu
import ppu

class NES:
    # NES memory bank goes from 0x0 to 0xFFFF
    memory = bytearray(0x10000)
    # program counter
    pc = 0x0
    # stack pointer
    sp = 0x10
    # flag register
    p = 0x0

    # general purpose registers
    a = 0x0
    x = 0x0
    y = 0x0