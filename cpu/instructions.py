def ADC(cpu, mode, op1=None, op2=None):
    '''
    Add with carry
    '''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    value += cpu.registers['a'].read() + cpu.get_status('carry')

    cpu.set_status('carry', value > 0xff)
    cpu.registers['a'].write(value)
    cpu.set_status('zero', value & 0xff)
    cpu.set_status('overflow', value != cpu.registers['a'].read())

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def AND(cpu, mode, op1=None, op2=None):
    '''Logical AND'''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()

    result = a & value
    cpu.registers['a'].write(result)
    if (result & 0xff) == 0:
        cpu.set_status('zero', 1)
    if (result >> 7 & 0x1):
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def ASL(cpu, mode, op1=None, op2=None):
    '''Arithmetic shift left'''
    value, page_crossed = mode.read(cpu, op1, op2)
    bit7 = value & 0x80
    cpu.set_status('carry', bit7)

    value = value << 1

    cpu.registers['a'].write(value)

    if value % 0x100 == 0:
        cpu.set_status('zero', 1)
    cpu.set_status('negative', value & 0x80)

    return 0 # no extra cycles

def BCC(cpu, mode, op1=None, op2=None):
    '''Branch if carry clear'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('carry') == 0:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1
    
    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BCS(cpu, mode, op1=None, op2=None):
    '''Branch if carry set'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('carry') == 1:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1
    
    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BEQ(cpu, mode, op1=None, op2=None):
    '''Branch if equal'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('zero') == 1:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BIT(cpu, mode, op1=None, op2=None):
    '''Bit test'''
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()
    value &= a

    if value == 0:
        cpu.set_status('zero', 1)

    cpu.set_status('negative', value >> 7)
    cpu.set_status('overflow', (value >> 6) & 0x1 )

    return 0 # no extra cycles

def BMI(cpu, mode, op1=None, op2=None):
    '''Branch if minus'''
    '''Branch if equal'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('negative') == 1:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BNE(cpu, mode, op1=None, op2=None):
    '''Branch if not equal'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('zero') == 0:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BPL(cpu, mode, op1=None, op2=None):
    '''Branch if positive'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('negative') == 0:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BRK(cpu, mode, op1=None, op2=None):
    '''Force Interrupt'''
    pc = cpu.registers['pc'].read()
    print "[DEBUG] - [BRK] pc: {}".format(pc)
    cpu.push_stack(pc & 0xff)
    cpu.push_stack(pc >> 8)
    cpu.push_stack(cpu.registers['p'].read())

    irq = cpu.memory.read(0xfffe)
    irq |= cpu.memory.read(0xffff)

    cpu.registers['pc'].write(irq)
    cpu.set_status('break', 1)

    return 0

def BVC(cpu, mode, op1=None, op2=None):
    '''Branch if overflow clear'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('overflow') == 0:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BVS(cpu, mode, op1=None, op2=None):
    '''Branch if overflow set'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('overflow') == 1:
        # see if we are going into a new page
        #page = value / 0x800
        #pc = cpu.registers['pc'].read()
        #newpage = (pc + value) / 0x800

        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    pc = cpu.registers['pc'].read()
    cpu.registers['pc'].write(pc + value)
    return extra_cycles

def CLC(cpu, mode, op1=None, op2=None):
    '''Clear carry flag'''
    cpu.set_status('carry', 0)
    return 0

def CLD(cpu, mode, op1=None, op2=None):
    '''Clear decimal mode'''
    cpu.set_status('decimal', 0)
    return 0

def CLI(cpu, mode, op1=None, op2=None):
    '''Clear interrupt disable'''
    cpu.set_status('interrupt', 0)
    return 0

def CLV(cpu, mode, op1=None, op2=None):
    '''Clear overflow flag'''
    cpu.set_status('overflow', 0)
    return 0

