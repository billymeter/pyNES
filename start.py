import nes

with open("roms/rom_singles/1-cli_latency.nes", 'rb') as rom:
    emulator = nes.NES(rom.read())
    #emulator.cpu.registers['pc'].write(0xc000)

while True:
    emulator.cpu.execute(True)
