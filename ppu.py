'''
Picture Processing Unit
'''
from collections import namedtuple
from utils import *
import logging
import numpy as np

logging.basicConfig(filename='errors.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

f = open("ppu.log", 'w')
pal = open('palette.txt', 'a')

''' Constants '''
MirrorType = enum('Horizontal', 'Vertical', 'SingleUpper', 'SingleLower')
# PatternTablePos = (0x0000, 0x1000)
PATTERN_TABLE_SIZE = 0x1000
# AttrTablePos = (0x23c0, 0x27c0, 0x2bc0, 0x2fc0)
# ATTR_TABLE_SIZE = 0x40
# NameTablePos = (0x2000, 0x2400, 0x2800, 0x2c00)
# NTMirrorPos = (0x3000, 0x3400, 0x3800, 0x3c00)
NAMETABLE_SIZE = 0x400
# PaletteRamPos = 0x3f00
# PALLETE_RAM_SIZE = 0x20
# status register
StatusBit = enum(SpriteOverflow=5, Sprite0Hit=6, InVblank=7)

rgb_palette = [
    0x666666, 0x002A88, 0x1412A7, 0x3B00A4, 0x5C007E,
    0x6E0040, 0x6C0600, 0x561D00, 0x333500, 0x0B4800,
    0x005200, 0x004F08, 0x00404D, 0x000000, 0x000000,
    0x000000, 0xADADAD, 0x155FD9, 0x4240FF, 0x7527FE,
    0xA01ACC, 0xB71E7B, 0xB53120, 0x994E00, 0x6B6D00,
    0x388700, 0x0C9300, 0x008F32, 0x007C8D, 0x000000,
    0x000000, 0x000000, 0xFFFEFF, 0x64B0FF, 0x9290FF,
    0xC676FF, 0xF36AFF, 0xFE6ECC, 0xFE8170, 0xEA9E22,
    0xBCBE00, 0x88D800, 0x5CE430, 0x45E082, 0x48CDDE,
    0x4F4F4F, 0x000000, 0x000000, 0xFFFEFF, 0xC0DFFF,
    0xD3D2FF, 0xE8C8FF, 0xFBC2FF, 0xFEC4EA, 0xFECCC5,
    0xF7D8A5, 0xE4E594, 0xCFEF96, 0xBDF4AB, 0xB3F3CC,
    0xB5EBF2, 0xB8B8B8, 0x000000, 0x000000,
]
               # [(0x1D << 2, 0x1D << 2, 0x1D << 2),
               # (0x09 << 2, 0x06 << 2, 0x23 << 2),
               # (0x00 << 2, 0x00 << 2, 0x2A << 2),
               # (0x11 << 2, 0x00 << 2, 0x27 << 2),
               # (0x23 << 2, 0x00 << 2, 0x1D << 2),
               # (0x2A << 2, 0x00 << 2, 0x04 << 2),
               # (0x29 << 2, 0x00 << 2, 0x00 << 2),
               # (0x1F << 2, 0x02 << 2, 0x00 << 2),
               # (0x10 << 2, 0x0B << 2, 0x00 << 2),
               # (0x00 << 2, 0x11 << 2, 0x00 << 2),
               # (0x00 << 2, 0x14 << 2, 0x00 << 2),
               # (0x00 << 2, 0x0F << 2, 0x05 << 2),
               # (0x06 << 2, 0x0F << 2, 0x17 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x2F << 2, 0x2F << 2, 0x2F << 2),
               # (0x00 << 2, 0x1C << 2, 0x3B << 2),
               # (0x08 << 2, 0x0E << 2, 0x3B << 2),
               # (0x20 << 2, 0x00 << 2, 0x3C << 2),
               # (0x2F << 2, 0x00 << 2, 0x2F << 2),
               # (0x39 << 2, 0x00 << 2, 0x16 << 2),
               # (0x36 << 2, 0x0A << 2, 0x00 << 2),
               # (0x32 << 2, 0x13 << 2, 0x03 << 2),
               # (0x22 << 2, 0x1C << 2, 0x00 << 2),
               # (0x00 << 2, 0x25 << 2, 0x00 << 2),
               # (0x00 << 2, 0x2A << 2, 0x00 << 2),
               # (0x00 << 2, 0x24 << 2, 0x0E << 2),
               # (0x00 << 2, 0x20 << 2, 0x22 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x3F << 2, 0x3F << 2, 0x3F << 2),
               # (0x0F << 2, 0x2F << 2, 0x3F << 2),
               # (0x17 << 2, 0x25 << 2, 0x3F << 2),
               # (0x33 << 2, 0x22 << 2, 0x3F << 2),
               # (0x3D << 2, 0x1E << 2, 0x3F << 2),
               # (0x3F << 2, 0x1D << 2, 0x2D << 2),
               # (0x3F << 2, 0x1D << 2, 0x18 << 2),
               # (0x3F << 2, 0x26 << 2, 0x0E << 2),
               # (0x3C << 2, 0x2F << 2, 0x0F << 2),
               # (0x20 << 2, 0x34 << 2, 0x04 << 2),
               # (0x13 << 2, 0x37 << 2, 0x12 << 2),
               # (0x16 << 2, 0x3E << 2, 0x26 << 2),
               # (0x00 << 2, 0x3A << 2, 0x36 << 2),
               # (0x1E << 2, 0x1E << 2, 0x1E << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x3F << 2, 0x3F << 2, 0x3F << 2),
               # (0x2A << 2, 0x39 << 2, 0x3F << 2),
               # (0x31 << 2, 0x35 << 2, 0x3F << 2),
               # (0x35 << 2, 0x32 << 2, 0x3F << 2),
               # (0x3F << 2, 0x31 << 2, 0x3F << 2),
               # (0x3F << 2, 0x31 << 2, 0x36 << 2),
               # (0x3F << 2, 0x2F << 2, 0x2C << 2),
               # (0x3F << 2, 0x36 << 2, 0x2A << 2),
               # (0x3F << 2, 0x39 << 2, 0x28 << 2),
               # (0x38 << 2, 0x3F << 2, 0x28 << 2),
               # (0x2A << 2, 0x3C << 2, 0x2F << 2),
               # (0x2C << 2, 0x3F << 2, 0x33 << 2),
               # (0x27 << 2, 0x3F << 2, 0x3C << 2),
               # (0x31 << 2, 0x31 << 2, 0x31 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2),
               # (0x00 << 2, 0x00 << 2, 0x00 << 2)]


class PPU(object):
    class Memory(object):
        class NameTable(object):
            def __init__(self):
                self.nametables = [[], [], [], []]
                self.attrtables = [[], [], [], []]
                self._nametables = [bytearray(0x3c0), bytearray(0x3c0)]
                self._attrtables = [bytearray(0x40), bytearray(0x40)]
                self._mirroring = None

            def read(self, addr):
                if 0x2000 <= addr < 0x23c0:
                    return self.nametables[0][addr - 0x2000]
                elif addr < 0x2400:
                    return self.attrtables[0][addr - 0x23c0]
                elif addr < 0x27c0:
                    return self.nametables[1][addr - 0x2400]
                elif addr < 0x2800:
                    return self.attrtables[1][addr - 0x27c0]
                elif addr < 0x2bc0:
                    return self.nametables[2][addr - 0x2800]
                elif addr < 0x2c00:
                    return self.attrtables[2][addr - 0x2bc0]
                elif addr < 0x2fc0:
                    return self.nametables[3][addr - 0x2c00]
                elif addr < 0x3000:
                    return self.attrtables[3][addr - 0x2fc0]
                else:
                    return self.read(addr - 0x1000)

            def write(self, addr, value):
                if 0x2000 <= addr < 0x23c0:
                    self.nametables[0][addr - 0x2000] = value
                elif addr < 0x2400:
                    self.attrtables[0][addr - 0x23c0] = value
                elif addr < 0x27c0:
                    self.nametables[1][addr - 0x2400] = value
                elif addr < 0x2800:
                    self.attrtables[1][addr - 0x27c0] = value
                elif addr < 0x2bc0:
                    self.nametables[2][addr - 0x2800] = value
                elif addr < 0x2c00:
                    self.attrtables[2][addr - 0x2bc0] = value
                elif addr < 0x2fc0:
                    self.nametables[3][addr - 0x2c00] = value
                elif addr < 0x3000:
                    self.attrtables[3][addr - 0x2fc0] = value

            def nt_byte(self, nametable, x, y):
                x /= 8
                y /= 8
                return self.nametables[nametable][y * 32 + x]

            def at_byte(self, nametable, x, y):
                x /= 32
                y /= 30
                return self.attrtables[nametable][y * 8 + x]

            def set_mirroring(self, mirroring):
                """ 'Horizontal', 'Vertical', 'SingleUpper', or 'SingleLower' """
                self.mirroring = mirroring
                if mirroring == 'Horizontal':
                    for (i, j) in zip(range(4), [0, 0, 1, 1]):
                        self.nametables[i] = self._nametables[j]
                        self.attrtables[i] = self._attrtables[j]
                elif mirroring == 'Vertical':
                    for (i, j) in zip(range(4), [0, 1, 0, 1]):
                        self.nametables[i] = self._nametables[j]
                        self.attrtables[i] = self._attrtables[j]
                elif mirroring == 'SingleUpper':
                    for (i, j) in zip(range(4), [0, 0, 0, 0]):
                        self.nametables[i] = self._nametables[j]
                        self.attrtables[i] = self._attrtables[j]
                elif mirroring == 'SingleLower':
                    for (i, j) in zip(range(4), [1, 1, 1, 1]):
                        self.nametables[i] = self._nametables[j]
                        self.attrtables[i] = self._attrtables[j]

        class PaletteTable(object):
            def __init__(self):
                self._memory = bytearray(0x20)

            def read(self, addr):
                if 0x3f00 <= addr < 0x3f20:
                    return self._memory[addr - 0x3f00]
                elif 0x3f20 <= addr < 0x3f40:
                    return self.read(addr - 0x20)
                elif 0x3f40 <= addr < 0x3f60:
                    return self.read(addr - 0x40)
                elif 0x3f60 <= addr < 0x3f80:
                    return self.read(addr - 0x60)
                elif 0x3f80 <= addr < 0x3fa0:
                    return self.read(addr - 0x80)
                elif 0x3fa0 <= addr < 0x3fc0:
                    return self.read(addr - 0xa0)
                elif 0x3fc0 <= addr < 0x3fe0:
                    return self.read(addr - 0xc0)
                elif 0x3fe0 <= addr < 0x4000:
                    return self.read(addr - 0xe0)

            def write(self, addr, value):
                if 0x3f00 <= addr < 0x3f20:
                    if addr == 0x3F00 or addr == 0x3F10:
                        self._memory[0x00] = value
                        self._memory[0x10] = value
                    elif addr == 0x3F04 or addr == 0x3F14:
                        self._memory[0x04] = value
                        self._memory[0x14] = value
                    elif addr == 0x3F08 or addr == 0x3F18:
                        self._memory[0x08] = value
                        self._memory[0x18] = value
                    elif addr == 0x3F0C or addr == 0x3F1C:
                        self._memory[0x0C] = value
                        self._memory[0x1C] = value
                    else:
                        self._memory[addr - 0x3f00] = value
                elif 0x3f20 <= addr < 0x3f40:
                    self.write(addr - 0x20, value)
                elif 0x3f40 <= addr < 0x3f60:
                    self.write(addr - 0x40, value)
                elif 0x3f60 <= addr < 0x3f80:
                    self.write(addr - 0x60, value)
                elif 0x3f80 <= addr < 0x3fa0:
                    self.write(addr - 0x80, value)
                elif 0x3fa0 <= addr < 0x3fc0:
                    self.write(addr - 0xa0, value)
                elif 0x3fc0 <= addr < 0x3fe0:
                    self.write(addr - 0xc0, value)
                elif 0x3fe0 <= addr < 0x4000:
                    self.write(addr - 0xe0, value)

        # Memory functions
        def __init__(self, nes):
            self._nes = nes
            self._memory = bytearray(0x8000)
            self.nametable = PPU.Memory.NameTable()
            self.palettetable = PPU.Memory.PaletteTable()

        def read(self, addr):
            if 0x0000 <= addr < 0x2000:
                return self._nes.rom.read_chr(addr)
            elif 0x2000 <= addr < 0x3f00:
                return self.nametable.read(addr)
            elif 0x3f00 <= addr < 0x4000:
                return self.palettetable.read(addr)
            else:
                return self.read(addr % 0x4000)

        def write(self, addr, value):
            self._memory[addr] = value
            if 0x0000 <= addr < 0x2000:
                self._nes.rom.write_chr(addr, value)
            elif 0x2000 <= addr < 0x3f00:
                self.nametable.write(addr, value)
            elif 0x3f00 <= addr < 0x4000:
                self.palettetable.write(addr, value)
            else:
                self.write(addr % 0x4000)

    class OAM(object):
        def __init__(self, nes):
            self._nes = nes
            self._memory = bytearray(0x100)

        def write(self, addr, value):
            self._memory[addr] = value

        def read(self, addr):
            return self._memory[addr]

        def get_sprite_data(self, addr):
            top_y = self._memory[addr]
            tile_index = self._memory[addr + 1]
            attributes = self._memory[addr + 2]
            left_x = self._memory[addr + 3]
            return (top_y, tile_index, attributes, left_x)

    def __init__(self, nes):
        self._nes = nes
        # ppu memory
        self.vram = PPU.Memory(nes)
        self.sram64 = PPU.OAM(nes)
        self.sram8 = PPU.OAM(nes)
        # render states
        self.sprite_data = {
            'y': [0] * 64,
            'tiles': [0] * 64,
            'attributes': [0] * 64,
            'x': [0] * 64
        }
        self.colors = [0] * 61440
        self.values = [0] * 61440
        self.pindexes = [0] * 61440
        self.frame_buffer = np.array([[0] * 240] * 256, ndmin=2, dtype=np.uint32)
        self.display = None

        ''' Flags (Reg 1) '''
        # Execute NMI on VBlank. 0=Disable, 1=Enable
        self.nmi_on_vblank = 0
        # Select PPU to be master/slave (unused?)
        self.master_slave = 0
        # 0 = 8x8, 1 = 8x16
        self.sprite_size = 0
        # 0 = $0000 (VRAM), 1 = $1000 (VRAM)
        self.background_tbl_addr = 0
        # 0 = $0000 (VRAM), 1 = $1000 (VRAM)
        self.sprite_tbl_addr = 0
        # 0 = Increment by 1, 1 = Increment by 32
        self.vram_addr_inc = 0
        # 0 = $2000, 1 = $2400, 2 = $2800, 3 = $2C00
        self.nametable_addr = 0

        ''' Mask Flags (Reg 2) '''
        # These flags give the background color if monochrome is on;
        # otherwise they signify color intensity. Black is default.
        self.more_red = 0
        self.more_green = 0
        self.more_blue = 0
        # Sprites: 0 = Not displayed, 1 = Displayed
        self.show_sprites = 0
        # Background: 0 = Not displayed, 1 = Displayed
        self.show_background = 0
        # 0 = Sprites invisible in left 8-pixel column, 1 = No clipping
        self.show_sprites_plus = 0
        # 0 = BG invisible in left 8-pixel column, 1 = No clipping
        self.show_background_plus = 0
        # Display type. 0=color, 1=monochrome
        self.monochrome = 0

        # registers
        self.control = 0
        self.mask = 0
        self.status = 0
        self.vram_data_buffer = 0
        self.vram_addr = 0
        self.vram_addr_buffer = 0
        self.sprite_ram_addr = 0
        self.vram_data = 0
        self.fine_x = 0
        self.vram_addr_latch = 0
        self.shift16_1 = 0
        self.shift16_2 = 0

        # other state
        self.frame_count = 0
        self.cycle = 0
        self.scanline = 241
        self.ignore_nmi = 0
        self.ignore_vblank = 1

        self.attr_loc = [0] * 0x400
        self.attr_shift = [0] * 0x400
        for i in range(0x400):
            self.attr_loc[i] = ((i >> 2) & 0x07) | (((i >> 4) & 0x38) | 0x3C0)
            self.attr_shift[i] = ((i >> 4) & 0x04) | (i & 0x02)

    def read_register(self, address):
        if address == 0x2002:
            return self.ppustatus_read()
        elif address == 0x2004:
            return self.oamdata_read()
        elif address == 0x2007:
            return self.ppudata_read()
        else:
            return 0

    def write_register(self, address, v):
        if address == 0x2000:
            self.ppuctrl_write(v)
        elif address == 0x2001:
            self.ppumask_write(v)
        elif address == 0x2003:
            self.oamaddr_write(v)
        elif address == 0x2004:
            self.oamdata_write(v)
        elif address == 0x2005:
            self.ppuscroll_write(v)
        elif address == 0x2006:
            self.ppuaddr_write(v)
        elif address == 0x2007:
            self.ppudata_write(v)
        elif address == 0x4014:
            self.dma_write(v)
        self.status |= v & 0x1f

    def ppuctrl_write(self, value):
        """ Handle a write to PPUCTRL ($2000) """
        '''
        7654 3210
        |||| ||||
        |||| ||++- Base nametable address
        |||| ||    (0 = $2000; 1 = $2400; 2 = $2800; 3 = $2C00)
        |||| |+--- VRAM address increment per CPU read/write of PPUDATA
        |||| |     (0: add 1, going across; 1: add 32, going down)
        |||| +---- Sprite pattern table address for 8x8 sprites
        ||||       (0: $0000; 1: $1000; ignored in 8x16 mode)
        |||+------ Background pattern table address (0: $0000; 1: $1000)
        ||+------- Sprite size (0: 8x8; 1: 8x16)
        |+-------- PPU master/slave select
        |          (0: read backdrop from EXT pins; 1:output color on EXT pins)
        +--------- Generate an NMI at the start of the
                   vertical blanking interval (0: off; 1: on)
        '''
        self.nametable_addr = value & 0x3
        self.vram_addr_inc = (value >> 2) & 0x1
        self.sprite_tbl_addr = (value >> 3) & 0x1
        self.background_tbl_addr = (value >> 4) & 0x1
        self.sprite_size = (value >> 5) & 0x1
        self.master_slave = (value >> 6) & 0x1
        self.nmi_on_vblank = (value >> 7) & 0x1

        # VRAM address buffer is also changed (affects scrolling)
        ''' vram_addr_buffer: ...BA.. ........ = value: ......BA '''
        self.vram_addr_buffer = (self.vram_addr_buffer & 0xf3ff) | (self.nametable_addr << 10)

    def ppumask_write(self, value):
        """ Handle a write to PPUMASK ($2001) """
        self.mask = value
        '''
        76543210
        ||||||||
        |||||||+- Grayscale (0: normal color; 1: produce a monochrome display)
        ||||||+-- 1: Show background in leftmost 8 pixels of screen; 0: Hide
        |||||+--- 1: Show sprites in leftmost 8 pixels of screen; 0: Hide
        ||||+---- 1: Show background
        |||+----- 1: Show sprites
        ||+------ Intensify reds (and darken other colors)
        |+------- Intensify greens (and darken other colors)
        +-------- Intensify blues (and darken other colors)
        '''
        self.monochrome = value & 0x1
        self.show_background_plus = (value >> 1) & 0x1
        self.show_sprites_plus = (value >> 2) & 0x1
        self.show_background = (value >> 3) & 0x1
        self.show_sprites = (value >> 4) & 0x1
        self.more_red = (value >> 5) & 0x1
        self.more_green = (value >> 6) & 0x1
        self.more_blue = (value >> 7) & 0x1

    def ppustatus_read(self):
        """ Handle a read to PPUSTATUS ($2002) """
        # vram address latch is cleared
        self.vram_addr_latch = 0

        '''
        7654 3210
        |||| ||||
        |||+-++++- Least significant bits previously written into a PPU register
        |||        (due to register not being updated for this address)
        ||+------- Sprite overflow. The intent was for this flag to be set
        ||         whenever more than eight sprites appear on a scanline, but a
        ||         hardware bug causes the actual behavior to be more complicated
        ||         and generate false positives as well as false negatives; see
        ||         PPU sprite evaluation. This flag is set during sprite
        ||         evaluation and cleared at dot 1 (the second dot) of the
        ||         pre-render line.
        |+-------- Sprite 0 Hit.  Set when a nonzero pixel of sprite 0 overlaps
        |          a nonzero background pixel; cleared at dot 1 of the pre-render
        |          line.  Used for raster timing.
        +--------- Vertical blank has started (0: not in VBLANK; 1: in VBLANK).
                   Set at dot 1 of line 241 (the line *after* the post-render
                   line); cleared after reading $2002 and at dot 1 of the
                   pre-render line.
        '''
        if self.scanline == 240 and self.cycle == 0:
            # reading one cycle before vblank results in:
            # ignore_nmi and ignore_vblank are set
            # return status with vblank cleared
            self.ignore_nmi = 1
            self.ignore_vblank = 1
            return clear_bit(self.status, StatusBit.InVblank)
        elif self.scanline == 240 and self.cycle == 2:
            # reading one cycle after vblank results in:
            # clear vblank, suppress NMI for the frame
            # return status with vblank set
            self.status = clear_bit(self.status, StatusBit.InVblank)
            self.ignore_nmi = 1
            return set_bit(self.status, StatusBit.InVblank)
        else:
            # otherwise normal behavior:
            # nmi, vblank aren't affected, status is returned then cleared
            self.ignore_nmi = 0
            self.ignore_vblank = 0
            tmp = self.status
            self.status = clear_bit(self.status, StatusBit.InVblank)
            return tmp

    def oamaddr_write(self, v):
        """ Handle a write to OAMADDR ($2003) """
        self.sprite_ram_addr = v

    def oamdata_write(self, v):
        """ Handle a write to OAMDATA ($2004) """
        self.sram64.write(self.sprite_ram_addr, v)
        self.update_sprite_buffer(self.sprite_ram_addr, v)
        self.sprite_ram_addr += 1
        self.sprite_ram_addr %= 0x100

    def oamdata_read(self):
        """ Handle a read to OAMDATA ($2004) """
        return self.sram64.read(self.sprite_ram_addr)

    def ppuscroll_write(self, v):
        """ Handle a write to PPUSCROLL ($2005) """
        '''
        First write (w = 0):
            vram_addr_buffer: ....... ...HGFED = value: HGFED...
            Fine x:                        CBA = value: .....CBA
            write_toggle:                      = 1
        Second write (w = 1):
            vram_addr_buffer: CBA..HG FED..... = d: HGFEDCBA
            write_toggle:                      = 0
        '''
        if not self.vram_addr_latch:
            # first write, horizontal scroll
            self.vram_addr_buffer &= 0x7fe0
            self.vram_addr_buffer |= ((v & 0xf8) >> 3)
            self.fine_x = v & 0x7
        else:
            # second write, vertical scroll
            self.vram_addr_buffer &= 0xc1f
            self.vram_addr_buffer |= (((v & 0xf8) << 2) | ((v & 0x07) << 12))
        self.vram_addr_latch = not self.vram_addr_latch

    def ppuaddr_write(self, v):
        """ Handle a write to PPUADDR ($2006) """
        '''
        During render:
        First write (w = 0):
            vram_addr_buffer: .FEDCBA ........ = v: ..FEDCBA
            vram_addr_buffer: X...... ........ = 0
            write_toggle:                      = 1
        Second write (w = 1):
            vram_addr_buffer: ....... HGFEDCBA = v: HGFEDCBA
            vram_addr                          = vram_addr_buffer
            write_toggle:                      = 0
        '''
        if not self.vram_addr_latch:
            self.vram_addr_buffer &= 0xff
            self.vram_addr_buffer |= ((v & 0x3f) << 8)
        else:
            self.vram_addr_buffer &= 0x7f00
            self.vram_addr_buffer |= v
            self.vram_addr = self.vram_addr_buffer

            # check sprite0
        self.vram_addr_latch = not self.vram_addr_latch

    def ppudata_write(self, v):
        """ Handle a write to PPUDATA ($2007) """
        self.vram.write(self.vram_addr, v)
        self.increment_vram_address()

    def ppudata_read(self):
        """ Handle a read to PPUDATA ($2007) """
        if 0x0000 <= self.vram_addr < 0x3f00:
            to_return = self.vram_data_buffer
            self.vram_data_buffer = self.vram.read(self.vram_addr)
        else:
            # This may be a little wrong. The docs say that the mirrored
            # nametable data is put in the data buffer, rather than the palette
            # data. But vram - 0x1000 could be non-mirrored nametable data.
            self.vram_data_buffer = self.vram.read(self.vram_addr - 0x1000)
            to_return = self.vram.read(self.vram_addr)
        self.increment_vram_address()
        return to_return

    def dma_write(self, v):
        """ Handle a write to $4014 """
        self.cycle += 1541 % 340
        self.scanline += 4

        base_address = v * 0x100
        for i in range(0, 0x100):
            data = self._nes.cpu.memory.read(base_address + i)
            self.sram64.write(i, data)
            self.update_sprite_buffer(i, data)

    def increment_vram_address(self):
        """
        vram address is incremented differently based on vram_addr_inc flag
        """
        if self.vram_addr_inc:
            self.vram_addr += 32
        else:
            self.vram_addr += 1

    def step(self):
        # if self.vram_addr > 0x4000:
            # with open('vram.txt', 'a') as f:
            #     f.write("Cycle: {}, Address: {}\n".format(self.cycle, self.vram_addr))
        # f.write("{:04X}  {:02X}   A:{:02X} X:{:02X} Y:{:02X} P:{:02X} SP:{:02X} CYC:{:3} SL:{} CTRL:{} MASK:{} STATUS:{} DBUF:{} D:{} ABUF:{} ADDR:{} SRAM:{} FX:{} ALATCH:{} SHIFT1:{} SHIFT2:{}\n".format(self._nes.cpu.registers['pc'].read(),
        #         self._nes.cpu.memory.read(self._nes.cpu.registers['pc'].read()),
        #         self._nes.cpu.registers['a'].read(), self._nes.cpu.registers['x'].read(), self._nes.cpu.registers['y'].read(),
        #         self._nes.cpu.registers['p'].read(), self._nes.cpu.registers['sp'].read(), self.cycle, self.scanline,
        #         self.control, self.mask, self.status, self.vram_data_buffer, self.vram_addr, self.vram_addr_buffer, self.sprite_ram_addr,
        #         self.vram_data, self.fine_x, self.vram_addr_latch, self.shift16_1, self.shift16_2))
        if self.scanline == -1:
            if self.cycle == 1:
                self.status = clear_bit(self.status, StatusBit.InVblank)
                self.status = clear_bit(self.status, StatusBit.SpriteOverflow)
                self.status = clear_bit(self.status, StatusBit.Sprite0Hit)
            if self.cycle == 304:
                '''
                From http://wiki._nesdev.com/w/index.php/PPU_scrolling:
                At the beginning of each frame, the contents of
                vram_addr_buffer copied into vram_addr, as long as background
                or sprites are enabled. This takes place on PPU cycle 304 of
                the pre-render scanline
                '''
                if self.show_background or self.show_sprites:
                    self.vram_addr = self.vram_addr_buffer
        elif self.scanline < 240:
            if self.cycle == 254:
                if self.show_background:
                    self.create_tile_row()
                if self.show_sprites:
                    self.evaluate_sprites()
            elif self.cycle == 256:
                if self.show_background:
                    self.end_scanline()
        elif self.scanline == 241:
            if self.cycle == 1:
                if not self.ignore_vblank:
                    self.status = set_bit(self.status, StatusBit.InVblank)
                if self.nmi_on_vblank == 1 and not self.ignore_nmi:
                    # request NMI from CPU!
                    self._nes.cpu.nmi_requested = 1
                    self.cycle += 21
                self.render_output()
        elif self.scanline == 260:
            if self.cycle >= 340:
                self.scanline = -2
                self.frame_count += 1

        if self.cycle >= 340:
            self.cycle = -1
            self.scanline += 1

        self.cycle += 1

    def create_tile_row(self):
        # get the first tile layer
        low, high, attr = self.get_tile_attributes()
        self.shift16_1, self.shift16_2 = low, high

        # get the second tile layer
        low, high, attr_buffer = self.get_tile_attributes()

        # shift the first tile to make room for the second
        self.shift16_1 = (self.shift16_1 << 8) | low
        self.shift16_2 = (self.shift16_2 << 8) | high

        # for each tile in the row
        for x in range(32):
            # for each pixel in the row of the tile
            for k in range(8):
                fb_row = self.scanline*256 + ((x * 8) + k)
                if self.values[fb_row] != 0:
                    continue

                # a pixel value is taken by layering a bit from each of the
                # 16-bit shift registers; the bit used is computed with k
                # and fine x
                current = (15 - k - self.fine_x)
                pxvalue = ((self.shift16_1 >> current) & 1) | (((self.shift16_2 >> current) & 1) << 1)

                # attr corresponds to the first tile, while attr_buffer
                # corresponds to the second; if we're taking bit 8 or higher,
                # then it's the second tile
                if current >= 8:
                    palette = self.get_background_entry(attr, pxvalue)
                else:
                    palette = self.get_background_entry(attr_buffer, pxvalue)

                # import random
                # palette = random.randrange(64)
                self.colors[fb_row] = rgb_palette[palette % 64]
                self.values[fb_row] = pxvalue
                self.pindexes[fb_row] = -1

            # shift in a new tile
            attr = attr_buffer
            low, high, attr_buffer = self.get_tile_attributes()
            self.shift16_1 = (self.shift16_1 << 8) | low
            self.shift16_2 = (self.shift16_2 << 8) | high

    def get_tile_attributes(self):
        attr_addr = (0x23c0 | (self.vram_addr & 0xc00) |
                     self.attr_loc[self.vram_addr & 0x3ff])
        shift = self.attr_shift[self.vram_addr & 0x3ff]
        attr = ((self.vram.read(attr_addr) >> shift) & 0x3) << 2

        index = self.vram.read(self.vram_addr)
        tile = self.get_bg_tbl_address(index)

        # flip 10th bit on wraparound
        if (self.vram_addr & 0x1f) == 0x1f:
            self.vram_addr ^= 0x41f
        else:
            self.vram_addr += 1

        return self._nes.rom.read_chr(tile), self._nes.rom.read_chr(tile + 8), attr

    def get_background_entry(self, attribute, pixel):
        if not pixel:
            return self.vram.read(0x3f00)

        return self.vram.read(attribute + pixel)

    def get_bg_tbl_address(self, v):
        table = 0x1000 if self.background_tbl_addr else 0x0000
        return (v << 4) | self.vram_addr >> 12 | table

    def update_sprite_buffer(self, address, v):
        i = address / 4
        bit = address % 4
        if bit == 0:
            self.sprite_data['y'][i] = v
        elif bit == 1:
            self.sprite_data['tiles'][i] = v
        elif bit == 2:
            self.sprite_data['attributes'][i] = v
        elif bit == 3:
            self.sprite_data['x'][i] = v

    def evaluate_sprites(self):
        if self.sprite_size:
            sprite_height = 16
        else:
            sprite_height = 8

        sprite_count = 0
        for i, y in zip(range(len(self.sprite_data['y'])), self.sprite_data['y']):
            if (y > (self.scanline - 1) - sprite_height and
                    y + (sprite_height - 1) < (self.scanline - 1) + sprite_height):
                attr_val = self.sprite_data['attributes'][i] & 0x3
                tile = self.sprite_data['tiles'][i]
                c = (self.scanline - 1) - y

                y_flip = self.sprite_data['attributes'][i] >> 7
                if y_flip:
                    y_coord = y + ((sprite_height - 1) - c)
                else:
                    y_coord = y + c + 1

                if self.sprite_size:
                    s = self.get_sprite_tbl_address(tile)

                    top = self._nes.rom.read_tile(s)
                    bottom = self._nes.rom.read_tile(s + 16)

                    if c > 7 and y_flip:
                        tile = top
                        y_coord += 8
                    elif c < 8 and y_flip:
                        tile = bottom
                        y_coord -= 8
                    elif c > 7:
                        tile = bottom
                    else:
                        tile = top

                    self.mux_tile([tile[c % 8], tile[(c % 8)+8]],
                                  self.sprite_data['x'][i], y_coord,
                                  attr_val, i)
                else:
                    s = self.get_sprite_tbl_address(tile)
                    tile = self._nes.rom.read_tile(s)
                    self.mux_tile([tile[c], tile[c+8]],
                                  self.sprite_data['x'][i], y_coord,
                                  attr_val, i)
                sprite_count += 1

                # if sprite_count == 9:
                #     if self.sprite_limit:
                #         set_bit(self.status, StatusBit.SpriteOverflow)
                #         break

    def mux_tile(self, tiles, x, y, palette_index, index):
        attr = self.sprite_data['attributes'][index]
        is_sprite0 = (index == 0)
        for b in range(8):
            if (attr >> 6) & 1 != 0:
                x_coord = x + b
            else:
                x_coord = x + (7 - b)

            if x_coord > 255:
                continue

            fb_row = y * 256 + x_coord

            # store the 0th and 1st bits
            pixel = (tiles[0] >> b) & 0x1
            pixel += ((tiles[1] >> b & 0x1) << 1)

            transparent = 0
            if attr and not pixel:
                transparent = 1

            if fb_row < 0xf000 and not transparent:
                priority = (attr >> 5) & 0x1

                hit = (self.status & 0x40 == 0x40)
                if (self.values[fb_row] != 0 and is_sprite0
                        and not hit):
                    # sprite 0 has been hit
                    self.status = set_bit(self.status, StatusBit.Sprite0Hit)

                if -1 < self.pindexes[fb_row] < index:
                    # higher priority sprite is already rendered here; skip
                    continue
                elif self.values[fb_row] != 0 and priority == 1:
                    # pixel is already rendered and priority 1 indicates
                    # that this should be skipped
                    continue

                pal = self.vram.read(0x3f10 + (palette_index * 0x4) + pixel)
                self.colors[fb_row] = rgb_palette[pal % 64]
                self.values[fb_row] = pixel
                self.pindexes[fb_row] = index

    def get_sprite_tbl_address(self, tile):
        if self.sprite_size:
            # 8x16 sprites
            if tile & 1 != 0:
                return 0x1000 | ((tile >> 1) * 0x20)
            else:
                return (tile >> 1) * 0x20

        if self.sprite_tbl_addr:
            table = 0x1000
        else:
            table = 0

        return tile * 0x10 + table

    def render_output(self):
        for i in range(len(self.colors)-1, -1, -1):
            y = i / 256
            x = i - (y * 256)
            color = self.colors[i]

            # overscan
            # if y < 8 or y > 231 or x < 8 or x > 247:
            #     continue
            # else:
            #     y -= 8
            #     x -= 8

            self.frame_buffer[x][y] = color
            self.values[i] = 0
            self.pindexes[i] = -1
        self.display.NewFrame(self.frame_buffer)

    def update_sprite_buffer(self, address, v):
        i = address / 4
        bit = address % 4
        if bit == 0:
            self.sprite_data['y'][i] = v
        elif bit == 1:
            self.sprite_data['tiles'][i] = v
        elif bit == 2:
            self.sprite_data['attributes'][i] = v
        elif bit == 3:
            self.sprite_data['x'][i] = v

    def end_scanline(self):
        # experiment
        if self.vram_addr & 0x1f == 0x1f:
            self.vram_addr ^= 0x41f
        else:
            self.vram_addr += 1

        if self.vram_addr & 0x1f == 0x1f:
            self.vram_addr ^= 0x41f
        else:
            self.vram_addr += 1

        if self.show_background or self.show_sprites:
            if self.vram_addr & 0x7000 == 0x7000:
                tmp = self.vram_addr & 0x3e0
                self.vram_addr &= 0xfff

                if tmp == 0x3a0:
                    self.vram_addr ^= 0xba0
                elif tmp == 0x3e0:
                    self.vram_addr ^= 0x3e0
                else:
                    self.vram_addr += 0x20
            else:
                self.vram_addr += 0x1000

            self.vram_addr = ((self.vram_addr & 0x7be0) |
                              (self.vram_addr_buffer & 0x41f))
