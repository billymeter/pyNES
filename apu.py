
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
            self.square1.tick(halfTick, fullTick)
            self.square2.tick(halfTick, fullTick)
            self.triangle.tick(halfTick, fullTick)
            self.noise.tick(halfTick, fullTick)
            # self.DMC.tick(halfTick, fullTick)
    class square:
        def __init__(self, apu):
            self.apu = apu
            # 0x00
            self.duty = 0
            self.halt = 0
            self.cv = 0
            self.v = 0
            # 0x01
            self.se = 0
            self.sp = 0
            self.sn = 0
            self.ss = 0
            # 0x02
            # self.timerlow = 0
            # 0x03
            self.length = 0
            # self.timerhigh = 0
            self.period = 0

        def write(self, reg, value):
            reg &= 3
            value &= 0xFF
            if reg == 0:
                self.duty = (value >> 6) & 3
                self.halt = (value >> 5) & 1
                self.cv = (value >> 4) & 1
                self.v = value & 0xf
            if reg == 1:
                self.se = (value >> 7) & 1
                self.sp = (value >> 4) & 7
                self.sn = (value >> 3) & 1
                self.ss = value & 7
            if reg == 2:
                self.period = value + self.period & 0x700
            if reg == 3:
                self.length = (value >> 3) & 0x1F
                self.period = (self.period & 0xFF) + ((value & 7) << 8)
        def tick(self, halfTick, fullTick):



    class triangle:

    class noise:

    class DMC:


