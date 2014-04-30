import pygame
import math
import numpy as np
import pygame.sndarray



class APU:
    def __init__(self, cpu):
        # I can't actually change the default samp rate
        self.sample_rate = 22050
        pygame.mixer.init(frequency = self.sample_rate, size = -16, channels = 2) # 22.05kHz, 16-bit signed, stereo

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
    
