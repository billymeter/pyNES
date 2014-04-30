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
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = False
        self.paused = False
        self.save = False

    def load_emulator(self, rom_path, display):
        with open(rom_path, 'rb') as rom:
            self.nes = nes.NES(rom.read(), display)
        self.rom_path = rom_path
        display.nes = self.nes

    def run(self):
        import StringIO, pstats
        self.running = True
        while self.running:
            cycles = self.nes.cpu.execute()
            for i in range(3 * cycles):
                self.nes.ppu.step()
            if self.nes.ppu.frame_count == 20 and self.nes.ppu.scanline == 1:
                s = StringIO.StringIO()
                sortby = 'cumulative'
                ps = pstats.Stats(self.nes.ppu.pr, stream=s).sort_stats(sortby)
                ps.print_stats()
                print s.getvalue()

    def save_game(self):
        self.nes.save_state()


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
        self.emu_thread = EmulatorThread()

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

    def start_emulation(self, rom_path):
        """ Initialize emulation thread """
        if self.emu_thread.running:
            self.emu_thread.save_game()
            self.emu_thread.load_emulator(rom_path, self.main_view.display)
        else:
            self.emu_thread.load_emulator(rom_path, self.main_view.display)
            self.emu_thread.start()

    def stop_emulation(self):
        """ Stop emulation thread """
        self.emu_thread.running = False

    def pause_emulation(self):
        """ Pause emulation thread """
        # self.emu_thread.paused = True
        pass

    def unpause_emulation(self):
        """ Unpause emulation thread """
        self.emu_thread.paused = False

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
