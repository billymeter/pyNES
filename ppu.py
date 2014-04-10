'''
Picture Processing Unit
'''


class PPU:
    __init__(self, nes):
        # ppu power up state can be found here:
        # http://wiki.nesdev.com/w/index.php/PPU_power_up_state

        # registers
        PPUCTRL = 0x0
        PPUMASK = 0x0
        PPUSTATUS = 0x0
        OAMADDR = 0x0
        OAMDATA = 0x0
        PPUSCROLL = 0x0
        PPUADDR = 0x0
        PPUDATA = 0x0
