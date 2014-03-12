'''
The entry point for the emulator
'''


import cpu
import ppu

class NES:
    # NES memory bank goes from 0x0 to 0xFFFF
    memory = bytearray(0x10000)