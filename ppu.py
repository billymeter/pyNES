'''
Picture Processing Unit
'''
from collections import namedtuple
from utils import *
import numpy as np


''' Constants '''
MirrorType = enum('Vertical', 'Horizontal', 'SingleUpper', 'SingleLower')
AttrTable = (0x23c0, 0x27c0, 0x2bc0, 0x2fc0)
ATTR_TABLE_LENGTH = 0x40
NameTablePos = (0x2000, 0x2400, 0x2800, 0x2c00)
NAMETABLE_LENGTH = 0x400


class Nametables(object):
    def __init__(self):
        self.logical_tables = [[], [], [], []]
        self.nametable0 = [0] * NAMETABLE_LENGTH
        self.nametable1 = [0] * NAMETABLE_LENGTH
        self.mirroring = None

    def set_mirroring(self, m):
        self.mirroring = m

        if self.mirroring == MirrorType.Vertical:
            self.logical_tables[0] = self.nametable0
            self.logical_tables[1] = self.nametable1
            self.logical_tables[2] = self.nametable0
            self.logical_tables[3] = self.nametable1
        elif self.mirroring == MirrorType.Horizontal:
            self.logical_tables[0] = self.nametable0
            self.logical_tables[1] = self.nametable0
            self.logical_tables[2] = self.nametable1
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


class PPU:
    def __init__(self, nes):
        # ppu power up state can be found here:
        # http://wiki.nesdev.com/w/index.php/PPU_power_up_state

        # ppu memory
        self.vram = bytearray(0xffff)
        self.sprite_ram = bytearray(0x100)
        self.nametables = Nametables()

        '''
        +---------+----------------------------------------------------------+
        |  $2000  | PPU Control Register #1 (W)                              |
        |         |                                                          |
        |         |    D7: Execute NMI on VBlank                             |
        |         |           0 = Disabled                                   |
        |         |           1 = Enabled                                    |
        |         |    D6: PPU Master/Slave Selection --+                    |
        |         |           0 = Master                +-- UNUSED           |
        |         |           1 = Slave               --+                    |
        |         |    D5: Sprite Size                                       |
        |         |           0 = 8x8                                        |
        |         |           1 = 8x16                                       |
        |         |    D4: Background Pattern Table Address                  |
        |         |           0 = $0000 (VRAM)                               |
        |         |           1 = $1000 (VRAM)                               |
        |         |    D3: Sprite Pattern Table Address                      |
        |         |           0 = $0000 (VRAM)                               |
        |         |           1 = $1000 (VRAM)                               |
        |         |    D2: PPU Address Increment                             |
        |         |           0 = Increment by 1                             |
        |         |           1 = Increment by 32                            |
        |         | D1-D0: Name Table Address                                |
        |         |         00 = $2000 (VRAM)                                |
        |         |         01 = $2400 (VRAM)                                |
        |         |         10 = $2800 (VRAM)                                |
        |         |         11 = $2C00 (VRAM)                                |
        +---------+----------------------------------------------------------+
        '''

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

        '''
        +---------+----------------------------------------------------------+
        |  $2001  | PPU Control Register #2 (W)                              |
        |         |                                                          |
        |         | D7-D5: Full Background Colour (when D0 == 1)             |
        |         |         000 = None  +------------+                       |
        |         |         001 = Green              | NOTE: Do not use more |
        |         |         010 = Blue               |       than one type   |
        |         |         100 = Red   +------------+                       |
        |         | D7-D5: Colour Intensity (when D0 == 0)                   |
        |         |         000 = None            +--+                       |
        |         |         001 = Intensify green    | NOTE: Do not use more |
        |         |         010 = Intensify blue     |       than one type   |
        |         |         100 = Intensify red   +--+                       |
        |         |    D4: Sprite Visibility                                 |
        |         |           0 = Sprites not displayed                      |
        |         |           1 = Sprites visible                            |
        |         |    D3: Background Visibility                             |
        |         |           0 = Background not displayed                   |
        |         |           1 = Background visible                         |
        |         |    D2: Sprite Clipping                                   |
        |         |           0 = Sprites invisible in left 8-pixel column   |
        |         |           1 = No clipping                                |
        |         |    D1: Background Clipping                               |
        |         |           0 = BG invisible in left 8-pixel column        |
        |         |           1 = No clipping                                |
        |         |    D0: Display Type                                      |
        |         |           0 = Colour display                             |
        |         |           1 = Monochrome display                         |
        +---------+----------------------------------------------------------+
        '''

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

        '''
        vram address format during rendering
        yyy NN YYYYY XXXXX
        ||| || ||||| +++++-- coarse X scroll
        ||| || +++++-------- coarse Y scroll
        ||| ++-------------- nametable select
        +++----------------- fine Y scroll
        '''

        # registers
        self.control = np.uint8(0)
        self.mask = np.uint8(0)
        self.status = np.uint8(0)
        self.vram_data_buffer = np.uint8(0)
        self.vram_addr = np.uint16(0)
        self.vram_addr_buffer = np.uint16(0)
        self.sprite_ram_addr = np.uint16(0)
        self.fine_x = np.uint8(0)
        self.data = np.uint8(0)
        self.first_write = 0
        self.v = [0] * 15    # Current VRAM address
        self.t = [0] * 15    # Temporary VRAM address
        self.x = [0] * 3     # Fine X scroll
        self.w = 0           # First or second write toggle

        # memory maps
        # PPUCTRL = 0x0       # $2000
        # PPUMASK = 0x0       # $2001
        # PPUSTATUS = 0x0     # $2002
        # OAMADDR = 0x0       # $2003
        # OAMDATA = 0x0       # $2004
        # PPUSCROLL = 0x0     # $2005
        # PPUADDR = 0x0       # $2006
        # PPUDATA = 0x0       # $2007

    '''
    PPU render behavior (needs to be implemented):
    The PPU renders 262 scanlines per frame. Each scanline lasts for 341 PPU
    clock cycles (113.667 CPU clock cycles; 1 CPU cycle = 3 PPU cycles),
    with each clock cycle producing one pixel.
    For more info see: http://wiki.nesdev.com/w/index.php/PPU_rendering
    '''

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
        self.mask = np.uint8(value)

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
        self.first_write = 0

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
        if not self.first_write:
            self.vram_addr_buffer = self.vram_addr_buffer & 0x7FE0
            self.vram_addr_buffer = self.vram_addr_buffer | ((v & 0xF8) >> 3)
            self.fine_x = v & 0x07
        else:
            self.vram_addr_buffer = self.vram_addr_buffer & 0xC1F
            self.vram_addr_buffer = (self.vram_addr_buffer |
                                    (((v & 0xF8) << 2) | ((v & 0x07) << 12)))
        self.first_write = not self.first_write

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
        if not self.w:
            self.vram_addr_buffer = self.vram_addr_buffer & 0xFF
            self.vram_addr_buffer = self.vram_addr_buffer | ((v & 0x3F) << 8)
        else:
            self.vram_addr_buffer = self.vram_addr_buffer & 0x7F00
            self.vram_addr_buffer = self.vram_addr_buffer | v
            self.vram_addr = self.vram_addr_buffer
        self.first_write = not self.first_write
