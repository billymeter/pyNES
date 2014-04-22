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
            value = cpu.memory.read(addr + cpu.registers['x'].read())
            if addr > (value % 0x100):
                # crossed a page
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
            value = cpu.memory.read(addr + cpu.registers['y'].read())
            if addr > (value % 0x100):
                # crossed a page
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
            addr1 = cpu.memory.read(op2 << 8 | op1)
            addr2 = cpu.memory.read((op2 << 8 | op1) + 1)
            addr = addr2 << 8 | addr1
            return addr

        @classmethod
        def write(self, cpu, op1, op2, value):
            addr1 = cpu.memory.read(op2 << 8 | op1)
            addr2 = cpu.memory.read((op2 << 8 | op1) + 1)
            addr = addr2 << 8 | addr1
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
            #print "[DEBUG] [INDIRECT_X READ] addr:{:X} value:{:X} pc:{:X}".format(addr, cpu.memory.read(addr), cpu.registers['pc'].read() - self.byte_size)
            #print "[DEBUG] [INDR_X] value at 0x0400:{:X}".format(cpu.memory.read(0x0400))
            return cpu.memory.read(addr), False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            indir_addr = (op1 + cpu.registers['x'].read()) % 0xff
            addr = cpu.memory.read(indir_addr)
            if op1==0xff:
                addr = addr << 8
            else:
                addr += (cpu.memory.read((indir_addr + 1) & 0xff) << 8)
            cpu.memory.write(addr, value)
            return None

    class Indirect_Y:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            page_crossed = False
            addr = cpu.memory.read(op1) & 0xff
            addr += ((cpu.memory.read(op1 + 1) & 0xff) << 8)
            y = cpu.registers['y'].read()

            # if cpu.get_status('negative'):
            #     y = (y ^ 0xff) + 1
            #     y *= -1

            if addr > (addr % 0x800):
                # page crossed
                page_crossed = True

            print "[DEBUG] addr:{:X}".format((addr+y))
            result = cpu.memory.read((addr+y)&0xfff)

            if (cpu.registers['pc'].read() - self.byte_size) == 0xd959:
                f=open("memdump","wb")
                f.write(cpu.memory._memory)
                f.close()
            
            #print "        [INDR_Y] value at read(read():{:X}".format(cpu.memory.read(cpu.memory.read(addr)))
            return result, page_crossed

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            page_crossed = False
            addr = cpu.memory.read(op1)
            addr += (cpu.memory.read(op1 + 1) << 8)
            if addr > (addr % 0x100):
                # page crossed
                page_crossed = True
            y = cpu.registers['y'].read()
            cpu.memory.write((addr + y) & 0xff, value)
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
