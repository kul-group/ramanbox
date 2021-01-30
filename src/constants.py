from enum import Enum

class PositionType(Enum):
    WAVENUMBER = 1
    WAVELENGTH = 2
    FREQUENCY = 3

class Label(Enum):
    BAD = 0
    GOOD = 1
    MAYBE = 2
    UNCAT = 3
