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
        #self.triangle = Triangle(self)
        #self.pulse1 = Pulse(self)
        #self.pulse2 = Pulse(self)

        self.DMC_interrupt = 0
        self.frame_interrupt = 0
        self.length_counter_status = 0
        """
        self.noise.enable = 0
        self.triangle.enable = 0
        self.pulse1.enable = 0
        self.pulse2.enable = 0
        """

    def read(self, reg):  # 0x4015 only
        ret = Byte(0)
        #ret[0] = self.pulse1.enable
        #ret[1] = self.pulse2.enable
        #ret[2] = self.triangle.enable 
        ret[3] = self.noise.enable 
        ret[4] = self.length_counter_status
        # ret[5] = 0
        ret[6] = self.frame_interrupt 
        ret[7] = self.DMC_interrupt 
        return int(ret)

    def write(self, reg, value):
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
        self.sinetest(440.0, 0.5)
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
        self.enable = 0

class Noise(Channel):
    def __init__(self, apu):
        Channel.__init__(self, apu)

    
