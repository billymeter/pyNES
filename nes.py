'''
The entry point for the emulator
'''
from cpu import cpu
import ppu
import cartridge
import apu


class NES(object):
    def __init__(self):
        self.rom = None
        self.cpu = cpu.CPU(self, self.rom)
        self.ppu = ppu.PPU(self)
        self.apu = apu.APU(self)


    def save_state(self):
        pass

    def load_state(self):
        pass

    def step(self):
        cycles = self.cpu.execute()

        for i in range(3 * cycles):
            self.ppu.step()

    def load_rom(self, rom_data):
        self.rom = cartridge.Cartridge(self, rom_data)

    def parse_input(self, button):
        print "parsed!"
