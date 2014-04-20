'''
The entry point for the emulator
'''
from cpu import cpu
import ppu
import cartridge


class NES(object):
    def __init__(self):
        self.cpu = cpu.CPU(self)
        self.ppu = ppu.PPU(self)
        self.rom = None

    def save_state(self):
        pass

    def load_state(self):
        pass

    def step(self):
        # cycles = self.cpu.step()

        # for i in range(3 * cycles):
        for i in range(3):
            self.ppu.step()

    def load_rom(self, rom_data):
        self.rom = cartridge.Cartridge(self, rom_data)
