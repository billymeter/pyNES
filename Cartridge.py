import logging

logging.basicConfig(filename='errors.log', level=logging.ERROR)
logger = logging.getLogger(__name__)


class Cartridge(object):
    def __init__(self, nes, rom):
        self._nes = nes
        # this is a romloader for the ines format

        # check for NES constant
        if rom[0:3].decode('utf-8') != 'NES':
            logger.error("Invalid ROM file")
            raise Exception('Attempted to load an invalid ROM file')

        # check for MS-DOS EOF
        if rom[3] != 0x1a:
            logger.error("Invalid ROM file")
            raise Exception('Attempted to load an invalid ROM file')

        # size of prg rom banks in 16KB units
        self.prg_bank_count = rom[4]
        # size of chr rom banks in 8KB units
        self.chr_bank_count = rom[5]

        # set mirroring for this rom in the ppu
        if rom[6] & 0x1:
            # vertical mirroring
            self._nes.ppu.nametables.set_mirroring(1)
        else:
            # horizontal mirroring
            self._nes.ppu.nametables.set_mirroring(0)

        if (rom[6] >> 1) & 0x1:
            self.battery = True

        # The lower 4 bits of the mapper come from bits rom[6].4-7,
        # and the upper 4 bits come from rom[7].4-7.
        mapper = (rom[6] >> 4) | (rom[7] & 0xf0)

        # only nrom mapper (mapper 0) is currently supported
        if mapper != 0:
            logger.error("Unsupported memory mapper")
            raise Exception('ROM file uses unsupported memory mapper')

        self.data = rom[16:]
