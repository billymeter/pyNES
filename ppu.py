'''
Picture Processing Unit
'''


class PPU:
    __init__(self, nes):
        # ppu power up state can be found here:
        # http://wiki.nesdev.com/w/index.php/PPU_power_up_state

        '''
        v, t format during rendering
        yyy NN YYYYY XXXXX
        ||| || ||||| +++++-- coarse X scroll
        ||| || +++++-------- coarse Y scroll
        ||| ++-------------- nametable select
        +++----------------- fine Y scroll
        '''

        # registers
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

    def ppuctrl_write(self, value):
        """ t: ...BA.. ........ = value: ......BA """
        if value & 0x2:
            self.t[3] = 1
        if value & 0x1:
            self.t[4] = 1

    def ppustatus_read(self):
        """ Write toggle is reset -- w = 0"""
        self.w = 0

    def ppuscroll_write(self, value):
        """
        First write (w = 0):
            t: ....... ...HGFED = d: HGFED...
            x:              CBA = d: .....CBA
            w:                  = 1
        Second write (w = 1):
            t: CBA..HG FED..... = d: HGFEDCBA
            w:                  = 0
        """
        if self.w == 0:
            self.t[11:] = [1 if value & 1 << k > 0 else 0
                           for k in range(7, 2, -1)]
            self.x = [1 if value & 1 << k > 0 else 0
                      for k in range(2, -1, -1)]
            self.w = 1
        else:
            self.t[:3] = [1 if value & 1 << k > 0 else 0
                          for k in range(2, -1, -1)]
            self.t[5:11] = [1 if value & 1 << k > 0 else 0
                            for k in range(7, 2, -1)]
            self.w = 0

    def ppuaddr_write(self, value):
        """
        First write (w = 0):
            t: .FEDCBA ........ = d: ..FEDCBA
            t: X...... ........ = 0
            w:                  = 1
        Second write (w = 1):
            t: ....... HGFEDCBA = d: HGFEDCBA
            v                   = t
            w:                  = 0
        """
        if self.w == 0:
            self.t[1:8] = [1 if value & 1 << k > 0 else 0
                           for k in range(5, -1, -1)]
            self.t[0] = 0
            self.w = 1
        else:
            self.t[8:] = [1 if value & 1 << k > 0 else 0
                          for k in range(7, -1, -1)]
            self.v = self.t[:]
            self.w = 0
