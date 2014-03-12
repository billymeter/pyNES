import wx
import pygame
import sys
import os

class PygameDisplay(wx.Window):
    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID)
        self.parent = parent
        self.hwnd = self.GetHandle()
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.hwnd)

        self.SetInitialSize((512, 480))

        pygame.display.init()
        self.screen = pygame.display.set_mode()
        self.size = self.GetSizeTuple()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)

    def Update(self, event):
        self.Redraw()

    def Redraw(self):
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def OnPaint(self, event):
        self.Redraw()

    def OnSize(self, event):
        self.size = self.GetSizeTuple()

    def Kill(self, event):
        # Unbind methods which call Redraw() method
        self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
        self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)

class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY)

        self.display = PygameDisplay(self, wx.ID_ANY)
        self.SetTitle("pyNES")

        #initialize menu bar
        menu_bar = wx.MenuBar()

        #file menu options
        file_menu = wx.Menu()
        m_exit = file_menu.Append(wx.ID_EXIT, "Exit\tAlt-X", "Exit pyNES.")
        m_load = file_menu.Append(wx.ID_OPEN, "&Load ROM\tAlt-L", "Load ROM into pyNES")
        self.Bind(wx.EVT_MENU, self.Kill, m_exit)
        self.Bind(wx.EVT_MENU, self.Kill, m_load)
        menu_bar.Append(file_menu, "&File")

        #config menu options
        conf_menu = wx.Menu()
        m_input = conf_menu.Append(wx.ID_ANY, "Input...", "Configure controls")
        m_video = conf_menu.Append(wx.ID_ANY, "Video...", "Configure video")
        m_sound = conf_menu.Append(wx.ID_ANY, "Sound...", "Configure sound")
        self.Bind(wx.EVT_MENU, self.Kill, m_input)
        self.Bind(wx.EVT_MENU, self.Kill, m_video)
        self.Bind(wx.EVT_MENU, self.Kill, m_sound)
        menu_bar.Append(conf_menu, "&Options")

        #finalize menu bar
        self.SetMenuBar(menu_bar)

        #status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-4, -3, -2])
        self.statusbar.SetStatusText("Wolololo", 0)
        self.statusbar.SetStatusText("Statusy status", 1)

        #window behavior
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)

        self.curframe = 0

        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)

        self.timer.Start((1000.0 / self.display.fps))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.display, 1, flag = wx.EXPAND)

        self.SetSizer(sizer)
        self.Fit()
        self.Layout()

    def Kill(self, event):
        self.display.Kill(event)
        pygame.quit()
        self.Destroy()

    def OnSize(self, event):
        self.Layout()

    def Update(self, event):
        self.curframe += 1
        self.statusbar.SetStatusText("Frame %i" % self.curframe, 2)

class App(wx.App):
    def OnInit(self):
        self.frame = Frame(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = App()
    app.MainLoop()
