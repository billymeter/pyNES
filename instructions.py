
# Flag register bit position
C_F = 0 # Carry Flag
Z_F = 1 # Zero Flag
I_F = 2 # Interrupt enable/disable
D_F = 3 # Decimal flag (not used)
B_F = 4 # Software Interrupt (BRK)
        # The 5th bit is not used
V_F = 6 # Overflow flag
N_F = 7 # Negative flag


# set negative flag
def set_n_flag(cpu, result):
    if (result & 0x80) == 0x80:
        cpu.status[N_F] = 1
    else:
        cpu.status[N_F] = 0

# set zero flag
def set_z_flag(cpu, result):
    if result == 0:
        cpu.status[Z_F] = 1
    else:
        cpu.status[Z_F] = 0

# set carry flag
def set_c_flag(cpu, val1, val2):
    if val1 >= val2:
        cpu.status[C_F] = 1
    else:
        cpu.status[C_F] = 0

# set overflow flag
def set_v_flag(cpu, result):
    if (result & 0x100) == 0x100:
        cpu.status[V_F] = 1
    else:
        cpu.status[V_F] = 0

# add with carry - absolute
def ADC_Absolute(cpu):
    address = cpu.get_next_word()
    result = cpu.read_memory(address) + cpu.accumulator + cpu.status[C_F]
    if result > 0xFF:
        cpu.status[C_F] = 1
        cpu.status[V_F] = 1
    else:
        cpu.status[C_F] = 0
        cpu.status[V_F] = 0

    cpu.accumulator = (result & 0xFF)

    set_n_flag(cpu, result)
    set_z_flag(cpu, result)

    # this opcode grabs 3 bytes from the memory
    # so move the program counter accordingly
    cpu.program_counter += 3

    return 4

# add with carry - immediate
def ADC_Immediate(cpu):
    value = cpu.get_next_byte()
    result = value + cpu.accumulator + cpu.status[C_F]

    if result > 0xFF:
        cpu.status[C_F] = 1
        cpu.status[V_F] = 1
    else:
        cpu.status[C_F] = 0
        cpu.status[V_F] = 0

    cpu.accumulator = (result & 0xFF)

    set_n_flag(cpu, result)
    set_z_flag(cpu, result)

    # this opcode grabs 2 bytes from the memory
    # so move the program counter accordingly
    cpu.program_counter += 2

    return 2

# add with carry - zero page
def ADC_ZeroPage(cpu):
    address = cpu.get_next_byte()
    result = cpu.read_memory(address) + cpu.accumulator + cpu.status[C_F]

    if result > 0xFF:
        cpu.status[C_F] = 1
        cpu.status[V_F] = 1
    else:
        cpu.status[C_F] = 0
        cpu.status[V_F] = 0

    cpu.accumulator = (result & 0xFF)

    set_n_flag(cpu, result)
    set_z_flag(cpu, result)

    # this opcode grabs 2 bytes from the memory
    # so move the program counter accordingly
    cpu.program_counter += 2

    return 3

# logical and - absolute
def AND_Absolute(cpu):
    address = cpu.get_next_word()
    cpu.accumulator = cpu.accumulator & cpu.read_memory(address)

    set_z_flag(cpu, cpu.accumulator)
    set_n_flag(cpu, cpu.accumulator)

    # this opcode uses 3 bytes
    cpu.program_counter += 3
    return 4

# logical and - immediate
def AND_Immediate(cpu):
    value = cpu.get_next_byte()
    cpu.accumulator = cpu.accumulator & value

    set_z_flag(cpu, cpu.accumulator)
    set_n_flag(cpu, cpu.accumulator)

    # this opcode uses 2 bytes
    cpu.program_counter += 2
    return 2

# arithmetic shift left
def ASL(cpu):
    # set contents of Carry flag to bit 7 of the accumulator
    cpu.status[C_F] = (cpu.accumulator & 0x80) >> 7
    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    # and do the shift
    cpu.accumulator = cpu.accumulator << 1

    # this opcode uses 1 byte
    cpu.program_counter += 1
    return 2

# branch if carry clear
def BCC(cpu):


def BCS(cpu):

def BEQ(cpu):

# bit test
def BIT(cpu):
    address = cpu.get_next_word()
    result = cpu.accumulator & cpu.read_memory(address)
    set_z_flag(cpu, result)

    cpu.status[V_F] = (result & 0x40) >> 6
    cpu.status[N_F] = (result & 0x80) >> 7

    cpu.program_counter += 4
    return 4

def BNE(cpu):
def BPL(cpu):

# clear carry flag
def CLC(cpu):
    cpu.status[C_F] = 0
    cpu.program_counter += 2
    return 2

# clear decimal mode
def CLD(cpu):
    cpu.status[D_F] = 0
    cpu.program_counter += 1
    return 2

# compare
def CMP(cpu):
    value = cpu.get_next_byte()
    if cpu.accumulator >= value:
        cpu.status[C_F] = 1

    if cpu.accumulator == value:
        cpu.status[Z_F] = 1

    if (cpu.accumulator - value) < 0:
        cpu.status[N_F] = 1

    cpu.program_counter += 2
    return 2