def CMP(cpu, mode, op1=None, op2=None):
    '''Compare'''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()
    result = a - value

    if a >= value:
        cpu.set_status('carry', 1)
    if a == value:
        cpu.set_status('zero', 1)
    if (result >> 7 & 0x1):
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def CPX(cpu, mode, op1=None, op2=None):
    '''Compare X register'''
    value, page_crossed = mode.read(cpu, op1, op2)
    x = cpu.registers['x'].read()
    result = x - value

    if x >= value:
        cpu.set_status('carry', 1)
    if x == value:
        cpu.set_status('zero', 1)
    if (result >> 7 & 0x1):
        cpu.set_status('negative', 1)

    return 0

def CPY(cpu, mode, op1=None, op2=None):
    '''Compare Y register'''
    value, page_crossed = mode.read(cpu, op1, op2)
    y = cpu.registers['y'].read()
    result = y - value

    if y >= value:
        cpu.set_status('carry', 1)
    if y == value:
        cpu.set_status('zero', 1)
    if (result >> 7 & 0x1):
        cpu.set_status('negative', 1)

    return 0

def DEC(cpu, mode, op1=None, op2=None):
    '''Decrement memory'''
    value, page_crossed = mode.read(cpu, op1, op2)

    result = (value - 1) & 0xff
    mode.write(cpu, op1, op2, result)

    if result == 0:
        cpu.set_status('zero', 1)

    if result >> 7:
        cpu.set_status('negative', 1)
    return 0

def DEX(cpu, mode, op1=None, op2=None):
    '''Decrement X register'''
    value = cpu.registers['x'].read()
    cpu.registers['x'].write(value - 1)
    return 0

def DEY(cpu, mode, op1=None, op2=None):
    '''Decrement Y register'''
    value = cpu.registers['y'].read()
    cpu.registers['y'].write(value - 1)
    return 0

def EOR(cpu, mode, op1=None, op2=None):
    '''Exclusive OR'''
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()
    extra_cycles = 0

    result = (a ^ value) & 0xff
    if result == 0:
        cpu.set_status('zero', 1)
    if result >> 7:
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def INC(cpu, mode, op1=None, op2=None):
    '''Increment memory'''
    value, page_crossed = mode.read(cpu, op1, op2)

    result = (value + 1) & 0xff
    mode.write(cpu, op1, op2, result)

    if result == 0:
        cpu.set_status('zero', 1)

    if result >> 7:
        cpu.set_status('negative', 1)
    return 0

def INX(cpu, mode, op1=None, op2=None):
    '''Increment X register'''
    value = cpu.registers['x'].read()
    cpu.registers['x'].write(value + 1)
    return 0

def INY(cpu, mode, op1=None, op2=None):
    '''Increment Y register'''
    value = cpu.registers['y'].read()
    cpu.registers['y'].write(value + 1)
    return 0

def JMP(cpu, mode, op1=None, op2=None):
    '''Jump'''
    address, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['pc'].write(address)
    return 0

def JSR(cpu, mode, op1=None, op2=None):
    '''Jump to subroutine'''
    address, page_crossed = mode.read(cpu, op1, op2)
    pc = cpu.registers['pc'].read()
    print " [DEBUG] [IN JSR] sp:{:04X}".format(cpu.registers['sp'].read())

    # we want to push the next instruction to the stack, not the JSR instruction
    # again, so increment it
    pc += 3
    print " [DEBUG] [IN JSR] pc:{:04X}".format(pc)
    cpu.push_stack(pc & 0xff)
    cpu.push_stack(pc >> 8)

    cpu.registers['pc'].write(address)
    return 0

