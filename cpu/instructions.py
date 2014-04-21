def ADC(cpu, mode, op1=None, op2=None):
    '''ADC'''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    c = cpu.get_status('carry')
    a = cpu.registers['a'].read()
    result = value + a + c
    overflow = (((a >> 6) & 0x1) and ((value >> 6) & 0x1) and not ((result >> 6) & 0x1) or (not ((a >> 6) & 0x1) and not ((value >> 6) & 0x1 and ((result >> 6) & 0x1))))
    print "************************************************  [DEBUG] [ADC] overflow: {} carry: {}".format(overflow, overflow)
    # cpu.registers['a'].write(result)
    # cpu.set_status('carry', overflow) #((a >> 6) & 0x1) and (result >> 7) )
    # cpu.set_status('zero', (result & 0xff) == 0)
    # cpu.set_status('overflow', overflow)
    # cpu.set_status('negative', result >> 7 & 0x1)

    cpu.set_status('negative', result & 0x80 == 0x80)
    cpu.set_status('zero', result & 0xff == 0x0)
    if ((a ^ value) & 0x80 == 0) and ((a ^ result) & 0x80 == 0x80):
        cpu.set_status('overflow', 1)
    else:
        cpu.set_status('overflow', 0)
    c2 = cpu.get_status('carry')
    cpu.set_status('carry', a + value + c2 > 0xff)

    cpu.registers['a'].write(result & 0xff)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def AND(cpu, mode, op1=None, op2=None):
    '''AND'''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()

    result = a & value
    cpu.registers['a'].write(result)

    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def ASL(cpu, mode, op1=None, op2=None):
    '''ASL'''
    value, page_crossed = mode.read(cpu, op1, op2)
    bit7 = value & 0x80
    cpu.set_status('carry', bit7)

    result = value << 1

    cpu.registers['a'].write(result)

    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    return 0 # no extra cycles