# compare X register
def CPX(cpu):
    value = cpu.get_next_byte()
    if cpu.x_register >= value:
        cpu.status[C_F] = 1

    if cpu.x_register == value:
        cpu.status[Z_F] = 1

    if (cpu.x_register - value) < 0:
        cpu.status[N_F] = 1

    cpu.program_counter += 2
    return 2

# compare Y register
def CPY(cpu):
    value = cpu.get_next_byte()
    if cpu.y_register >= value:
        cpu.status[C_F] = 1

    if cpu.y_register == value:
        cpu.status[Z_F] = 1

    if (cpu.y_register - value) < 0:
        cpu.status[N_F] = 1

    cpu.program_counter += 2
    return 2

# decrement memory - absolute
def DEC_Absolute(cpu):
    address = cpu.get_next_word()
    result = cpu.read_memory(address) - 1
    cpu.write_memory(address, result)

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 3
    return 6

# decrement memory - zeropage
def DEC_ZeroPage(cpu):
    address = cpu.get_next_byte()
    result = cpu.read_memory(address) - 1
    cpu.write_memory(address, result)

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 2
    return 5

# decrement X register
def DEX(cpu):
    result = cpu.x_register - 1
    cpu.x_register = result

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 1
    return 2

# decrement Y register
def DEY(cpu):
    result = cpu.y_register - 1
    cpu.y_register = result

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 1
    return 2

# exclusive or - zero page
def EOR_ZeroPage(cpu):
    address = cpu.get_next_byte()
    result = cpu.accumulator ^ cpu.read_memory(address)
    cpu.accumulator = result

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 2
    return 3

# increment memory
def INC(cpu):
    address = cpu.get_next_word()
    result = cpu.read_memory(address) + 1
    cpu.write_memory(address, result)

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 3
    return 6

# increment memory - zero page
def INC_ZeroPage(cpu):
    address = cpu.get_next_word()
    result = cpu.read_memory(address) + 1
    cpu.write_memory(address, result)

    set_z_flag(cpu, result)
    set_n_flag(cpu, result)

    cpu.program_counter += 2
    return 5

# increment X register
def INX(cpu):
    result = cpu.x_register + 1
    cpu.x_register = result
    set_z_flag(cpu, result)
    set_n_flag(cpu, result)
    cpu.program_counter += 1
    return 2

# increment Y register
def INY(cpu):
    result = cpu.y_register + 1
    cpu.y_register = result
    set_z_flag(cpu, result)
    set_n_flag(cpu, result)
    cpu.program_counter += 1
    return 2

# jump
def JMP(cpu):
    address = cpu.get_next_word()
    cpu.program_counter = address
    return 3

# jump - indirect
def JMP_Indirect(cpu):


def JSR(cpu):

# load accumulator - absolute
def LDA_Absolute(cpu):
    address = cpu.get_next_word()
    result = cpu.read_memory(address)
    cpu.accumulator = result
    set_z_flag(cpu, result)
    set_n_flag(cpu, result)
    cpu.program_counter += 3
    return 4

# load accumlator - absolute x
def LDA_AbsoluteX(cpu):
def LDA_AbsoluteY(cpu):
def LDA_Immediate(cpu):
def LDA_IndirectY(cpu):
def LDA_ZeroPage(cpu):
def LDX_Absolute(cpu):
def LDX_AbsoluteY(cpu):
def LDX_Immediate(cpu):
def LDY_Absolute(cpu):
def LDY_Immediate(cpu):

# logical shift right - accumulator
def LSR_Accumulat(cpu):
    result = cpu.accumulator >> 1
    
    set_z_flag(cpu, result)
    cpu.status[C_F] = cpu.accumulator & 0x1
    cpu.status[N_F] = cpu.accumulator & 0x80
    
    cpu.accumulator = result
    cpu.program_counter += 1
    return 2

# logical or - immediate
def ORA_Immediate(cpu):
    value = cpu.get_next_byte()
    result = cpu.accumulator | value

    set_z_flag(cpu, result)
    cpu.status[N_F] = result & 0x80
    cpu.accumulator = result

    cpu.program_counter += 2
    return 2

# logical or - zero page
def ORA_ZeroPage(cpu):
    address = cpu.get_next_byte()
    value = cpu.read_memory(address)
    result = cpu.accumulator | value

    set_z_flag(cpu, result)
    cpu.status[N_F] = result & 0x80

    cpu.accumulator = result
    cpu.program_counter += 2
    return 3

# Push Accumulator
def PHA(cpu):
def PLA(cpu):
def ROL_Accumulat(cpu):
def ROR_AbsoluteX(cpu):
def RTI(cpu):
def RTS(cpu):
def SBC_AbsoluteY(cpu):
def SEC(cpu):
def SED(cpu):
def SEI(cpu):
def STA_Absolute(cpu):
def STA_AbsoluteX(cpu):
def STA_AbsoluteY(cpu):
def STA_IndirectY(cpu):
def STA_ZeroPage(cpu):
def STX_ZeroPage(cpu):
def STY_Absolute(cpu):
def TAX(cpu):
def TAY(cpu):
def TXA(cpu):
def TXS(cpu):
def TYA(cpu):
