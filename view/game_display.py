import sys
import os
import wx
import pygame


class Display(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self, *args, **kwargs)
        self.parent = kwargs['parent']
        self.hwnd = self.GetHandle()
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.hwnd)

        self.SetInitialSize((256, 240))

        pygame.display.init()
        self.screen = pygame.display.set_mode((256, 240), pygame.HWSURFACE)
        self.surface = pygame.PixelArray(self.screen)
        self.size = self.GetSizeTuple()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)

    def Update(self, event):
        pass

    def DrawGame(self):
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
