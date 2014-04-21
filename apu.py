
"""
self.apu = apu.APU(self)
return self._nes.apu.get_status() $ 0xff
self._nes.apu.write_register(addr, value)
self._nes.apu.tick()
"""

class APU:
    def __init__(self, nes):
        self._nes = nes
        self.fiveCycleDivider = False
        self.IRQdisable = True
        self.channelsEnabled = [False] * 5
        self.periodicIRQ = False
        self.DMCIRQ = False  # probably won't get implemented

        self.fastCount = 0  # 240Hz, lo
        self.slowCount = 0  # 60Hz, hi

    def tick(self):
        self.fastCount += 2
        if self.fastCount >= 14915:
            self.fastCount -= 14915;
            self.slowCount += 1
            if self.slowCount >= (5 if self.fiveCycleDivider else 4):
                self.slowCount = 0
            if not self.IRQdisable and not self.fiveCycleDivider and not self.slowCount:
                self.periodicIRQ = True
                # do something to the CPU to enable the interrupt (no the flag)
            halfTick = self.slowCount & 5
            fullTick = self.slowCount < 4
            self.square1.tick()
            self.square2.tick()
            self.triangle.tick()
            self.noise.tick()
            # self.DMC.tick()
    class square:
        def __init__(self, apu):
            self.apu = apu
            # 0x00
            self.duty = 0
            self.loop = 0
            self.cv = 0
            self.v = 0
            # 0x01
            self.se = 0
            self.sp = 0
            self.sn = 0
            self.ss = 0
            # 0x02
            self.timerlow = 0
            # 0x03
            self.load = 0
            self.timerhigh = 0

        def write(self, reg, value):
            reg &= 3
            value &= 0xFF
            if reg == 0:
                self.duty = (value >> 6) & 3
                self.loop = (value >> 5) & 1
                self.cv = (value >> 4) & 1
                self.v = value & 0xf
            if reg == 1:
                self.se = (value >> 7) & 1
                self.sp = (value >> 4) & 7
                self.sn = (value >> 3) & 1
                self.ss = value & 7
            if reg == 2:
                self.timerlow = value
            if reg == 3:
                self.load = (value >> 3) & 0x1F
                self.timerhigh = value & 7
        def tick():
            


    class triangle:

    class noise:

    class DMC:


