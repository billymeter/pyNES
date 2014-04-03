import wx
from wx.lib.pubsub import pub


class UserKeyDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self.SetWindowStyle(wx.SIMPLE_BORDER)
        self.SetFocus()
        self.parent = kwargs['parent']

        # Controls
        self.current_key = wx.StaticText(parent=self, label="Press key...")

        # Binds
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)

        # Sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.current_key, border=40, flag=wx.ALL)

        self.SetSizer(sizer)
        self.Fit()

    def OnKey(self, event):
        self.EndModal(event.GetKeyCode())


class GamepadInput(wx.Panel):
    def __init__(self, player, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetWindowStyle(wx.DOUBLE_BORDER)
        self.parent = kwargs['parent']
        self.player = player

        # This dictionary maps wx key codes to WXK_ constant names.
        self.key_map = {}
        for varName in vars(wx):
            if varName.startswith("WXK_"):
                self.key_map[getattr(wx, varName)] = varName

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

        # ROW 3
        grid_sizer.Add(empty_cell)
        grid_sizer.Add(self.button_down, flag=wx.ALIGN_TOP |
                       wx.ALIGN_CENTER_HORIZONTAL)
        # 5 empty cells
        grid_sizer.AddMany([empty_cell, empty_cell, empty_cell, empty_cell,
                           empty_cell])

        self.SetSizer(grid_sizer)

    def ButtonClicked(self, event):
        """ Open modal dialog to get user key """

        # We need the button object
        btn = event.GetEventObject()

        # Launch a dialog to grab a key from the user
        dlg = UserKeyDialog(parent=self, title=btn.GetLabel())

        # A WXK_ constant key code is returned
        key_code = dlg.ShowModal()

        # This is a WIP.  wx does not normally differentiate RSHIFT and LSHIFT,
        # but pygame does and we should too. dlg should listen for modifiers.
        try:
            # 'WXK_' is chopped off the front of the constant name.
            key_value = self.key_map[key_code][4:]
        except KeyError:
            try:
                key_value = unichr(key_code)
            except ValueError as e:
                with open('error.log', 'a') as error_log:
                    error_log.write(e.message + '\n')
                key_value = 'Error'
        key = (self.player, str(btn.GetName()), key_value)
        pub.sendMessage("Pending Options.Input", key=key)

        # We set the button label to key_value so the user knows they succeeded
        # (for once in their life)
        try:
            button = getattr(self, 'button_' + str(btn.GetName()))
            button.SetLabel(key_value)
        except AttributeError as e:
            with open('error.log', 'a') as error_log:
                error_log.write(e.message + '\n')


class OptionsInput(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)

        # gamepad panels
        gamepad1_name = wx.StaticText(parent=self, label="Gamepad 1")
        self.gamepad1_panel = GamepadInput(parent=self, player=1)
        gamepad2_name = wx.StaticText(parent=self, label="Gamepad 2")
        self.gamepad2_panel = GamepadInput(parent=self, player=2)

        # ok/cancel buttons
        ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)

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
