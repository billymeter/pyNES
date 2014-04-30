__author__ = 'Micah'

import pygame
import sys
import nes

with open("roms/mario.nes", 'rb') as rom:
    emu = nes.NES(rom.read())

pygame.init()
screen = pygame.display.set_mode((256, 240))
emu.ppu.display = 0

gamepad1 = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'a': pygame.K_z,
    'b': pygame.K_x,
    'select': pygame.K_a,
    'start': pygame.K_r
}
gamepad2 = {
    'up': 0,
    'down': 0,
    'left': 0,
    'right': 0,
    'a': 0,
    'b': 0,
    'select': 0,
    'start': 0
}

while 1:
    emu.step()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            for button in gamepad1:
                if event.key == gamepad1[button]:
                    emu.parse_input(1, button, 1)
            for button in gamepad2:
                if event.key == gamepad2[button]:
                    emu.parse_input(2, button, 1)
        elif event.type == pygame.KEYUP:
            for button in gamepad1:
                if event.key == gamepad1[button]:
                    emu.parse_input(1, button, 0)
            for button in gamepad2:
                if event.key == gamepad2[button]:
                    emu.parse_input(2, button, 0)

    if emu.ppu.display == 1:
        emu.ppu.display = 0
        pygame.surfarray.blit_array(screen, emu.ppu.colors)
        pygame.display.update()