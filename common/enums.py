# module for enums
from enum import Enum


class Themes(Enum):
    DEFAULT = 0
    LAVA = 1
    SANDSTORM = 2
    MIDNIGHT_OCEAN = 3
    EMERALD_VAULT = 4
    CRIMSON = 5
    ROYAL_PURPLE = 6
    TOXIC = 7


class CellType(Enum):
    START = 0
    END = 1
    LOCED = 2
    ROAD = 3


class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


class Action(Enum):
    OPEN = 0
    CLOSE = 1
