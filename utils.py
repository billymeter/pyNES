def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def clear_bit(v, bit):
    v &= ~(1 << bit)


def set_bit(v, bit):
    v |= (1 << bit)
