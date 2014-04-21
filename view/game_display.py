import sys
import os
import wx
import pygame
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('settings.ini')

# not complete
key_to_pykey = {
    'NONE': 0,
    'BACK': 8,
    'TAB': 9,
    'CLEAR': 12,
    'RETURN': 13,
    'PAUSE': 19,
    'ESCAPE': 27,
    'SPACE': 32,
    'EXCLAIM': 33,
    'QUOTEDBL': 34,
    'HASH': 35,
    'DOLLAR': 36,
    'AMPERSAND': 38,
    'QUOTE': 39,
    'LEFTPAREN': 40,
    'RIGHTPAREN': 41,
    'ASTERISK': 42,
    'PLUS': 43,
    'COMMA': 44,
    'MINUS': 45,
    'PERIOD': 46,
    'SLASH': 47,
    '0': 48,
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,
    'COLON': 58,
    'SEMICOLON': 59,
    'LESS': 60,
    'EQUALS': 61,
    'GREATER': 62,
    'QUESTION': 63,
    'AT': 64,
    'LEFTBRACKET': 91,
    'BACKSLASH': 92,
    'RIGHTBRACKET': 93,
    'CARET': 94,
    'UNDERSCORE': 95,
    'BACKQUOTE': 96,
    'A': 97,
    'B': 98,
    'C': 99,
    'D': 100,
    'E': 101,
    'F': 102,
    'G': 103,
    'H': 104,
    'I': 105,
    'J': 106,
    'K': 107,
    'L': 108,
    'M': 109,
    'N': 110,
    'O': 111,
    'P': 112,
    'Q': 113,
    'R': 114,
    'S': 115,
    'T': 116,
    'U': 117,
    'V': 118,
    'W': 119,
    'X': 120,
    'Y': 121,
    'Z': 122,
    'DELETE': 127,
    'KP0': 256,
    'KP1': 257,
    'KP2': 258,
    'KP3': 259,
    'KP4': 260,
    'KP5': 261,
    'KP6': 262,
    'KP7': 263,
    'KP8': 264,
    'KP9': 265,
    'KP_PERIOD': 266,
    'KP_DIVIDE': 267,
    'KP_MULTIPLY': 268,
    'KP_MINUS': 269,
    'KP_PLUS': 270,
    'KP_ENTER': 271,
    'KP_EQUALS': 272,
    'UP': 273,
    'DOWN': 274,
    'RIGHT': 275,
    'LEFT': 276,
    'INSERT': 277,
    'HOME': 278,
    'END': 279,
    'PAGEUP': 280,
    'PAGEDOWN': 281,
    'F1': 282,
    'F2': 283,
    'F3': 284,
    'F4': 285,
    'F5': 286,
    'F6': 287,
    'F7': 288,
    'F8': 289,
    'F9': 290,
    'F10': 291,
    'F11': 292,
    'F12': 293,
    'F13': 294,
    'F14': 295,
    'F15': 296,
    'NUMLOCK': 300,
    'CAPSLOCK': 301,
    'SCROLLOCK': 302,
    'RSHIFT': 303,
    'LSHIFT': 304,
    'RCTRL': 305,
    'LCTRL': 306,
    'RALT': 307,
    'LALT': 308,
    'RMETA': 309,
    'LMETA': 310,
    'LSUPER': 311,
    'RSUPER': 312,
    'MODE': 313,
    'HELP': 315,
    'PRINT': 316,
    'SYSREQ': 317,
    'BREAK': 318,
    'MENU': 319,
    'POWER': 320,
    'EURO': 321,
    'LAST': 323,
    'LEFT':       276,  # left arrow
    'UP':         273,  # up arrow
    'RIGHT':      275,  # right arrow
    'DOWN':       274,  # down arrow
    'SHIFT':      303,  # SHIFT to RSHIFT :(
    'RETURN':     13
}


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
        self.size = self.GetSizeTuple()

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
                gamepad1 = config.items('Gamepad 1')
                for key in gamepad1:
                    if event.key == key_to_pykey[key[1]]:
                        pass
                        # nes.input(key_to_pykey[key[0]])
        self.Redraw()

    def Redraw(self):
        pygame.display.update()

    def NewFrame(self, buffer):
            # pygame.pixelcopy.array_to_surface(self.screen, buffer)
            pygame.surfarray.blit_array(self.screen, buffer)

    def OnPaint(self, event):
        self.Redraw()

    def OnSize(self, event):
        self.size = self.GetSizeTuple()

    def Kill(self, event):
        # Unbind methods which call Redraw() method
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
        self.Unbind(event=wx.EVT_TIMER, handler=self.Update, source=self.timer)
        pygame.quit()
