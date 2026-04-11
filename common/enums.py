# module for enums
from enum import Enum

class Themes(Enum):
    DEFAULT = 0
    LAVA = 1
    SANDSTORM = 2
    MIDNIGHT_OCEAN = 3
    EMERALD_VAULT = 4
    CRIMSON_NIGHT = 5

class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


class Action(Enum):
    OPEN = 0
    CLOSE = 1
