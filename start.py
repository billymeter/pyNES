import nes

with open("roms/nestest.nes", 'rb') as rom:
    emulator = nes.NES(rom.read())
    emulator.cpu.registers['pc'].write(0xc000)

while True:
    emulator.cpu.run()
