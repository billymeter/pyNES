'''
NES CPU: Ricoh 2A05
'''

import instructions

class cpu:
    __init__(self, nes):
        # program counter
        self.program_counter = 0x0
        # stack pointer
        self.stack_pointer = 0x10
        # flag register
        self.status = [0,0,0,0,0,0,0,0]

        # general purpose registers
        self.accumlator = 0x0
        self.x_register = 0x0
        self.y_register = 0x0

        # big dictionary of NES opcodes
        self.op_codes = {
            "0xa"  : instructions.ASL,
            "0x2c" : instructions.BIT,
            "0x78" : instructions.SEI,
            "0xd8" : instructions.CLD,
            "0xa9" : instructions.LDA_Immediate,
            "0xa5" : instructions.LDA_ZeroPage,
            "0x5"  : instructions.ORA_ZeroPage,
            "0x9"  : instructions.ORA_Immediate,
            "0x10" : instructions.BPL,
            "0x18" : instructions.CLC,
            "0x8d" : instructions.STA_Absolute,
            "0x20" : instructions.JSR,
            "0x2a" : instructions.ROL_Accumulator,
            "0x38" : instructions.SEC,
            "0x3d" : instructions.AND_Absolute,
            "0x40" : instructions.RTI,
            "0x45" : instructions.EOR_ZeroPage,
            "0x48" : instructions.PHA,
            "0x4a" : instructions.LSR_Accumulator,
            "0x4c" : instructions.JMP,
            "0x29" : instructions.AND_Immediate,
            "0xa8" : instructions.TAY,
            "0xaa" : instructions.TAX,
            "0xac" : instructions.LDY_Absolute,
            "0xa2" : instructions.LDX_Immediate,
            "0xae" : instructions.LDX_Absolute,
            "0x8a" : instructions.TXA,
            "0x9a" : instructions.TXS,
            "0x99" : instructions.STA_AbsoluteY,
            "0xad" : instructions.LDA_Absolute,
            "0xa0" : instructions.LDY_Immediate,
            "0xb1" : instructions.LDA_IndirectY,
            "0xbd" : instructions.LDA_AbsoluteX,
            "0xbe" : instructions.LDX_AbsoluteY,
            "0xb9" : instructions.LDA_AbsoluteY,
            "0xc9" : instructions.CMP,
            "0xc6" : instructions.DEC_ZeroPage,
            "0xb0" : instructions.BCS,
            "0xca" : instructions.DEX,
            "0xce" : instructions.DEC_Absolute,
            "0xd0" : instructions.BNE,
            "0x6c" : instructions.JMP_Indirect,
            "0x6d" : instructions.ADC_Absolute,
            "0x69" : instructions.ADC_Immediate,
            "0x7e" : instructions.ROR_AbsoluteX,
            "0x85" : instructions.STA_ZeroPage,
            "0x86" : instructions.STX_ZeroPage,
            "0x8c" : instructions.STY_Absolute,
            "0xe0" : instructions.CPX,
            "0xe8" : instructions.INX,
            "0x90" : instructions.BCC,
            "0x91" : instructions.STA_IndirectY,
            "0x98" : instructions.TYA,
            "0x9d" : instructions.STA_AbsoluteX,
            "0x88" : instructions.DEY,
            "0xc0" : instructions.CPY,
            "0xc8" : instructions.INY,
            "0xee" : instructions.INC,
            "0xe6" : instructions.INC_ZeroPage,
            "0x60" : instructions.RTS,
            "0x65" : instructions.ADC_ZeroPage,
            "0x68" : instructions.PLA,
            "0xf0" : instructions.BEQ,
            "0xf8" : instructions.SED,
            "0xf9" : instructions.SBC_AbsoluteY
        }
