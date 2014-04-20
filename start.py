import nes

emulator = nes.NES()

with open("roms/nestest.nes", 'rb') as rom:
    emulator.load_rom(rom.read())

while True:
    emulator.cpu.run()