def LDA(cpu, mode, op1=None, op2=None):
    '''Load accumulator'''
    value, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['a'].write(value)
    extra_cycles = 0

    if value == 0:
        cpu.set_status('zero', 1)
    if value >> 7 == 1:
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def LDX(cpu, mode, op1=None, op2=None):
    '''Load X register'''
    value, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['x'].write(value)
    extra_cycles = 0

    if value == 0:
        cpu.set_status('zero', 1)
    if value >> 7 == 1:
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def LDY(cpu, mode, op1=None, op2=None):
    '''Load Y register'''
    value, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['y'].write(value)
    extra_cycles = 0

    if value == 0:
        cpu.set_status('zero', 1)
    if value >> 7 == 1:
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def LSR(cpu, mode, op1=None, op2=None):
    '''Logical Shift Right'''
    value, page_crossed = mode.read(cpu, op1, op2)

    result = (value >> 1) & 0xff
    mode.write(cpu, op1, op2, result)

    cpu.set_status('carry', value & 0x1)
    if value == 0:
        cpu.set_status('zero', 1)
    if value >> 7:
        cpu.set_status('negative', 1)
    return 0

def NOP(cpu, mode, op1=None, op2=None):
    '''No operation'''
    return 0

def ORA(cpu, mode, op1=None, op2=None):
    '''Logical Inclusive OR'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    a = cpu.registers['a'].read()

    result = a | value
    if result == 0:
        cpu.set_status('zero', 1)
    if result >> 7:
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1
    return extra_cycles

def PHA(cpu, mode, op1=None, op2=None):
    '''Push accumulator'''
    a = cpu.registers['a'].read()
    cpu.push_stack(a)
    return 0

def PHP(cpu, mode, op1=None, op2=None):
    '''Push processor status'''
    p = cpu.registers['p'].read()
    cpu.push_stack(p)
    return 0

def PLA(cpu, mode, op1=None, op2=None):
    '''Pull accumulator'''
    a = cpu.pop_stack()

    if a == 0:
        cpu.set_status('zero', 1)
    if a >> 7:
        cpu.set_status('negative', 1)
    cpu.registers['a'].write(a)
    return 0

def PLP(cpu, mode, op1=None, op2=None):
    '''Pull processor status'''
    p = cpu.pop_stack()
    cpu.registers['p'].write(p)

    cpu.set_status('carry', p & 0x1)
    cpu.set_status('zero', p >> 1 & 0x1)
    cpu.set_status('interrupt', p >> 2 & 0x1)
    cpu.set_status('decimal', p >> 3 & 0x1)
    cpu.set_status('break', p >> 4 & 0x1)

    cpu.set_status('overflow', p >> 6 & 0x1)
    cpu.set_status('negative', p >> 7)
    return 0

def ROL(cpu, mode, op1=None, op2=None):
    '''Rotate Left'''
    value, page_crossed = mode.read(cpu, op1, op2)
    bit7 = value >> 7
    carry = cpu.get_status('carry')
    result = (value << 1) & 0xff
    result = (result & 0xfe) | carry

    mode.write(cpu, op1, op2, result)

    cpu.set_status('carry', bit7)
    if result == 0:
        cpu.set_status('zero', 1)
    if result >> 7:
        cpu.set_status('negative', 1)
    return 0

def ROR(cpu, mode, op1=None, op2=None):
    '''Rotate Right'''
    value, page_crossed = mode.read(cpu, op1, op2)
    bit0 = value & 0x1
    carry = cpu.get_status('carry')
    result = (value >> 1) & 0xff
    result = (result & 0x7f) | (carry << 7)

    mode.write(cpu, op1, op2, result)

    cpu.set_status('carry', bit0)
    if result == 0:
        cpu.set_status('zero', 1)
    if result >> 7:
        cpu.set_status('negative', 1)
    return 0

def RTI(cpu, mode, op1=None, op2=None):
    '''Return from interrupt'''
    p = cpu.pop_stack()
    pc = cpu.pop_stack()
    pc = pc << 8
    pc |= cpu.pop_stack()

    cpu.registers['p'].write(p)
    cpu.registers['pc'].write(pc)

    cpu.set_status('carry', p & 0x1)
    cpu.set_status('zero', p >> 1 & 0x1)
    cpu.set_status('interrupt', p >> 2 & 0x1)
    cpu.set_status('decimal', p >> 3 & 0x1)
    cpu.set_status('break', p >> 4 & 0x1)

    cpu.set_status('overflow', p >> 6 & 0x1)
    cpu.set_status('negative', p >> 7)

    return 0

def RTS(cpu, mode, op1=None, op2=None):
    '''Return from subroutine'''
    pc = cpu.pop_stack()
    pc = pc << 8
    pc |= cpu.pop_stack()

    cpu.registers['pc'].write(pc)

    return 0

def SBC(cpu, mode, op1=None, op2=None):
    '''Subtract with carry'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    a = cpu.registers['a'].read()
    c = cpu.get_status('carry')
    result = a - value - (1 - c)

    cpu.registers['a'].write(result)
    if result < 0:
        cpu.set_status('carry', 0)
        cpu.set_status('overflow', 1)
    if result == 0:
        cpu.set_status('zero', 1)
    if (result & 0xff) >> 7:
        cpu.set_status('negative', 1)

    if page_crossed:
        extra_cycles = 1
    return extra_cycles

