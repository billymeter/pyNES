import sys
import os
import threading
import ConfigParser
from wx.lib.pubsub import pub
from view.wx_view import *
from view.pygame_display import *
import nes


class EmulatorThread(threading.Thread):
    """ Thread for emulator computations """
    def __init__(self, rom_path):
        threading.Thread.__init__(self)
        self.emulator = nes.NES()
        self.running = False
        self.rom_path = rom_path
        self.paused = False
        self.save = False

        with open(rom_path, 'rb') as rom:
            self.emulator.load_rom(rom)

    def run(self):
        self.running = True
        while self.running:
            while self.paused:
                if self.save:
                    self.emulator.save_state()
                    self.save = False
            self.emulator.step()
        if self.save:
            self.emulator.save_state()
            self.save = False


class Controller(object):
    """
    The GUI should pass settings and display information to this model by using
    wx.lib.pubsub.pub.sendMessage(topic, message).
    The following (topic, message) pairs are needed:
        topic                       message
        "Load ROM"                  '/path/to/ROM'
        "Pending Options.Input"     (player, button name, key value)
        "Push Options.Input"        None

    Notes:
        "player" should be:
            1 or 2
        "button name" should be one of the following values:
            up, down, left, right, a, b, select, start
        "key value" should be one of the following KeyASCII values:
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
        self.emu_thread = EmulatorThread(None)
        self.main_view = MainView(None)

        # Emulator config parser
        self.config = ConfigParser.ConfigParser()
        try:
            with open('settings.ini') as configfile:
                self.config.readfp(configfile)
        except IOError as e:
            with open('error.log', 'a') as error_log:
                error_log.write(e.message + '\n')

        # Assign emulation start/stop listeners
        pub.subscribe(self.start_emulation, "Start Emulation")
        pub.subscribe(self.stop_emulation, "Stop Emulation")
        pub.subscribe(self.pause_emulation, "Pause Emulation")
        pub.subscribe(self.unpause_emulation, "Unpause Emulation")

        # Assign emulation state-config listeners
        pub.subscribe(self.load_rom, "Load ROM")
        pub.subscribe(self.push_input_config, "Push Options.Input")
        pub.subscribe(self.pending_input_config, "Pending Options.Input")

        self.main_view.Show()

    def start_emulation(self):
        """ Initialize emulation thread """
        if self.emu_thread.rom_path:
            self.emu_thread.start()
        else:
            with open('error.log', 'a') as error_log:
                error_log.write('Tried to start emulation before ROM loaded\n')

    def stop_emulation(self):
        """ Stop emulation thread """
        self.emu_thread.running = False

    def pause_emulation(self):
        """ Pause emulation thread """
        self.emu_thread.paused = True

    def unpause_emulation(self):
        """ Unpause emulation thread """
        self.emu_thread.paused = False

    def load_rom(self, rom_path):
        """ Give ROM path to emulator """
        self.emu_thread.rom_path = rom_path

    def push_input_config(self):
        """ Write user changes to settings file """
        with open('settings.ini', 'wb') as configfile:
            self.config.write(configfile)

    def pending_input_config(self, key):
        """ Write pending changes to config parser without writing to file """
        gamepad = 'Gamepad ' + str(key[0])
        button = key[1]
        key_value = key[2]

        # add section if it doesn't exist; can get rid of this after providing
        # a default settings file
        if not self.config.has_section(gamepad):
            self.config.add_section(gamepad)
        self.config.set(gamepad, button, key_value)


if __name__ == "__main__":
    """ main """
    app = wx.App(False)
    controller = Controller(app)
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
