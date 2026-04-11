from pathlib import Path
from typing import List, Dict, TextIO
import io
from common import Themes
from ascii_art.ThemePicker import ThemePicker


class AsciiCell:
    def __init__(self, hex_value: str) -> None:
        self.value = int(hex_value, 16)
        self.n, self.e, self.s, self.w = self.hex_to_bool(self.value)


    def display(self):
        print(f"{self.w} {self.s} {self.e} {self.n}")

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

    for line in cells_str.splitlines():
        row_cell: List[AsciiArt] = []
        for cell in line:
            row_cell.append(AsciiCell(cell))
        cells.append(row_cell)

    return cells



def print_blk(color: str, inch: int) -> None:
    DEFAULT = "\033[49m"
    print(f"{color}", " " * inch, DEFAULT, sep="", end="")


class AsciiArt:
    def __init__(self, config: str | TextIO, theme: Themes = Themes.DEFAULT) -> None:
        if isinstance(config, io.IOBase):
            config = config.read()
        if isinstance(config, str):
            self.maze: List[List[AsciiCell]] = cells_gen(config)
            self.width = len(self.maze[0])
            self.height = len(self.maze)
            self.theme: Themes = theme
        else:
            raise ValueError("The Config Must be String or File")

    def render(self):
        picker = ThemePicker(self.theme)

        CELL, READ, WALL, PAD_BG, BACKDROP, SHADOW = picker.maze_theme().values()
        PAD = 2


        # top padding
        for _ in range(0, 2):
            print_blk(PAD_BG, ((PAD * 2) * 2) + (self.width * 6) + 3)
            print()

        for h in range(0, self.height):
            for j in range(0, 3):
                print_blk(PAD_BG, PAD * 2)
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
                        print_blk(BACKDROP, 4)
                print_blk(WALL, 2)
                print_blk(SHADOW, 1)
                print_blk(PAD_BG, PAD * 2)
                print()

        print_blk(PAD_BG, PAD * 2)
        for cell in self.maze[self.height - 1]:
            print_blk(WALL, 2)
            if cell.s:
                print_blk(WALL, 4)
            else:
                print_blk(BACKDROP, 4)
        print_blk(WALL, 2)
        print_blk(SHADOW, 1)
        print_blk(PAD_BG, PAD * 2)
        print()

        # bottom badding
        print_blk(PAD_BG, PAD * 2)
        print_blk(SHADOW, (self.width * 6) + 3)
        for _ in range(0, 2):
            print_blk(PAD_BG, ((PAD * 2) * 2) + (self.width * 6) + 3)
            print()






