from wx.lib.pubsub import pub
from game_display import *
from options_dialogs import *


class MainView(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetTitle("pyNES")

        # Display for emulator
        self.display = Display(parent=self)

        # Menu bar
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        m_load = file_menu.Append(id=wx.ID_OPEN, text="Load ROM\tCtrl-O",
                                  help="Load ROM into pyNES")
        m_exit = file_menu.Append(id=wx.ID_EXIT, text="Exit\tCtrl-Q",
                                  help="Exit pyNES.")

        conf_menu = wx.Menu()
        m_input = conf_menu.Append(id=wx.ID_ANY, text="Input...",
                                   help="Configure Input")
        m_video = conf_menu.Append(id=wx.ID_ANY, text="Video...",
                                   help="Configure video")
        m_sound = conf_menu.Append(id=wx.ID_ANY, text="Sound...",
                                   help="Configure sound")
        self.SetMenuBar(menu_bar)

        # Status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(1)
        # self.statusbar.SetStatusWidths([-4, -3, -2])

        # Bind events which pause/unpause emulation
        self.Bind(wx.EVT_MENU_OPEN, self.RequestPause)
        self.Bind(wx.EVT_MENU_CLOSE, self.RequestUnpause)
        self.display.Bind(wx.EVT_KILL_FOCUS, self.RequestPause)
        self.display.Bind(wx.EVT_SET_FOCUS, self.RequestUnpause)

        # Bind file menu events
        self.Bind(wx.EVT_MENU, self.Kill, m_exit)
        self.Bind(wx.EVT_MENU, self.OnLoadRom, m_load)
        menu_bar.Append(file_menu, "&File")

        # Bind options menu events
        self.Bind(wx.EVT_MENU, self.OnOptionsInput, m_input)
        self.Bind(wx.EVT_MENU, self.OnOptionsVideo, m_video)
        self.Bind(wx.EVT_MENU, self.Kill, m_sound)
        menu_bar.Append(conf_menu, "&Options")

        # Bind window behavior events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)

        # Configure layout with sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.display, 1, flag=wx.EXPAND)

        self.SetSizer(sizer)
        self.Fit()
        self.Layout()

    def RequestStop(self, event):
        pub.sendMessage("Stop Emulation")

    def RequestStart(self, event):
        pub.sendMessage("Start Emulation")

    def RequestPause(self, event):
        pub.sendMessage("Pause Emulation")

    def RequestUnpause(self, event):
        pub.sendMessage("Unpause Emulation")

    def OnLoadRom(self, event):
        dlg = wx.FileDialog(parent=self, style=wx.FD_OPEN,
                            wildcard="NES files (*.nes) | *.nes")
        if dlg.ShowModal() == wx.ID_OK:
            pub.sendMessage("Load ROM", rom_path=dlg.GetPath())
            pub.sendMessage("Start Emulation")

            # Update status bar
            self.statusbar.SetStatusText(dlg.GetFilename())
        dlg.Destroy()

    def OnOptionsInput(self, event):
        dlg = OptionsInput(parent=self, title="Input Settings")
        if dlg.ShowModal() == wx.ID_OK:
            pub.sendMessage("Push Options.Input")
        dlg.Destroy()

    def OnOptionsVideo(self, event):
        dlg = OptionsVideo(parent=self, title="Video Settings")
        if dlg.ShowModal() == wx.ID_OK:
            pub.sendMessage("Push Options.Input")
        dlg.Destroy()

    def OnSize(self, event):
        self.Layout()

    def Kill(self, event):
        pub.sendMessage("Stop Emulation")
        self.Destroy()
