import sys
import os
import threading
import ConfigParser
from wx.lib.pubsub import pub
from view.wx_view import *
from view.game_display import *
from view.options_dialogs import *
import nes
from utils import key_to_pykey


class EmulatorThread(threading.Thread):
    """ Thread for emulator computations """
    def __init__(self, rom_path, display):
        threading.Thread.__init__(self)
        self.daemon = True
        self.nes = nes.NES()
        self.nes.ppu.display = display
        display.nes = self.nes
        self.running = False
        self.rom_path = rom_path
        self.paused = False
        self.save = False

    def load_rom(self, rom_path):
        self.rom_path = rom_path
        with open(rom_path, 'rb') as rom:
            self.nes.load_rom(rom.read())

    def run(self):
        self.running = True
        while self.running:
            while self.paused:
                if self.save:
                    self.nes.save_state()
                    self.save = False
            self.nes.step()
        if self.save:
            self.nes.save_state()
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
    """
    def __init__(self, app):
        self.main_view = MainView(None)
        self.emu_thread = EmulatorThread(None, self.main_view.display)

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

        self.load_defaults()

        self.main_view.Show()

    def load_defaults(self):
        self.set_gamepads()

    def set_gamepads(self):
        try:
            for item in self.config.items('Gamepad 1'):
                self.main_view.display.gamepad1[item[0]] = key_to_pykey[item[1]]
        except ConfigParser.NoSectionError:
            pass
        try:
            for item in self.config.items('Gamepad 2'):
                self.main_view.display.gamepad1[item[0]] = key_to_pykey[item[1]]
        except ConfigParser.NoSectionError:
            pass

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
        self.emu_thread.load_rom(rom_path)

    def push_input_config(self):
        """ Write user changes to settings file """
        with open('settings.ini', 'wb') as configfile:
            self.config.write(configfile)
        self.set_gamepads()

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
