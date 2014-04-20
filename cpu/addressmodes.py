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
            value = op2 << 8 | op1 #cpu.memory.read(op2 << 8 | op1)
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
            return None

    class Indirect_X:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            # this addressing mode works on the zero page, so
            # wrap around
            addr = (op1 + cpu.registers['x'].read()) % 0x100
            return addr, False

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            return None

    class Indirect_Y:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
            page_crossed = False
            addr = op1 + cpu.registers['y'].read()
            if addr > (addr % 0x100):
                # page crossed
                page_crossed = True

            return addr, page_crossed

        @classmethod
        def write(self, cpu, op1, op2=None, value=0):
            return None

    class Relative:
        byte_size = 2
        @classmethod
        def read(self, cpu, op1, op2=None):
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
