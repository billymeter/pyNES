import wx
import pygame
import sys
import os
from wx.lib.pubsub import pub


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


class OptionsInput(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.SetTitle("Input Configuration")

        # toolbar
        toolbar = self.CreateToolBar(style=wx.TB_HORIZONTAL | wx.NO_BORDER |
                                     wx.TB_FLAT | wx.TB_NODIVIDER)
        t_save = toolbar.AddLabelTool(wx.ID_APPLY, "Save",
                                      wx.Bitmap('save.png'),
                                      shortHelp="Save settings")
        t_save = toolbar.AddLabelTool(wx.ID_CANCEL, "Save",
                                      wx.Bitmap('cancel.png'),
                                      shortHelp="Cancel changes")
        toolbar.Realize()

        self.gamepad1 = wx.Button(parent=self, id=wx.ID_ANY,
                                  label="Gamepad 1", name="gamepad1")
        self.gamepad2 = wx.Button(parent=self, id=wx.ID_ANY,
                                  label="Gamepad 2", name="gamepad2")

        self.Bind(wx.EVT_BUTTON, self.OnGamepadButton, self.gamepad1)
        self.Bind(wx.EVT_BUTTON, self.OnGamepadButton, self.gamepad2)

        sizer = wx.GridSizer(rows=1, cols=2)
        sizer.Add(self.gamepad1, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.gamepad2, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.Fit()
        self.Layout()
        self.Show()

    def OnGamepadButton(self, event):
        btn = event.GetEventObject()
        pub.sendMessage("Input.Gamepad", message=btn.GetName())


class OptionsInputGamepad(wx.Frame):
    def __init__(self, parent, gamepad):
        wx.Frame.__init__(self, parent=parent, id=wx.ID_ANY,
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.parent = parent
        self.SetTitle(gamepad)
        self.SetBackgroundColour((221, 217, 206))

        # toolbar
        toolbar = self.CreateToolBar(style=wx.TB_HORIZONTAL | wx.NO_BORDER |
                                     wx.TB_FLAT | wx.TB_NODIVIDER)
        toolbar.SetBackgroundColour((221, 217, 206))
        t_save = toolbar.AddLabelTool(wx.ID_APPLY, "Save",
                                      wx.Bitmap('save.png'),
                                      shortHelp="Save settings")
        t_save = toolbar.AddLabelTool(wx.ID_CANCEL, "Save",
                                      wx.Bitmap('cancel.png'),
                                      shortHelp="Cancel changes")
        toolbar.Realize()
        self.SetClientSize((460, 166))

        # panel for dark area containing buttons
        btns = wx.Panel(self, size=(450, 156))
        btns.SetBackgroundColour((39, 44, 39))

        self.button_a = wx.Button(btns, wx.ID_ANY, "A", size=(50, 50))
        self.button_b = wx.Button(btns, wx.ID_ANY, "B", size=(50, 50))
        self.button_start = wx.Button(btns, wx.ID_ANY, "Start", size=(50, 25))
        self.button_sel = wx.Button(btns, wx.ID_ANY, "Select", size=(50, 25))
        self.button_up = wx.Button(btns, wx.ID_ANY, "Up", size=(50, 25))
        self.button_down = wx.Button(btns, wx.ID_ANY, "Down", size=(50, 25))
        self.button_left = wx.Button(btns, wx.ID_ANY, "Left", size=(50, 25))
        self.button_right = wx.Button(btns, wx.ID_ANY, "Right", size=(50, 25))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer = wx.GridSizer(rows=3, cols=7)
        sizer.Add(btns, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=15)
        empty_cell = (0, 0)

        # row 1
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_up, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)

        # row 2
        grid_sizer.Add(self.button_left, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_right, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_sel, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_start, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_b, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(self.button_a, flag=wx.ALIGN_CENTER)

        #row 3
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_down, flag=wx.ALIGN_CENTER)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(empty_cell)

        self.SetSizer(sizer)
        btns.SetSizer(grid_sizer)
        self.Layout()
        self.Show()


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

        # input submenu
        input_menu = wx.Menu()
        m_gamepad1 = input_menu.Append(wx.ID_ANY, "Gamepad 1",
                                       "Configure Gamepad 1")
        m_gamepad2 = input_menu.Append(wx.ID_ANY, "Gamepad 2",
                                       "Configure Gamepad 2")
        conf_menu.AppendMenu(wx.ID_ANY, "Input...", input_menu)

        m_video = conf_menu.Append(wx.ID_ANY, "Video...", "Configure video")
        m_sound = conf_menu.Append(wx.ID_ANY, "Sound...", "Configure sound")

        # BINDS #
        # file menu binds
        self.Bind(wx.EVT_MENU, self.Kill, m_exit)
        self.Bind(wx.EVT_MENU, self.Kill, m_load)
        menu_bar.Append(file_menu, "&File")

        # option menu binds
        self.Bind(wx.EVT_MENU, self.MenuGamepad1, m_gamepad1)
        self.Bind(wx.EVT_MENU, self.MenuGamepad2, m_gamepad2)
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

    def MenuGamepad1(self, event):
        pub.sendMessage("Input.Gamepad", gamepad_title="Gamepad 1")

    def MenuGamepad2(self, event):
        pub.sendMessage("Input.Gamepad", gamepad_title="Gamepad 2")

    def OnSize(self, event):
        self.Layout()

    def Kill(self, event):
        self.display.Kill(event)
        pygame.quit()
        self.Destroy()


class Controller(object):
    def __init__(self, app):
        # Emulator
        self.emulator = None

        # Main window
        self.main_view = MainView(None)

        # gui events
        pub.subscribe(self.OpenOptionsInput, "Options.Input")
        pub.subscribe(self.OpenGamepadConfig, "Input.Gamepad")

        self.main_view.Show()

    def OpenOptionsInput(self, unused):
        self.input_view = OptionsInput(None)
        self.input_view.Show()

    def OpenGamepadConfig(self, gamepad_title):
        self.gamepad_view = OptionsInputGamepad(None, gamepad_title)

if __name__ == "__main__":
    app = wx.App(False)
    controller = Controller(app)
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
