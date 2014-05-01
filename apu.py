import pygame
import math
import numpy as np
import pygame.sndarray



class APU:
    def __init__(self, cpu):
        # I can't actually change the default samp rate
        self.sample_rate = 22050
        pygame.mixer.init(frequency = self.sample_rate, size = -16, channels = 2) # 22.05kHz, 16-bit signed, stereo

        self.noise = Noise(self)
        self.triangle = Triangle(self)
        self.pulse1 = Pulse(self)
        self.pulse2 = Pulse(self)
        self.pulse = [self.pulse1, self.pulse2]
        self.DMC = DMC(self)

        self.DMC.interrupt = 0
        self.frame_interrupt = 0
        self.length_counter_status = 0
        """
        self.noise.enable = 0
        self.triangle.enable = 0
        self.pulse1.enable = 0
        self.pulse2.enable = 0
        """

        self.fiveframe = 0
        self.disable_frame_int = 1

        self._clock = 0
        self._fast_clock = 0

    def read(self, reg):  # 0x4015 only
        ret = Byte(0)
        ret[0] = self.pulse1.enable()
        ret[1] = self.pulse2.enable()
        ret[2] = self.triangle.enable()
        ret[3] = self.noise.enable()
        ret[4] = self.DMC.enable()
        # ret[5] = 0
        ret[6] = self.frame_interrupt 
        self.frame_interrupt = 0
        ret[7] = self.DMC.interrupt 
        # print "irq reset"
        return int(ret)

    def write(self, reg, value):
        value = Byte(value)
        reg &= 0xFF
        if reg < 8:
            self.pulse[reg // 4].write(reg, value)
        elif reg in [0x8, 0xA, 0xB]:
            self.triangle.write(reg, value)
        elif reg in [0xC, 0xE, 0xF]:
            self.noise.write(reg, value)
        elif reg in [0x10, 0x11, 0x12, 0x13]:
            self.DMC.write(reg, value)
        elif reg == 0x15:
            self.DMC.enable(value[4])
            self.noise.enable(value[3])
            self.triangle.enable(value[2])
            self.pulse2.enable(value[1])
            self.pulse1.enable(value[0])
        elif reg == 0x17:
            self.fiveframe = value[7]
            self.disable_frame_int = value[6]
            if self.disable_frame_int:
                self.frame_interrupt = 0
            # print(value)
            # print self.disable_frame_int, self.fiveframe


    def clock(self, cycles):
        self._fast_clock += 2*cycles
        if self._fast_clock > 14915:  # I think this needs changing
            self._fast_clock -= 14915
            # clock envelopes and triangle's linear counter
            self.fast_clock()
            self._clock += 1
            self._clock %= 5 if self.fiveframe else 4
            if self._clock < 4:

                if self._clock % 2 == self.fiveframe:
                    # clock length counters and sweep units
                    self.slow_clock()
                    self.slow_clock()
                if self._clock == 3 and not self.fiveframe and not self.disable_frame_int:
                        # print "irq set"
                        self.frame_interrupt = 1

    def slow_clock(self):
        # clock length counters and sweep units
        # TODO: EVERYTHING
        pass
    def fast_clock(self):
        # clock envelopes and triangle's linear counter
        # TODO: EVERYTHING
        pass





    def play_floats(self, floatsound):
        floatsound *= 2**15
        s = np.int16(zip(floatsound, floatsound))
        self.play(s)

    def play(self, rawsound):
        s = pygame.sndarray.make_sound(rawsound)
        s.play(0)

    def sinetest(self, freq, runtime):
        raw = np.array([math.sin(x*2.0*math.pi*freq/self.sample_rate) for x in xrange(0, int(runtime*self.sample_rate))])
        self.play_floats(raw)
        
    def testtone(self):
        self.sinetest(440.0, 0.1)
        # raw_input()

class Byte():
    def __init__(self, val):
        self.val = val
    def __getitem__(self, s):
        if type(s) is slice:
            ret = self.val
            ret >>= s.start
            ret &= 1<<(s.stop - s.start + 1) - 1
        else:
            ret = (self.val >> s) & 1
        return ret
    def __setitem__(self, s, value):
        if type(s) is slice:
            mask = (1<<(s.stop - s.start + 1) - 1) << s.start
            newval = self.val & ~(mask)
            newval += (value << s.start) & mask
        else:
            newval = self.val & ~(1<<s)
            newval += (value << s) & (1<<s)
        self.val = newval
    def __str__(self):
        return str(self.val)
    def __int__(self):
        return self.val



class Channel():
    def __init__(self, apu):
        self.apu = apu
        self.enable(0)
        
        self._enabled = 0

        self.duty = 0
        self.loop_envelope = 0
        self.const_vol = 0
        self.volume = 0

        self.sweep = 0
        self.sweep_en = 0
        self.sweep_period = 0
        self.sweep_negative = 0
        self.sweep_shift = 0
        self.sweep_start = 0

        self.timer = 0
        self.length_counter = 0
        self.length_counter = 0
        self.envelope_start = 0
        self.envelope_counter = 0
        self.envelope = 0
        
        
        
    def enable(self, val = None):
        if val is not None:
            self._enabled = val
            if not val:
                self.length_counter = 0
        else:
            return self._enabled and self.length_counter > 0

    def fast_clock(self):
        # clock envelopes and triangle's linear counter

        if self.length_counter and not self.loop_envelope:
            self.length_counter -= 1

        if self.envelope_start:
            self.envelope_start = 0
            self.envelope_counter = 15

        if self.loop_envelope and not self.envelope_counter:
            self.envelope_counter = 15
        elif self.envelope_counter:
            self.envelope_counter -= 1


    def slow_clock(self):
        # clock length counters and sweep units
        # TODO: EVERYTHING
        pass



    def get_volume(self):
        if self.const_vol:
            return self.volume
        else:
            return self.envelope_counter


class Pulse(Channel):
    def __init__(self, apu):
        Channel.__init__(self, apu)
        self.length_lookup = [0x0A,0xFE,0x14,0x02,0x28,0x04,0x50,0x06,0xA0,0x08,0x3C,0x0A,0x0E,0x0C,0x1A,0x0E,0x0C,0x10,0x18,0x12,0x30,0x14,0x60,0x16,0xC0,0x18,0x48,0x1A,0x10,0x1C,0x20,0x1E]

    def write(self, reg, value):
        reg %= 4
        if not reg:
            self.duty = value[6:7]
            self.loop_envelope = value[5]  # aka length counter halt
            self.const_vol = value[4]
            self.volume = value[0:3]
        if reg == 1:
            self.sweep_en = value[7]
            self.sweep_period = value[4:6]
            self.sweep_negative = value[3]
            self.sweep_shift = value[0:2]
            self.sweep_start = 1
        if reg == 2:
            self.timer &= 0x700
            self.timer += value[0:7]
        if reg == 3:
            self.timer &= 0xFF
            self.timer += value[0:2]
            self.length_counter = self.length_lookup[value[3:7]]
            self.envelope_start = 1
            self.sequence = 0
    


class Noise(Channel):
    def __init__(self, apu):
        Channel.__init__(self, apu)
    def write(self, reg, value):
        pass

class Triangle(Channel):
    def __init__(self, apu):
        Channel.__init__(self, apu)
    def write(self, reg, value):
        pass

class DMC(Channel):
    def __init__(self, apu):
        Channel.__init__(self, apu)
        self.interrupt = 0
    def write(self, reg, value):
        pass


    
