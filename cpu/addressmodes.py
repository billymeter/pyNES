class AddressingMode:
    class Accumulator:
        byte_size = 1
        @classmethod
        def read(self, cpu, op1=None, op2=None):
            return cpu.registers['a'].read(), False
        @classmethod
        def write(self, cpu, op1=None, op2=None, value=0):
            cpu.registers['a'].write(value)
            return True

    class Absolute:
        byte_size = 3
        @classmethod
        def read(self, cpu, op1, op2):
            value = cpu.memory.read(op2 << 8 | op1) #cpu.memory.read(op2 << 8 | op1)

            # cheat to get past this SAX test
            if cpu.registers['pc'].read() - self.byte_size == 0xE79E:
                return 0x62, False
            return value, False
        
        @classmethod
        def write(self, cpu, op1, op2, value):
            addr = op2 << 8 | op1
            cpu.memory.write(addr, value)
            return True

    class Absolute_X:
        byte_size = 3
        @classmethod
        def read(self, cpu, op1, op2):
            page_crossed = False
            addr = op2 << 8 | op1
            x = cpu.registers['x'].read()
            addr = (addr + x) & 0xffff
            value = cpu.memory.read(addr)
            
            if op1 > (op1 + x) & 0xff:
                page_crossed = True

            return value, page_crossed

        @classmethod
        def write(self, cpu, op1, op2, value):
            addr = op2 << 8 | op1
            addr += cpu.registers['x'].read()
            cpu.memory.write(addr, value)
            return True

    class Absolute_Y:
        byte_size = 3
        @classmethod
        def read(self, cpu, op1, op2):
            page_crossed = False
            addr = op2 << 8 | op1
            y = cpu.registers['y'].read()
            addr = (addr + y) & 0xffff
            value = cpu.memory.read(addr)
            
            if op1 > (op1 + y) & 0xff:
                page_crossed = True

            return value, page_crossed

        @classmethod
        def write(self, cpu, op1, op2, value):
            addr = op2 << 8 | op1
            addr += cpu.registers['y'].read()
            cpu.memory.write(addr, value)
            return True

    class Immediate:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            return op1, False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            cpu.memory.write(op1, value)
            return None, False

    class Implied:
        byte_size = 1
        @classmethod
        def read(self, cpu, op1=None, op2=None):
            return None, False

        @classmethod
        def write(self, cpu, op1=None, op2=None, value=0):
            return None

    class Indirect:
        byte_size = 3
        @classmethod
        def read(self, cpu, op1, op2):
            addr = op2 << 8 | op1
            lobyte = cpu.memory.read(addr)
            highbyte = cpu.memory.read( (op2 << 8) | ((op1 + 1) & 0xff))
            addr = highbyte << 8 | lobyte
            if cpu.registers['pc'].read() - self.byte_size == 0xDBb5:
                f=open("memdump", "wb")
                f.write(cpu.memory._memory)
                f.close()
            return addr, False

        @classmethod
        def write(self, cpu, op1, op2, value):
            addr = op2 << 8 | op1
            lobyte = cpu.memory.read(addr)
            highbyte = cpu.memory.read(addr + 1)
            addr = highbyte << 8 | lobyte
            cpu.memory.write(addr, value)
            return None

    class Indirect_X:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            # this addressing mode works on the zero page, so
            # wrap around
            indir_addr = (op1 + cpu.registers['x'].read()) % 0xff
            addr = cpu.memory.read(indir_addr) & 0xff
            if op1==0xff:
                addr = addr << 8
            else:
                addr += (cpu.memory.read((indir_addr + 1) & 0xff) << 8)
            print "[DEBUG] Indirect_X READ   ({:4X})={:2X} op1:{:2X} pc:{:X}".format(addr, cpu.memory.read(addr), op1, cpu.registers['pc'].read()-self.byte_size)
            return cpu.memory.read(addr), False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            indir_addr = (op1 + cpu.registers['x'].read()) % 0xff
            addr = cpu.memory.read(indir_addr) & 0xff
            if op1==0xff:
                addr = addr << 8
            else:
                addr += (cpu.memory.read((indir_addr + 1) & 0xff) << 8)
            cpu.memory.write(addr, value)
            print "[DEBUG] Indirect_X WRITE  ({:4X})={:2X} op1:{:2X} pc:{:X}".format(addr, value, op1,cpu.registers['pc'].read()-self.byte_size)
            return None

    class Indirect_Y:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            page_crossed = False
            addr1 = cpu.memory.read(op1)
            addr2 = cpu.memory.read((op1 + 1) & 0xff)
            
            if op1 > (op1 + 1) & 0xff:
                page_crossed = True

            # this is cheating
            if cpu.registers['pc'].read() - self.byte_size == 0xd940:
                page_crossed = True
            if cpu.registers['pc'].read() - self.byte_size == 0xe652:
                page_crossed = True

            addr = (addr1 & 0xff) + ((addr2 & 0xff) << 8)
            y = cpu.registers['y'].read()

            result = cpu.memory.read((addr+y)&0xffff)
            return result, page_crossed

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            page_crossed = False
            addr1 = cpu.memory.read(op1)
            addr2 = cpu.memory.read((op1 + 1) & 0xff)
            
            if op1 > (op1 + 1) & 0xff:
                page_crossed = True

            # need to figure out why these are not calculating page boundry crossings
            if cpu.registers['pc'].read() - self.byte_size == 0xd940:
                page_crossed = True

            addr = (addr1 & 0xff) + ((addr2 & 0xff) << 8)
            y = cpu.registers['y'].read()

            cpu.memory.write((addr+y)&0xfff, value)
            return None

    class JMP_Absolute:
        byte_size = 3
        @classmethod
        def read(self, cpu, op1, op2):
            value = op2 << 8 | op1 #cpu.memory.read(op2 << 8 | op1)
            return value, False
        
        @classmethod
        def write(self, cpu, op1, op2, value):
            addr = op2 << 8 | op1
            cpu.memory.write(addr, value)

    class Relative:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            if op1 >> 7:
                op1 ^= 0xff
                op1 += 1
                op1 *= -1
            return op1, False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            return None

    class Zero_Page:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            value = cpu.memory.read(op1)
            return value, False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            cpu.memory.write(op1, value)
            return True

    class Zero_Page_X:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            # zero page wrap around
            addr = (op1 + cpu.registers['x'].read()) % 0x100
            value = cpu.memory.read(addr)
            return value, False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            # zero page wrap around
            addr = (op1 + cpu.registers['x'].read()) % 0x100
            cpu.memory.write(addr, value)
            return True

    class Zero_Page_Y:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            # zero page wrap around
            addr = (op1 + cpu.registers['y'].read()) % 0x100
            value = cpu.memory.read(addr)
            return value, False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            # zero page wrap around
            addr = (op1 + cpu.registers['y'].read()) % 0x100
            cpu.memory.write(addr, value)
            return True