def SEC(cpu, mode, op1=None, op2=None):
    '''Set Carry flag'''
    cpu.set_status('carry', 1)
    return 0

def SED(cpu, mode, op1=None, op2=None):
    '''Set decimal flag'''
    cpu.set_status('decimal', 1)
    return 0

def SEI(cpu, mode, op1=None, op2=None):
    '''Set interrupt disable'''
    cpu.set_status('interrupt', 1)
    return 0

def STA(cpu, mode, op1=None, op2=None):
    '''Store accumulator'''
    a = cpu.registers['a'].read()
    mode.write(cpu, op1, op2, a)
    return 0

def STX(cpu, mode, op1=None, op2=None):
    '''Store X register'''
    x = cpu.registers['x'].read()
    mode.write(cpu, op1, op2, x)
    return 0

def STY(cpu, mode, op1=None, op2=None):
    '''Store Y register'''
    y = cpu.registers['y'].read()
    mode.write(cpu, op1, op2, y)
    return 0

def TAX(cpu, mode, op1=None, op2=None):
    '''Transfer accumulator to X'''
    a = cpu.registers['a'].read()
    if a == 0:
        cpu.set_status('zero', 1)
    if a >> 7:
        cpu.set_status('negative', 1)

    cpu.registers['x'].write(a)
    return 0

def TAY(cpu, mode, op1=None, op2=None):
    '''Transfer accumulator to Y'''
    a = cpu.registers['a'].read()
    if a == 0:
        cpu.set_status('zero', 1)
    if a >> 7:
        cpu.set_status('negative', 1)

    cpu.registers['y'].write(a)
    return 0

def TSX(cpu, mode, op1=None, op2=None):
    '''Transfer stack pointer to X'''
    sp = cpu.registers['sp'].read()
    if sp == 0:
        cpu.set_status('zero', 1)
    if sp >> 7:
        cpu.set_status('negative', 1)

    cpu.registers['x'].write(sp)
    return 0

def TXA(cpu, mode, op1=None, op2=None):
    '''Transfer X to accumulator'''
    x = cpu.registers['x'].read()
    if x == 0:
        cpu.set_status('zero', 1)
    if x >> 7:
        cpu.set_status('negative', 1)

    cpu.registers['a'].write(x)
    return 0

def TXS(cpu, mode, op1=None, op2=None):
    '''Transfer X to stack pointer'''
    x = cpu.registers['x'].read()
    cpu.registers['sp'].write(x)
    return 0

def TYA(cpu, mode, op1=None, op2=None):
    '''Transfer Y to accumulator'''
    y = cpu.registers['y'].read()
    if y == 0:
        cpu.set_status('zero', 1)
    if y >> 7:
        cpu.set_status('negative', 1)

    cpu.registers['a'].write(y)
    return 0
