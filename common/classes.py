from common.enums import CellType


class Cell:
    def __init__(self, hex_val: str = "F") -> None:
        self.value: int = int(hex_val, 16)
        self.type: CellType = CellType.NORMAL
