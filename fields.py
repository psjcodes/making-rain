from enum import StrEnum, auto


class Fields(StrEnum):
    VELOCITY = auto()
    REFLECTIVITY = auto()
    SPECTRUM_WIDTH = auto()
    DIFFERENTIAL_PHASE = auto()
    CROSS_CORRELATION_RATIO = auto()
    DIFFERENTIAL_REFLECTIVITY = auto()
