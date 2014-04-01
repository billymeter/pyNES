import sys
import os
from wx.lib.pubsub import pub
import ConfigParser
from view.wx_view import *


class Controller(object):
    """
    A view should pass settings and display information to this model by using
    wx.lib.pubsub.pub.sendMessage(topic, message).
    The following (topic, message) pairs are needed:
        topic                       message
        "Pending Options.Input"     (gamepad #, button name, key value)
        "Push Options.Input"        None

    Notes:
        "gamepad #" should be:
            1 or 2
        "button name" should be one of the following values:
            up, down, left, right, a, b, select, start
        "key value" should be one of the following values:
            KeyASCII     ASCII   Common Name
            BACKSPACE    \b      backspace
            TAB          \t      tab
            CLEAR                clear
            RETURN       \r      return
            PAUSE                pause
            ESCAPE       ^[      escape
            SPACE                space
            EXCLAIM      !       exclaim
            QUOTEDBL     "       quotedbl
            HASH         #       hash
            DOLLAR       $       dollar
            AMPERSAND    &       ampersand
            QUOTE                quote
            LEFTPAREN    (       left parenthesis
            RIGHTPAREN   )       right parenthesis
            ASTERISK     *       asterisk
            PLUS         +       plus sign
            COMMA        ,       comma
            MINUS        -       minus sign
            PERIOD       .       period
            SLASH        /       forward slash
            0            0       0
            1            1       1
            2            2       2
            3            3       3
            4            4       4
            5            5       5
            6            6       6
            7            7       7
            8            8       8
            9            9       9
            COLON        :       colon
            SEMICOLON    ;       semicolon
            LESS         <       less-than sign
            EQUALS       =       equals sign
            GREATER      >       greater-than sign
            QUESTION     ?       question mark
            AT           @       at
            LEFTBRACKET  [       left bracket
            BACKSLASH    \       backslash
            RIGHTBRACKE  ]       right bracket
            CARET        ^       caret
            UNDERSCORE   _       underscore
            BACKQUOTE    `       grave
            a            a       a
            b            b       b
            c            c       c
            d            d       d
            e            e       e
            f            f       f
            g            g       g
            h            h       h
            i            i       i
            j            j       j
            k            k       k
            l            l       l
            m            m       m
            n            n       n
            o            o       o
            p            p       p
            q            q       q
            r            r       r
            s            s       s
            t            t       t
            u            u       u
            v            v       v
            w            w       w
            x            x       x
            y            y       y
            z            z       z
            DELETE               delete
            KP0                  keypad 0
            KP1                  keypad 1
            KP2                  keypad 2
            KP3                  keypad 3
            KP4                  keypad 4
            KP5                  keypad 5
            KP6                  keypad 6
            KP7                  keypad 7
            KP8                  keypad 8
            KP9                  keypad 9
            KP_PERIOD    .       keypad period
            KP_DIVIDE    /       keypad divide
            KP_MULTIPLY  *       keypad multiply
            KP_MINUS     -       keypad minus
            KP_PLUS      +       keypad plus
            KP_ENTER     \r      keypad enter
            KP_EQUALS    =       keypad equals
            UP                   up arrow
            DOWN                 down arrow
            RIGHT                right arrow
            LEFT                 left arrow
            INSERT               insert
            HOME                 home
            END                  end
            PAGEUP               page up
            PAGEDOWN             page down
            F1                   F1
            F2                   F2
            F3                   F3
            F4                   F4
            F5                   F5
            F6                   F6
            F7                   F7
            F8                   F8
            F9                   F9
            F10                  F10
            F11                  F11
            F12                  F12
            F13                  F13
            F14                  F14
            F15                  F15
            NUMLOCK              numlock
            CAPSLOCK             capslock
            SCROLLOCK            scrollock
            RSHIFT               right shift
            LSHIFT               left shift
            RCTRL                right ctrl
            LCTRL                left ctrl
            RALT                 right alt
            LALT                 left alt
            RMETA                right meta
            LMETA                left meta
            LSUPER               left windows key
            RSUPER               right windows key
            MODE                 mode shift
            HELP                 help
            PRINT                print screen
            SYSREQ               sysrq
            BREAK                break
            MENU                 menu
            POWER                power
            EURO                 euro
    """
    def __init__(self, app):
        # emulator
        self.emulator = None

        # main window
        self.main_view = MainView(None)

        # emulator settings parser
        self.config = ConfigParser.ConfigParser()
        try:
            with open('settings.ini') as configfile:
                self.config.readfp(configfile)
        except IOError as e:
            with open('error.log', 'a') as error_log:
                error_log.write(e.message + '\n')

        # bind emulator data to view
        pub.subscribe(self.pull_input_config, "Pull Options.Input")
        pub.subscribe(self.push_input_config, "Push Options.Input")
        pub.subscribe(self.pending_input_config, "Pending Options.Input")

        self.main_view.Show()

    def pull_input_config(self, input_view):
        pass

    def push_input_config(self, ignored):
        """ Update with user changes to gamepad settings """
        with open('settings.ini', 'wb') as configfile:
            self.config.write(configfile)

    def pending_input_config(self, key):
        gamepad = 'Gamepad ' + str(key[0])
        button = key[1]
        key_value = key[2]

        # add section if it doesn't exist; can get rid of this after adding
        # generator for default settings file
        if not self.config.has_section(gamepad):
            self.config.add_section(gamepad)
        self.config.set(gamepad, button, key_value)


if __name__ == "__main__":
    app = wx.App(False)
    controller = Controller(app)
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
