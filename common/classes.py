from typing import List
from common.enums import CellType

class Cell:
    def __init__(self, hex_val: str = "F") -> None:
        self.value: int = int(hex_val, 16)
        self.n, self.e, self.s, self.w = self.hex_to_bool(self.value)
        self.type: CellType = CellType.NORMAL

    @staticmethod
    def hex_to_bool(hex_val: int) -> List[int]:
        return [
            hex_val >> 0 & 1,
            hex_val >> 1 & 1,
            hex_val >> 2 & 1,
            hex_val >> 3 & 1,
        ]
