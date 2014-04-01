from pygame_display import *
from options_dialogs import *


class MainView(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY)
        self.parent = parent
        self.SetTitle("pyNES")

        # pygame display
        self.display = PygameDisplay(self, wx.ID_ANY)

        #initialize menu bar
        menu_bar = wx.MenuBar()

        # CONSTRUCTORS #
        # file menu options
        file_menu = wx.Menu()
        m_exit = file_menu.Append(wx.ID_EXIT, "Exit\tAlt-X", "Exit pyNES.")
        m_load = file_menu.Append(wx.ID_OPEN, "&Load ROM\tAlt-L",
                                  "Load ROM into pyNES")
        # config menu options
        conf_menu = wx.Menu()
        m_input = conf_menu.Append(wx.ID_ANY, text="Input...",
                                   help="Configure Input")
        m_video = conf_menu.Append(wx.ID_ANY, "Video...", "Configure video")
        m_sound = conf_menu.Append(wx.ID_ANY, "Sound...", "Configure sound")

        # BINDS #
        # file menu binds
        self.Bind(wx.EVT_MENU, self.Kill, m_exit)
        self.Bind(wx.EVT_MENU, self.Kill, m_load)
        menu_bar.Append(file_menu, "&File")

        # option menu binds
        self.Bind(wx.EVT_MENU, self.OnOptionsInput, m_input)
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

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.display, 1, flag=wx.EXPAND)

        #window behavior
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)

        self.SetSizer(sizer)
        self.Fit()
        self.Layout()

    def OnOptionsInput(self, event):
        frame = OptionsInput(parent=self, title="Input Settings")
        frame.ShowModal()

    def OnSize(self, event):
        self.Layout()

    def Kill(self, event):
        self.display.Kill(event)
        pygame.quit()
        self.Destroy()