def BCC(cpu, mode, op1=None, op2=None):
    '''BCC'''
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

    if not cpu.get_status('carry'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BCS(cpu, mode, op1=None, op2=None):
    '''BCS'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    if cpu.get_status('carry') == 1:
        if page_crossed:
            extra_cycles = 2
        else:
            extra_cycles = 1

    if cpu.get_status('carry'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)

    return extra_cycles

def BEQ(cpu, mode, op1=None, op2=None):
    '''BEQ'''
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

    if cpu.get_status('zero'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BIT(cpu, mode, op1=None, op2=None):
    '''BIT'''
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()

    result = a & value
    print "                    [DEBUG] [BIT] A:{:X} value:{:X} result:{:X}".format(a, value, result)
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', value >> 7)
    cpu.set_status('overflow', (value >> 6) & 0x1 )

    return 0 # no extra cycles

def BMI(cpu, mode, op1=None, op2=None):
    '''BMI'''
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

    if cpu.get_status('negative'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BNE(cpu, mode, op1=None, op2=None):
    '''BNE'''
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

    if not cpu.get_status('zero'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BPL(cpu, mode, op1=None, op2=None):
    '''BPL'''
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

    if not cpu.get_status('negative'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BRK(cpu, mode, op1=None, op2=None):
    '''BRK'''
    raise SystemExit
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
    '''BVC'''
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

    if not cpu.get_status('overflow'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def BVS(cpu, mode, op1=None, op2=None):
    '''BVS'''
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

    if cpu.get_status('overflow'):
        pc = cpu.registers['pc'].read()
        cpu.registers['pc'].write(pc + value)
    return extra_cycles

def CLC(cpu, mode, op1=None, op2=None):
    '''CLC'''
    cpu.set_status('carry', 0)
    return 0

def CLD(cpu, mode, op1=None, op2=None):
    '''CLD'''
    cpu.set_status('decimal', 0)
    return 0

def CLI(cpu, mode, op1=None, op2=None):
    '''CLI'''
    cpu.set_status('interrupt', 0)
    return 0

def CLV(cpu, mode, op1=None, op2=None):
    '''CLV'''
    cpu.set_status('overflow', 0)
    return 0

def CMP(cpu, mode, op1=None, op2=None):
    '''CMP'''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()
    result = a - value

    cpu.set_status('carry', a >= value)
    cpu.set_status('zero', a == value)
    cpu.set_status('negative', result >> 7)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def CPX(cpu, mode, op1=None, op2=None):
    '''CPX'''
    value, page_crossed = mode.read(cpu, op1, op2)
    x = cpu.registers['x'].read()
    result = x - value

    cpu.set_status('carry', x >= value)
    cpu.set_status('zero', x == value)
    cpu.set_status('negative', result >> 7)

    return 0

def CPY(cpu, mode, op1=None, op2=None):
    '''CPY'''
    value, page_crossed = mode.read(cpu, op1, op2)
    y = cpu.registers['y'].read()
    result = y - value

    cpu.set_status('carry', y >= value)
    cpu.set_status('zero', y == value)
    cpu.set_status('negative', result >> 7)

    return 0

def DEC(cpu, mode, op1=None, op2=None):
    '''DEC'''
    value, page_crossed = mode.read(cpu, op1, op2)

    result = (value - 1) & 0xff
    mode.write(cpu, op1, op2, result)

    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)
    return 0

def DEX(cpu, mode, op1=None, op2=None):
    '''DEX'''
    value = cpu.registers['x'].read()
    value -= 1
    cpu.set_status('zero', value == 0)
    cpu.set_status('negative', value >> 7)
    cpu.registers['x'].write(value)
    return 0

def DEY(cpu, mode, op1=None, op2=None):
    '''DEY'''
    value = cpu.registers['y'].read()
    value -= 1
    cpu.set_status('zero', value == 0)
    cpu.set_status('negative', value >> 7)
    cpu.registers['y'].write(value)
    return 0

def EOR(cpu, mode, op1=None, op2=None):
    '''EOR'''
    value, page_crossed = mode.read(cpu, op1, op2)
    a = cpu.registers['a'].read()
    extra_cycles = 0

    result = (a ^ value) & 0xff
    cpu.registers['a'].write(result)
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def INC(cpu, mode, op1=None, op2=None):
    '''INC'''
    value, page_crossed = mode.read(cpu, op1, op2)

    result = (value + 1) & 0xff
    mode.write(cpu, op1, op2, result)

    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)
    return 0

def INX(cpu, mode, op1=None, op2=None):
    '''INX'''
    value = cpu.registers['x'].read()
    value += 1
    cpu.set_status('zero', (value & 0xff) == 0)
    cpu.set_status('negative', (value & 0xff) >> 7)
    cpu.registers['x'].write(value)
    return 0

def INY(cpu, mode, op1=None, op2=None):
    '''INY'''
    value = cpu.registers['y'].read()
    value += 1
    cpu.set_status('zero', (value & 0xff) == 0)
    cpu.set_status('negative', (value & 0xff) >> 7)
    cpu.registers['y'].write(value)
    return 0

def JMP(cpu, mode, op1=None, op2=None):
    '''JMP'''
    address, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['pc'].write(address)
    return 0

def JSR(cpu, mode, op1=None, op2=None):
    '''JSR'''
    address, page_crossed = mode.read(cpu, op1, op2)
    pc = cpu.registers['pc'].read()

    print " [DEBUG] [IN JSR] pc:{:04X}".format(pc)
    print " [DEBUG] [IN JSR] sp:{:04X}".format(cpu.registers['sp'].read())
    print " [DEBUG] [IN JSR - PUSHED to STACK] {:02X}{:02X}\n\n".format(pc & 0xff, pc >> 8)
    cpu.push_stack(pc & 0xff)
    cpu.push_stack(pc >> 8)

    cpu.registers['pc'].write(address)
    return 0

def LDA(cpu, mode, op1=None, op2=None):
    '''LDA'''
    value, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['a'].write(value)
    extra_cycles = 0

    print "         [DEBUG] [LDA] value:{:X} value@value:{:X}".format(value, cpu.memory.read(value))
    result = value
    cpu.set_status('zero', (result & 0xff) == 0)
    cpu.set_status('negative', (result & 0xff) >> 7)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def LDX(cpu, mode, op1=None, op2=None):
    '''LDX'''
    value, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['x'].write(value)
    extra_cycles = 0
    result = value
    cpu.set_status('zero', (result & 0xff) == 0)
    cpu.set_status('negative', (result & 0xff) >> 7)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def LDY(cpu, mode, op1=None, op2=None):
    '''LDY'''
    value, page_crossed = mode.read(cpu, op1, op2)
    cpu.registers['y'].write(value)
    extra_cycles = 0
    result = value
    cpu.set_status('zero', (result & 0xff) == 0)
    cpu.set_status('negative', (result & 0xff) >> 7)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles

def LSR(cpu, mode, op1=None, op2=None):
    '''LSR'''
    value, page_crossed = mode.read(cpu, op1, op2)

    result = (value >> 1) & 0xff
    mode.write(cpu, op1, op2, result)

    cpu.set_status('carry', value & 0x1)
    cpu.set_status('zero', (result & 0xff) == 0)
    cpu.set_status('negative', (result & 0xff) >> 7)
    return 0

def NOP(cpu, mode, op1=None, op2=None):
    '''NOP'''
    return 0

def ORA(cpu, mode, op1=None, op2=None):
    '''ORA'''
    value, page_crossed = mode.read(cpu, op1, op2)
    extra_cycles = 0

    a = cpu.registers['a'].read()

    result = a | value
    cpu.registers['a'].write(result)
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    if page_crossed:
        extra_cycles = 1
    return extra_cycles

def PHA(cpu, mode, op1=None, op2=None):
    '''PHA'''
    a = cpu.registers['a'].read()
    cpu.push_stack(a)
    return 0

def PHP(cpu, mode, op1=None, op2=None):
    '''PHP'''
    p = cpu.registers['p'].read()
    p |= 0x1 << 4
    cpu.push_stack(p)
    return 0

def PLA(cpu, mode, op1=None, op2=None):
    '''PLA'''
    result = cpu.pop_stack()

    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)
    cpu.registers['a'].write(result)
    return 0

def PLP(cpu, mode, op1=None, op2=None):
    '''PLP'''
    p = cpu.pop_stack()
    cpu.registers['p'].write(p)

    cpu.set_status('carry', p & 0x1)
    cpu.set_status('zero', p >> 1 & 0x1)
    cpu.set_status('interrupt', p >> 2 & 0x1)
    cpu.set_status('decimal', p >> 3 & 0x1)
    cpu.set_status('break', 0) # p >> 4 & 0x1)
    cpu.set_status('unused', 1)
    cpu.set_status('overflow', p >> 6 & 0x1)
    cpu.set_status('negative', p >> 7)
    return 0

def ROL(cpu, mode, op1=None, op2=None):
    '''ROL'''
    value, page_crossed = mode.read(cpu, op1, op2)
    bit7 = value >> 7
    carry = cpu.get_status('carry')
    result = (value << 1) & 0xff
    result = (result & 0xfe) | carry

    mode.write(cpu, op1, op2, result)

    cpu.set_status('carry', bit7)
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)
    return 0

def ROR(cpu, mode, op1=None, op2=None):
    '''ROR'''
    value, page_crossed = mode.read(cpu, op1, op2)
    bit0 = value & 0x1
    carry = cpu.get_status('carry')
    result = (value >> 1) & 0xff
    result = (result & 0x7f) | (carry << 7)

    mode.write(cpu, op1, op2, result)

    cpu.set_status('carry', bit0)
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)
    return 0

def RTI(cpu, mode, op1=None, op2=None):
    '''RTI'''
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
    '''RTS'''
    pc = cpu.pop_stack()
    pc = pc << 8
    pc |= cpu.pop_stack()

    cpu.registers['pc'].write(pc)
    print " [DEBUG] pc:{:04X}".format(pc)
    return 0

def SBC(cpu, mode, op1=None, op2=None):
    '''SBC'''
    extra_cycles = 0
    value, page_crossed = mode.read(cpu, op1, op2)
    c = cpu.get_status('carry')
    a = cpu.registers['a'].read()
    result = a - value - (1 - c)
    overflow = (((a >> 6) & 0x1) and ((value >> 6) & 0x1) and not ((result >> 6) & 0x1) or (not ((a >> 6) & 0x1) and not ((value >> 6) & 0x1 and ((result >> 6) & 0x1))))
    print "************************************************  [DEBUG] [SBC] overflow: {} carry: {}".format(overflow, overflow)

    cpu.set_status('negative', result & 0x80 == 0x80)
    cpu.set_status('zero', result & 0xff == 0x0)
    if ((a ^ value) & 0x80 != 0) and ((a ^ result) & 0x80 != 0):
        cpu.set_status('overflow', 1)
    else:
        cpu.set_status('overflow', 0)
    
    #cpu.set_status('overflow', value > 0x100)
    cpu.set_status('carry', result >> 8 == 0)

    cpu.registers['a'].write(result & 0xff)

    if page_crossed:
        extra_cycles = 1

    return extra_cycles
    # value, page_crossed = mode.read(cpu, op1, op2)
    # extra_cycles = 0

    # a = cpu.registers['a'].read()
    # c = cpu.get_status('carry')
    # result = a - value - (1 - c)

    # cpu.registers['a'].write(result)
    # if result < 0:
    #     cpu.set_status('carry', 0)
    #     cpu.set_status('overflow', 1)
    # cpu.set_status('zero', result == 0)
    # cpu.set_status('negative', result >> 7)

    # if page_crossed:
    #     extra_cycles = 1
    # return extra_cycles

def SEC(cpu, mode, op1=None, op2=None):
    '''SEC'''
    cpu.set_status('carry', 1)
    return 0

def SED(cpu, mode, op1=None, op2=None):
    '''SED'''
    cpu.set_status('decimal', 1)
    return 0

def SEI(cpu, mode, op1=None, op2=None):
    '''SEI'''
    cpu.set_status('interrupt', 1)
    return 0

def STA(cpu, mode, op1=None, op2=None):
    '''STA'''
    a = cpu.registers['a'].read()
    mode.write(cpu, op1, op2, a)
    return 0

def STX(cpu, mode, op1=None, op2=None):
    '''STX'''
    x = cpu.registers['x'].read()
    mode.write(cpu, op1, op2, x)
    return 0

def STY(cpu, mode, op1=None, op2=None):
    '''STY'''
    y = cpu.registers['y'].read()
    mode.write(cpu, op1, op2, y)
    return 0

def TAX(cpu, mode, op1=None, op2=None):
    '''TAX'''
    result = cpu.registers['a'].read()
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    cpu.registers['x'].write(result)
    return 0

def TAY(cpu, mode, op1=None, op2=None):
    '''TAY'''
    result = cpu.registers['a'].read()
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    cpu.registers['y'].write(result)
    return 0

def TSX(cpu, mode, op1=None, op2=None):
    '''TSX'''
    result = cpu.registers['sp'].read()
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    cpu.registers['x'].write(result)
    return 0

def TXA(cpu, mode, op1=None, op2=None):
    '''TXA'''
    result = cpu.registers['x'].read()
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    cpu.registers['a'].write(result)
    return 0

def TXS(cpu, mode, op1=None, op2=None):
    '''TXS'''
    x = cpu.registers['x'].read()
    cpu.registers['sp'].write(x)
    return 0

def TYA(cpu, mode, op1=None, op2=None):
    '''TYA'''
    result = cpu.registers['y'].read()
    cpu.set_status('zero', result == 0)
    cpu.set_status('negative', result >> 7)

    cpu.registers['a'].write(result)
    return 0
