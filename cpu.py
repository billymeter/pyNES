'''
NES CPU: Ricoh 2A05
'''

class cpu:
    # program counter
    pc = 0x0
    # stack pointer
    sp = 0x10
    # flag register
    p = 0x0

    # general purpose registers
    a = 0x0
    x = 0x0
    y = 0x0