'''
The entry point for the emulator
'''
import logging
from cpu import cpu
import ppu
import cartridge

logging.basicConfig(filename='nes.log', level=logging.ERROR)
logger = logging.getLogger(__name__)


class NES(object):
    def __init__(self):
        self.rom = None
        self.cpu = cpu.CPU(self, self.rom)
        self.ppu = ppu.PPU(self)

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
