'''
The entry point for the emulator
'''
from cpu import cpu
import ppu
import cartridge


class NES(object):
    def __init__(self, rom=None):
        if rom:
            self.ppu = ppu.PPU(self)
            self.rom = cartridge.Cartridge(self, rom)
            self.cpu = cpu.CPU(self, self.rom)
            self.halt_cpu = 0

            self.power_up()
        else:
            self.rom = None
            self.cpu = cpu.CPU(self, self.rom)
            self.ppu = ppu.PPU(self)
            self.halt_cpu = 0

    def power_up(self):
        self.cpu.set_reset_vector()

    def save_state(self):
        pass

    def load_state(self):
        pass

    def step(self):
        if not self.halt_cpu:
            cycles = self.cpu.execute()
        else:
            cycles = 1
            self.halt_cpu -= 1

        for i in range(3):# * cycles):
            self.ppu.step()

    def load_rom(self, rom_data):
        self.rom = cartridge.Cartridge(self, rom_data)
        # self.cpu.set_reset_vector()

    def parse_input(self, button):
        print "parsed!"
