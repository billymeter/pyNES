import wx
import pygame
import sys
import os
from wx.lib.pubsub import pub
import ConfigParser


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
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
        self.Unbind(event=wx.EVT_TIMER, handler=self.Update, source=self.timer)


class UserKeyDialog(wx.Dialog):
    def __init__(self, button, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self.SetWindowStyle(wx.SIMPLE_BORDER)
        self.SetFocus()
        self.button = button

        # Controls
        self.current_key = wx.StaticText(parent=self, label="Press key...")
        # ok_btn = wx.Button(parent=self, id=wx.ID_OK)
        # cancel_btn = wx.Button(parent=self, id=wx.ID_CANCEL)

        # Binds
        # self.Bind(wx.EVT_BUTTON, self.OnClose, ok_btn)
        # self.Bind(wx.EVT_BUTTON, self.OnClose, cancel_btn)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)

        # Sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.current_key, border=40, flag=wx.ALL)
        # button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # button_sizer.Add(ok_btn)
        # button_sizer.Add(cancel_btn)
        # sizer.Add(button_sizer, proportion=1)
        self.SetSizer(sizer)
        self.Fit()

    def OnKey(self, event):
        key = (self.button[0], self.button[1], event.GetKeyCode())
        pub.sendMessage("Pending Options.Input", key=key)
        self.Close()


class GamepadInput(wx.Panel):
    def __init__(self, gamepad, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetWindowStyle(wx.DOUBLE_BORDER)
        self.gamepad = gamepad

        # Add gamepad buttons
        self.button_up = wx.Button(parent=self, label="Up", name="up",
                                   size=(50, 25))
        self.button_left = wx.Button(parent=self, label="Left", name="left",
                                     size=(50, 25))
        self.button_right = wx.Button(parent=self, label="Right", name="right",
                                      size=(50, 25))
        self.button_select = wx.Button(parent=self, label="Select",
                                       name="select", size=(50, 25))
        self.button_start = wx.Button(parent=self, label="Start", name="start",
                                      size=(50, 25))
        self.button_b = wx.Button(parent=self, label="B", name="b",
                                  size=(50, 50))
        self.button_a = wx.Button(parent=self, label="A", name="a",
                                  size=(50, 50))
        self.button_down = wx.Button(parent=self, label="Down", name="down",
                                     size=(50, 25))

        # BINDS
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_up)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_left)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_right)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_select)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_start)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_b)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_a)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.button_down)

        # SIZER CONFIG
        grid_sizer = wx.GridSizer(rows=3, cols=7)
        empty_cell = (0, 0)

        # ROW 1
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_up, flag=wx.ALIGN_BOTTOM |
                       wx.ALIGN_CENTER_HORIZONTAL)
        # 5 empty cells
        grid_sizer.AddMany([empty_cell, empty_cell, empty_cell, empty_cell,
                           empty_cell])

        # ROW 2
        grid_sizer.Add(self.button_left, flag=wx.ALIGN_RIGHT |
                       wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_right, flag=wx.ALIGN_LEFT |
                       wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.button_select, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_start, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_b, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_a, flag=wx.ALIGN_CENTER)

        #ROW 3
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_down, flag=wx.ALIGN_TOP |
                       wx.ALIGN_CENTER_HORIZONTAL)
        # 5 empty cells
        grid_sizer.AddMany([empty_cell, empty_cell, empty_cell, empty_cell,
                           empty_cell])

        self.SetSizer(grid_sizer)

    def ButtonClicked(self, event):
        """ Open modal dialog to get user key """
        btn = event.GetEventObject()
        button = (self.gamepad, str(btn.GetName()))
        dlg = UserKeyDialog(parent=self, button=button, title=btn.GetLabel())
        dlg.ShowModal()


class OptionsInput(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)

        # gamepad panels
        gamepad1_name = wx.StaticText(parent=self, label="Gamepad 1")
        self.gamepad1_panel = GamepadInput(parent=self, gamepad=1)
        gamepad2_name = wx.StaticText(parent=self, label="Gamepad 2")
        self.gamepad2_panel = GamepadInput(parent=self, gamepad=2)

        # ok/cancel buttons
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)

        self.Bind(wx.EVT_BUTTON, self.Save, ok_btn)

        # sizer stuff
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gamepad1_name, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT)
        sizer.Add(self.gamepad1_panel, border=10,
                  flag=wx.LEFT | wx.RIGHT | wx.BOTTOM)
        sizer.Add(gamepad2_name, border=10, flag=wx.TOP | wx.LEFT | wx.RIGHT)
        sizer.Add(self.gamepad2_panel, border=10,
                  flag=wx.LEFT | wx.RIGHT | wx.BOTTOM)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddMany([ok_btn, cancel_btn])
        sizer.Add(button_sizer, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

        self.SetSizer(sizer)
        self.Fit()
        self.Layout()
        self.Show()

    def Save(self, event):
        pub.sendMessage("Push Options.Input", ignored=None)
        self.Close()


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


class ViewModel(object):
    def __init__(self, app):
        # emulator
        self.emulator = None

        # main window
        self.main_view = MainView(None)

        # utilities (should probably be factored out)
        self.config = ConfigParser.ConfigParser()
        try:
            with open('settings.ini') as configfile:
                self.config.readfp(configfile)
        except IOError:
            pass
        # need to standardize key names (wx and pygame key names differ)
        self.key_map = {}
        for varName in vars(wx):
            if varName.startswith("WXK_"):
                self.key_map[getattr(wx, varName)] = varName

        # bind emulator data to view
        pub.subscribe(self.pull_input_config, "Pull Options.Input")
        pub.subscribe(self.push_input_config, "Push Options.Input")
        pub.subscribe(self.pending_input_config, "Pending Options.Input")

        self.main_view.Show()

    def pull_input_config(self, input_view):
        """ Initialize and bind state for input views """
        pass

    def push_input_config(self, ignored):
        """ Update with user changes to gamepad settings """
        with open('settings.ini', 'wb') as configfile:
            self.config.write(configfile)

    def pending_input_config(self, key):
        gamepad = 'Gamepad ' + str(key[0])
        button = key[1]
        try:
            key_value = self.key_map[key[2]][4:]
        except KeyError:
            key_value = unichr(key[2])

        # add section if it doesn't exist; can get rid of this after adding
        # generator for default settings file
        if not self.config.has_section(gamepad):
            self.config.add_section(gamepad)
        self.config.set(gamepad, button, key_value)


if __name__ == "__main__":
    app = wx.App(False)
    ViewModel = ViewModel(app)
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
