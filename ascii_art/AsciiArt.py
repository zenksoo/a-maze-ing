from typing import List, TextIO
import io
from common import Themes, CellType
from ascii_art.ThemePicker import ThemePicker


class AsciiCell:
    def __init__(self, hex_value: str) -> None:
        self.value = int(hex_value, 16)
        self.n, self.e, self.s, self.w = self.hex_to_bool(self.value)
        self.type: CellType = None

    @staticmethod
    def hex_to_bool(hex_val: int) -> List[int]:
        return [
            hex_val >> 0 & 1,
            hex_val >> 1 & 1,
            hex_val >> 2 & 1,
            hex_val >> 3 & 1,
        ]


def cells_gen(cells_str: str) -> List[List[AsciiCell]]:
    cells: List[List[AsciiCell]] = []
    locations: List[tuple] = []
    road: str = None

    for line in cells_str.splitlines():
        row_cell: List[AsciiArt] = []
        if "," in line:
            locations.append(tuple(map(int, line.split(",")),))
        elif any(c in "NSW" for c in line):
            road = line
        elif line:
            for cell in line:
                row_cell.append(AsciiCell(cell))
            cells.append(row_cell)

    start, end = locations

    path = list(start)
    for blk in road:
        if blk == "S":
            path[1] += 1
        elif blk == "N":
            path[1] -= 1
        elif blk == "E":
            path[0] += 1
        elif blk == "W":
            path[0] -= 1
        cells[path[1]][path[0]].type = CellType.ROAD

    cells[start[1]][start[0]].type = CellType.START
    cells[end[1]][end[0]].type = CellType.END
    return cells


def print_blk(color: str, inch: int) -> None:
    DEFAULT = "\033[49m"
    print(f"{color}", " " * inch, DEFAULT, sep="", end="")


class AsciiArt:
    def __init__(self, config: str | TextIO,
                 theme: Themes = Themes.MIDNIGHT_OCEAN) -> None:
        if isinstance(config, io.IOBase):
            config = config.read()
        if isinstance(config, str):
            self.maze: List[List[AsciiCell]] = cells_gen(config)
            self.width = len(self.maze[0])
            self.height = len(self.maze)
            self.theme: Themes = theme
        else:
            raise ValueError("The Config Must be String or File")

    def render(self, show_path: bool = False):
        picker = ThemePicker(self.theme)
        maze_theme = picker.maze_theme().values()
        CELL, ROAD, WALL, PADDING, BACKDROP, SHADOW = maze_theme
        ENTRY, EXIT = picker.locations_theme().values()
        PAD = 2

        # top padding
        for _ in range(0, 2):
            print_blk(PADDING, ((PAD * 4) * 2) + (self.width * 6) + 3)
            print()

        for h in range(0, self.height):
            for j in range(0, 3):
                print_blk(PADDING, PAD * 4)
                for w in range(0, self.width):
                    cell = self.maze[h][w]
                    if j == 0:
                        print_blk(WALL, 2)
                        if cell.n:
                            print_blk(WALL, 4)
                        else:
                            print_blk(BACKDROP, 4)
                    else:
                        if cell.w:
                            print_blk(WALL, 2)
                        else:
                            print_blk(BACKDROP, 2)
                        if cell.type == CellType.START:
                            print_blk(ENTRY, 4)
                        elif cell.type == CellType.END:
                            print_blk(EXIT, 4)
                        elif cell.type == CellType.ROAD and show_path:
                            print_blk(ROAD, 4)
                        elif cell.n and cell.e and cell.s and cell.w:
                            print_blk(CELL, 4)
                        else:
                            print_blk(BACKDROP, 4)
                print_blk(WALL, 2)
                print_blk(SHADOW, 1)
                print_blk(PADDING, PAD * 4)
                print()

        print_blk(PADDING, PAD * 4)
        for cell in self.maze[self.height - 1]:
            print_blk(WALL, 2)
            if cell.s:
                print_blk(WALL, 4)
            else:
                print_blk(BACKDROP, 4)
        print_blk(WALL, 2)
        print_blk(SHADOW, 1)
        print_blk(PADDING, PAD * 4)
        print()

        # bottom badding
        print_blk(PADDING, PAD * 4)
        print_blk(SHADOW, (self.width * 6) + 3)
        print_blk(PADDING, PAD * 4)
        print()
        for _ in range(0, 2):
            print_blk(PADDING, ((PAD * 4) * 2) + (self.width * 6) + 3)
            print()
