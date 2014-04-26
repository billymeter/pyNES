import logging
import struct

logging.basicConfig(filename='errors.log', level=logging.ERROR)
logger = logging.getLogger(__name__)


def frombyte(byte):
    return struct.unpack('b', byte)[0]


class Cartridge(object):
    def __init__(self, nes, rom):
        self._nes = nes
        # this is a romloader for the ines format

        # check for NES constant
        if rom[0:3].decode('utf-8') != 'NES':
            logger.error("Invalid ROM file")
            raise Exception('Attempted to load an invalid ROM file')

        # check for MS-DOS EOF
        if struct.unpack('b', rom[3])[0] != 0x1a:
            logger.error("Invalid ROM file")
            raise Exception('Attempted to load an invalid ROM file')

        # size of prg rom banks in 16KB units
        self.prg_bank_count = frombyte(rom[4])
        # size of chr rom banks in 8KB units
        self.chr_bank_count = frombyte(rom[5])

        # set mirroring for this rom in the ppu
        if frombyte(rom[6]) & 0x1:
            # vertical mirroring
            self._nes.ppu.vram.nametable.set_mirroring('Vertical')
        else:
            # horizontal mirroring
            self._nes.ppu.vram.nametable.set_mirroring('Horizontal')

        if (frombyte(rom[6]) >> 1) & 0x1:
            self.battery = True

        self.data = rom[16:]

        # The lower 4 bits of the mapper come from bits rom[6].4-7,
        # and the upper 4 bits come from rom[7].4-7.
        mapper = (frombyte(rom[6]) >> 4) | (frombyte(rom[7]) & 0xf0)

        # only nrom mapper (mapper 0) is currently supported
        if mapper == 0:
            self.load_nrom()
        else:
            logger.error("Unsupported memory mapper")
            raise Exception("Unsupported memory mapper")

    def load_nrom(self):
        self.prg_banks = [[] for i in range(self.prg_bank_count)]

        # add prg banks from data
        for i in range(self.prg_bank_count):
            bank = [0] * 0x4000
            for offset in range(0x4000):
                bank[offset] = frombyte(self.data[(0x4000 * i) + offset])
            self.prg_banks[i] = bank
        # with open('prgdump.txt', 'w') as out:
        #     for bank in self.prg_banks:
        #         for byte in bank:
        #             out.write(byte)

        # add chr banks from data (they're after prg banks)
        chr_rom = self.data[0x4000 * len(self.prg_banks):]

        if self.chr_bank_count > 0:
            self.chr_banks = [[] for i in range(self.chr_bank_count)*2]
        else:
            self.chr_banks = [[], []]

        for i in range(len(self.chr_banks)):
            bank = [0] * 0x1000

            if self.chr_bank_count > 0:
                for offset in range(0x1000):
                    bank[offset] = frombyte(chr_rom[(0x1000 * i) + offset])
            self.chr_banks[i] = bank
        # with open('chrdump.txt', 'w') as out:
        #     for bank in self.chr_banks:
        #         for byte in bank:
        #             out.write(byte)

    def read_prg(self, address):
        offset = address & 0x3fff
        if address >= 0xc000:
            return self.prg_banks[len(self.prg_banks)-1][offset]

        return self.prg_banks[0][offset]

    def read_chr(self, address):
        offset = address & 0xfff
        if address >= 0x1000:
            return self.chr_banks[len(self.chr_banks)-1][offset]

        return self.chr_banks[0][offset]

    def write_chr(self, address, value):
        if address >= 0x1000:
            self.chr_banks[len(self.chr_banks)-1][address & 0xfff] = value
            return

        self.chr_banks[0][address & 0xfff] = value

    def read_tile(self, address):
        offset = address & 0xfff
        if address >= 0x1000:
            return self.chr_banks[len(self.chr_banks)-1][offset:offset + 16]

        return self.chr_banks[0][offset:offset + 16]
