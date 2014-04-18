class AddressingMode:
    class Absolute:
        byte_size = 3
        def read(cpu, op1, op2):
            value = cpu.memory.read(op2 << 8 | op1)
            return value

        def write(cpu, op1, op2, value):
            addr = op2 << 8 | op1
            cpu.memory.write(addr, value)

    class Absolute_X:
        byte_size = 3
        def read(cpu, op1, op2):
            addr = op2 << 8 | op1
            value = cpu.memory.read(addr + cpu.registers['x'].read())
            return value

        def write(cpu, op1, op2, value):
            addr = op2 << 8 | op1
            addr += cpu.registers['x'].read()
            cpu.memory.write(addr, value)

    class Absolute_Y:
        byte_size = 3
        def read(cpu, op1, op2):
            addr = op2 << 8 | op1
            value = cpu.memory.read(addr + cpu.registers['y'].read())
            return value

        def write(cpu, op1, op2, value):
            addr = op2 << 8 | op1
            addr += cpu.registers['y'].read()
            cpu.memory.write(addr, value)

    class Immediate:
        byte_size = 2
        def read(cpu, op1, op2=None):
            return op1
        def write(cpu, op1, op2=None, value):
            return None

    class Implicit:
        byte_size = 1
        def read(cpu, op1=None, op2=None):
            return None
        def write(cpu, op1=None, op2=None, value):
            return None

    class Indirect:
        byte_size = 3
        def read(cpu, op1, op2):
            addr1 = cpu.memory.read(op2 << 8 | op1)
            addr2 = cpu.memory.read((op2 << 8 | op1) + 1)
            addr = addr2 << 8 | addr1
            return addr

        def write(cpu, op1, op2, value):
            return None

    class Indirect_X:
        byte_size = 2
        def read(cpu, op1, op2=None):
            # this addressing mode works on the zero page, so
            # wrap around
            addr = (op1 + cpu.registers['x'].read()) % 0x100
        def write(cpu, op1, op2=None, value):
            return None

    class Indirect_Y:
        byte_size = 2
        def read(cpu, op1, op2=None):
        def write(cpu, op1, op2=None, value):

    class Relative:
        byte_size = 2
        def read(cpu, op1, op2=None):
            return op1
        def write(cpu, op1, op2=None, value):
            pass

    class Zero_Page:
        byte_size = 2
        def read(cpu, op1, op2=None):
        def write(cpu, op1, op2=None, value):

    class Zero_Page_X:
        byte_size = 2
        def read(cpu, op1, op2=None):
        def write(cpu, op1, op2=None, value):

    class Zero_Page_Y:
        byte_size = 2
        def read(cpu, op1, op2=None):
        def write(cpu, op1, op2=None, value):

