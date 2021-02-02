from enum import Enum

class PositionType(Enum):
    """
    An Enum that represents a Position type in a spectrum
    """
    WAVENUMBER = 1
    WAVELENGTH = 2
    FREQUENCY = 3

class Label(Enum):
    """
    An enum that represents the label on a spectrum
    """
    BAD = 0
    GOOD = 1
    MAYBE = 2
    UNCAT = 3
