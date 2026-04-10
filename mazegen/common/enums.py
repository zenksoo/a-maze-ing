# module for enums
from enum import Enum


class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


class Action(Enum):
    OPEN = 0
    CLOSE = 1
