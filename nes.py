'''
The entry point for the emulator
'''


import cpu
import ppu


class NES(object):
    # NES memory bank goes from 0x0 to 0xFFFF
    memory = bytearray(0x10000)
    self.cpu = CPU(self)
    self.ppu = PPU(self)
