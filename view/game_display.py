import sys
import os
import wx
import pygame


class Display(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self, *args, **kwargs)
        self.parent = kwargs['parent']
        self.nes = None
        self.hwnd = self.GetHandle()
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.hwnd)

        self.SetInitialSize((256, 240))

        pygame.display.init()
        self.screen = pygame.display.set_mode((256, 240), pygame.HWSURFACE)
        self.surface = pygame.surfarray.pixels2d(self.screen)
        # self.surface = pygame.PixelArray(self.screen)
        self.size = self.GetSizeTuple()

        self.gamepad1 = {
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'a': 0,
            'b': 0,
            'select': 0,
            'start': 0,
        }
        self.gamepad2 = {
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'a': 0,
            'b': 0,
            'select': 0,
            'start': 0
        }

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)

    def Update(self, event):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RSHIFT:
                    for i in range(32):
                        self.nes.ppu.vram.nametable.nt_changed[i] = 1
                for button in self.gamepad1:
                    if event.key == self.gamepad1[button]:
                        self.nes.parse_input(1, button, 1)
                for button in self.gamepad2:
                    if event.key == self.gamepad2[button]:
                        self.nes.parse_input(2, button, 1)
            elif event.type == pygame.KEYUP:
                for button in self.gamepad1:
                    if event.key == self.gamepad1[button]:
                        self.nes.parse_input(1, button, 0)
                for button in self.gamepad2:
                    if event.key == self.gamepad2[button]:
                        self.nes.parse_input(2, button, 0)
        # self.Redraw()

    def Redraw(self):
        pygame.display.update()


    def NewScanline(self, buffer, y):
        for x in range(256):
            self.surface[x, y] = buffer[x, y]
        pygame.display.update(pygame.Rect(0, y-1, 256, 2))

    def NewFrame(self, buffer):
        # pygame.pixelcopy.array_to_surface(self.screen, buffer)
        pygame.surfarray.blit_array(self.screen, buffer)
        pygame.display.update()

    def OnPaint(self, event):
        self.Redraw()

    def OnSize(self, event):
        self.size = self.GetSizeTuple()

    def Kill(self, event):
        # Unbind methods which call Redraw() method
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
        self.Unbind(event=wx.EVT_TIMER, handler=self.Update, source=self.timer)
        pygame.quit()
