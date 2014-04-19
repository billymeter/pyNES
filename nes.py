'''
The entry point for the emulator
'''
import cpu
import ppu
import cartridge


class NES(object):
    # NES memory bank goes from 0x0 to 0xFFFF
    self.memory = bytearray(0x10000)
    self.cpu = cpu.CPU(self)
    self.ppu = ppu.PPU(self)
    self.rom = None

    def save_state(self):
        pass

    def load_state(self):
        pass

    def step(self):
        cycles = self.cpu.step()

        for i in range(3 * cycles):
            self.ppu.step()

    def load_rom(self, rom_data):
        self.rom = cartridge.Cartridge(rom_data)
