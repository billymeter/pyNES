'''
Picture Processing Unit
'''
from collections import namedtuple
from utils import *
import logging
import numpy as np

logging.basicConfig(filename='errors.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

rgb_palette = [(0x1D << 2, 0x1D << 2, 0x1D << 2),
               (0x09 << 2, 0x06 << 2, 0x23 << 2),
               (0x00 << 2, 0x00 << 2, 0x2A << 2),
               (0x11 << 2, 0x00 << 2, 0x27 << 2),
               (0x23 << 2, 0x00 << 2, 0x1D << 2),
               (0x2A << 2, 0x00 << 2, 0x04 << 2),
               (0x29 << 2, 0x00 << 2, 0x00 << 2),
               (0x1F << 2, 0x02 << 2, 0x00 << 2),
               (0x10 << 2, 0x0B << 2, 0x00 << 2),
               (0x00 << 2, 0x11 << 2, 0x00 << 2),
               (0x00 << 2, 0x14 << 2, 0x00 << 2),
               (0x00 << 2, 0x0F << 2, 0x05 << 2),
               (0x06 << 2, 0x0F << 2, 0x17 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x2F << 2, 0x2F << 2, 0x2F << 2),
               (0x00 << 2, 0x1C << 2, 0x3B << 2),
               (0x08 << 2, 0x0E << 2, 0x3B << 2),
               (0x20 << 2, 0x00 << 2, 0x3C << 2),
               (0x2F << 2, 0x00 << 2, 0x2F << 2),
               (0x39 << 2, 0x00 << 2, 0x16 << 2),
               (0x36 << 2, 0x0A << 2, 0x00 << 2),
               (0x32 << 2, 0x13 << 2, 0x03 << 2),
               (0x22 << 2, 0x1C << 2, 0x00 << 2),
               (0x00 << 2, 0x25 << 2, 0x00 << 2),
               (0x00 << 2, 0x2A << 2, 0x00 << 2),
               (0x00 << 2, 0x24 << 2, 0x0E << 2),
               (0x00 << 2, 0x20 << 2, 0x22 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x3F << 2, 0x3F << 2, 0x3F << 2),
               (0x0F << 2, 0x2F << 2, 0x3F << 2),
               (0x17 << 2, 0x25 << 2, 0x3F << 2),
               (0x33 << 2, 0x22 << 2, 0x3F << 2),
               (0x3D << 2, 0x1E << 2, 0x3F << 2),
               (0x3F << 2, 0x1D << 2, 0x2D << 2),
               (0x3F << 2, 0x1D << 2, 0x18 << 2),
               (0x3F << 2, 0x26 << 2, 0x0E << 2),
               (0x3C << 2, 0x2F << 2, 0x0F << 2),
               (0x20 << 2, 0x34 << 2, 0x04 << 2),
               (0x13 << 2, 0x37 << 2, 0x12 << 2),
               (0x16 << 2, 0x3E << 2, 0x26 << 2),
               (0x00 << 2, 0x3A << 2, 0x36 << 2),
               (0x1E << 2, 0x1E << 2, 0x1E << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x3F << 2, 0x3F << 2, 0x3F << 2),
               (0x2A << 2, 0x39 << 2, 0x3F << 2),
               (0x31 << 2, 0x35 << 2, 0x3F << 2),
               (0x35 << 2, 0x32 << 2, 0x3F << 2),
               (0x3F << 2, 0x31 << 2, 0x3F << 2),
               (0x3F << 2, 0x31 << 2, 0x36 << 2),
               (0x3F << 2, 0x2F << 2, 0x2C << 2),
               (0x3F << 2, 0x36 << 2, 0x2A << 2),
               (0x3F << 2, 0x39 << 2, 0x28 << 2),
               (0x38 << 2, 0x3F << 2, 0x28 << 2),
               (0x2A << 2, 0x3C << 2, 0x2F << 2),
               (0x2C << 2, 0x3F << 2, 0x33 << 2),
               (0x27 << 2, 0x3F << 2, 0x3C << 2),
               (0x31 << 2, 0x31 << 2, 0x31 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2),
               (0x00 << 2, 0x00 << 2, 0x00 << 2)]


class NameTables(object):
    """
    Name table occupy 0x2000 through 0x2fff in PPU memory map, and are
    mirrored at 0x3000.
    """
    def __init__(self):
        self.logical_tables = [[], [], [], []]
        self.nametable0 = [0] * NAMETABLE_SIZE
        self.nametable1 = [0] * NAMETABLE_SIZE
        self.mirroring = None

    def set_mirroring(self, m):
        self.mirroring = m

        if self.mirroring == MirrorType.Horizontal:
            self.logical_tables[0] = self.nametable0
            self.logical_tables[1] = self.nametable0
            self.logical_tables[2] = self.nametable1
            self.logical_tables[3] = self.nametable1
        elif self.mirroring == MirrorType.Vertical:
            self.logical_tables[0] = self.nametable0
            self.logical_tables[1] = self.nametable1
            self.logical_tables[2] = self.nametable0
            self.logical_tables[3] = self.nametable1
        elif self.mirroring == MirrorType.SingleUpper:
            self.logical_tables[0] = self.nametable0
            self.logical_tables[1] = self.nametable0
            self.logical_tables[2] = self.nametable0
            self.logical_tables[3] = self.nametable0
        elif self.mirroring == MirrorType.SingleLower:
            self.logical_tables[0] = self.nametable1
            self.logical_tables[1] = self.nametable1
            self.logical_tables[2] = self.nametable1
            self.logical_tables[3] = self.nametable1

    def write(self, addr, value):
        self.logical_tables[(addr & 0xc00) >> 10][addr & 0x3ff] = value

    def read(self, addr):
        return self.logical_tables[(addr & 0xc00) >> 10][addr & 0x3ff]


SpriteData = namedtuple('SpriteData', 'y tiles attributes x')


class PPU(object):
    def __init__(self, nes):
        self._nes = nes
        # ppu memory
        self.vram = [0] * 0x10000
        self.sprite_ram = [0] * 0x100
        self.palette_ram = [0] * 0x20
        self.nametables = NameTables()
        # pattern tables aren't actually in the ppu, they're on the cartridge
        # self.patterntables = PatternTables()
        # still confused about sprites; not sure if this is good
        self.sprite_data = SpriteData([0] * 64, [0] * 64, [0] * 64, [0] * 64)
        self.sprite_data = {
            'y': [0] * 64,
            'tiles': [0] * 64,
            'attributes': [0] * 64,
            'x': [0] * 64
        }

        # render states
        self.palette_buffer = [{'color': 0, 'value': 0, 'index': 0}] * 61440
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
        # self.shift8_1 = 0
        # self.shift8_2 = 0

        # other state
        self.frame_count = 0
        self.cycle = 0
        self.scanline = 241
        self.ignore_nmi = 0
        self.ignore_vblank = 0

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
        # get current status
        tmp = self._nes.cpu.read(0x2002)

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
        if self.scanline == 240 and self.cycle == 1:
            # a read at this (scanline, cycle) causes skips
            tmp &= 0x7f
            self.ignore_nmi = 1
            self.ignore_vblank = 1
        else:
            # vblank flag is cleared
            clear_bit(self.status, StatusBit.InVblank)
            self.ignore_nmi = 0
            self.ignore_vblank = 0

        return tmp

    def oamaddr_write(self, v):
        """ Handle a write to OAMADDR ($2003) """
        self.sprite_ram_addr = v

    def oamdata_write(self, v):
        """ Handle a write to OAMDATA ($2004) """
        self.sprite_ram[self.sprite_ram_addr] = v
        self.update_sprite_buffer(self.sprite_ram_addr, v)
        self.sprite_ram_addr += 1
        self.sprite_ram_addr %= 0x100

    def oamdata_read(self):
        """ Handle a read to OAMDATA ($2004) """
        return self.sprite_ram[self.sprite_ram_addr]

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
        if self.vram_addr_latch:
            # first write, horizontal scroll
            self.vram_addr_buffer &= 0x7fe0
            self.vram_addr_buffer |= ((v & 0xf8) >> 3)
            self.fine_x = v & 0x07
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
        if self.vram_addr_latch:
            self.vram_addr_buffer &= 0xff
            self.vram_addr_buffer |= ((v & 0x3f) << 8)
        else:
            self.vram_addr_buffer &= 0x7f00
            self.vram_addr_buffer |= v
            self.vram_addr = self.vram_addr_buffer
        self.vram_addr_latch = not self.vram_addr_latch

    def ppudata_write(self, v):
        """ Handle a write to PPUDATA ($2007) """
        if self.vram_addr > 0x3000:
            self.write_mirrored_vram(self.vram_addr, v)
        elif self.vram_addr >= 0x2000 and self.vram_addr < 0x3000:
            self.nametables.write(self.vram_addr, v)
        elif self.vram_addr < 0x2000:
            self._nes.rom.write_chr(self.vram_addr, v)
        else:
            self.vram[self.vram_addr & 0x3fff] = v
        self.inc_vram_address()

    def ppudata_read(self):
        """ Handle a read to PPUDATA ($2007) """
        if 0x2000 <= self.vram_addr < 0x3000:
            data = self.vram_data_buffer
            self.vram_data_buffer = self.nametables.read(self.vram_addr)
        elif self.vram_addr < 0x3f00:
            data = self.vram_data_buffer

            if self.vram_addr < 0x2000:
                self.vram_data_buffer = self._nes.rom.read_chr(self.vram_addr)
            else:
                self.vram_data_buffer = self.vram[self.vram_addr]
        else:
            buffer_addr = self.vram_addr - 0x1000
            if 0x2000 <= buffer_addr < 0x3000:
                self.vram_data_buffer = self.nametables.read(buffer_addr)
            else:
                self.vram_data_buffer = self.vram[buffer_addr]

            address = self.vram_addr
            if address & 0xf == 0:
                address = 0
            data = self.palette_ram[address & 0x1f]

        self.inc_vram_address()

        return data

    def dma_write(self, v):
        """ Handle a write to $4014 """
        self._nes.cpu.cycles += 513

        base_address = v * 0x100
        for i in range(self.sprite_ram_addr, 0x100):
            data = self._nes.cpu.read(base_address + i)
            self.sprite_ram[i] = data
            self.update_sprite_buffer(i, data)

    def inc_vram_address(self):
        """
        vram address is incremented differently based on vram_addr_inc flag
        """
        if self.vram_addr_inc:
            self.vram_addr += 32
        else:
            self.vram_addr += 1

    def step(self):
        if self.scanline == -1:
            if self.cycle == 1:
                clear_bit(self.status, StatusBit.SpriteOverflow)
                clear_bit(self.status, StatusBit.Sprite0Hit)
            if self.cycle == 304:
                '''
                From http://wiki.nesdev.com/w/index.php/PPU_scrolling:
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
        elif self.scanline == 241:
            if self.cycle == 1:
                if not self.ignore_vblank:
                    set_bit(self.status, StatusBit.InVblank)
                if self.nmi_on_vblank == 1 and not self.ignore_nmi:
                    # request interrupt from CPU!
                    self._nes.cpu.set_status('interrupt', 1)
                self.render_output()
        elif self.scanline == 260:
            if self.cycle == 1:
                clear_bit(self.status, StatusBit.InVblank)
            elif self.cycle == 341:
                self.scanline = -1
                self.cycle = 1
                self.frame_count += 1

        if self.cycle == 341:
            self.cycle = 0
            self.scanline += 1

        self.cycle += 1

    def create_tile_row(self):
        low, high, attr = self.get_tile_attributes()
        self.shift16_1, self.shift16_2 = low, high

        low, high, attr_buffer = self.get_tile_attributes()

        self.shift16_1 = (self.shift16_1 << 8) | low
        self.shift16_2 = (self.shift16_2 << 8) | high

        # for each tile in the row
        for x in range(32):

            # for each pixel in the row of the tile
            for k in range(8):
                fb_row = self.scanline*256 + ((x * 8) + k)
                pixel = self.palette_buffer[fb_row]
                if pixel['value'] != 0:
                    continue

                current = (15 - k - self.fine_x)
                pxvalue = (((self.shift16_1 >> current) & 1) |
                           (((self.shift16_2 >> current) & 1) << 1))

                if current >= 8:
                    palette = self.get_background_entry(attr, pxvalue)
                else:
                    palette = self.get_background_entry(attr_buffer, pxvalue)

                pixel['color'] = rgb_palette[palette % 64]
                pixel['value'] = pxvalue
                pixel['index'] = -1

            attr = attr_buffer

            low, high, attr_buffer = self.get_tile_attributes()

            self.shift16_1 = (self.shift16_1 << 8) | low
            self.shift16_2 = (self.shift16_2 << 8) | high

    def get_tile_attributes(self):
        attr_addr = (0x23c0 | (self.vram_addr & 0xc00) |
                     self.attr_loc[self.vram_addr & 0x3ff])
        shift = self.attr_shift[self.vram_addr & 0x3ff]
        attr = ((self.nametables.read(attr_addr) >> shift) & 0x3) << 2

        index = self.nametables.read(self.vram_addr)
        tile = self.get_bg_tbl_address(index)

        # flip 10th bit on wraparound
        if self.vram_addr & 0b11111 == 0b11111:
            self.vram_addr ^= 0x41f
        else:
            self.vram_addr += 1

        return self.vram[tile], self.vram[tile + 8], attr

    def get_background_entry(self, attribute, pixel):
        if not pixel:
            return self.palette_ram[0]

        return self.palette_ram[attribute + pixel]

    def get_bg_tbl_address(self, v):
        table = 1 if self.background_tbl_addr else 0

        return v | (v << 4) | self.vram_addr >> 12

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

                    top = self._nes.rom.read_chr(s, 16)
                    bottom = self._nes.rom.read_chr(s + 16, 16)

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
                else:
                    s = self.get_sprite_tbl_address(tile)
                    tile = self._nes.rom.read_chr(s, 16)

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
            if (attr >> 6) & 1:
                x_coord = x + b
            else:
                x_coord = x + (7 - b)

            if x_coord > 255:
                continue

            fb_row = y * 256 + x_coord

            pixel = (tiles[0] >> b) & 0x1
            pixel += ((tiles[1] >> b & 0x1) << 1)

            trans = 0
            if not attr and not pixel:
                trans = 1

            if fb_row < 0xf000 and not trans:
                px = self.palette_buffer[fb_row]
                priority = (attr >> 5) & 0x1

                hit = self._nes.cpu.read(0x2002) & 0x40
                if px['value'] != 0 and is_sprite0 and not hit:
                    # sprite 0 has been hit
                    set_bit(self.status, StatusBit.Sprite0Hit)

                if -1 < px['index'] < index:
                    # higher priority sprite is already rendered here; skip
                    continue
                elif px['value'] != 0 and priority == 1:
                    # pixel is already rendered and priority 1 indicates
                    # that this should be skipped
                    continue

                pal = self.palette_ram[0x10 + (palette_index * 0x4) + pixel]

                self.palette_buffer[fb_row]['color'] = rgb_palette[pal % 64]
                self.palette_buffer[fb_row]['value'] = pixel
                self.palette_buffer[fb_row]['index'] = index

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

        return table | (tile << 4) | (self.vram_addr >> 12)

    def write_mirrored_vram(self, address, v):
        if address >= 0x3f00:
            if address & 0xf == 0:
                address = 0
            self.palette_ram[address & 0x1f] = v
        else:
            self.nametables.write(address - 0x1000, v)

    def render_output(self):
        for i in range(len(self.palette_buffer)-1, -1, -1):
            y = i / 256
            x = i - (y * 256)
            color = self.palette_buffer[i]['color']

            # overscan
            # if y < 8 or y > 231 or x < 8 or x > 247:
            #     continue
            # else:
            #     y -= 8
            #     x -= 8

            width = 256
            self.frame_buffer[x][y] = color << 8
            self.palette_buffer[i]['value'] = 0
            self.palette_buffer[i]['index'] = -1
        # from random import randrange
        # i = randrange(256)
        # dumb_buffer = np.array([[i] * 240] * 256, ndmin=2, dtype=np.uint32)
        # self.display.NewFrame(dumb_buffer)
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
