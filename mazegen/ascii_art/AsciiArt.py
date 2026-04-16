from typing import List, TextIO
from mazegen.MazeCell import MazeCell
from .ThemePicker import ThemePicker
from mazegen.edit_cell_type import *
import sys
import io


SAVE_CURSOR = "\033[s"
RESTORE_CURSOR = "\033[u"
CLEAR_LINE = "\033[K"
CLEAR_DOWN = "\033[J"


def cells_gen(cells_str: str) -> List[List[MazeCell]]:
    cells: List[List[MazeCell]] = []
    locations: List[tuple] = []
    road: str = None

    x = y = 0
    for line in cells_str.splitlines():
        row_cell: List[MazeCell] = []
        if "," in line:
            locations.append(tuple(map(int, line.split(","))))
        elif any(c in "NSW" for c in line):
            road = line
        elif line:
            x = 0
            for cell in line:
                row_cell.append(MazeCell(x, y, cell))
                if walls_value(row_cell[x]) == 15:
                    setup_cell_type(row_cell[x], 'l')
                x += 1
            cells.append(row_cell)
        y += 1

    start, end = locations

    path = list(start)
    if road:
        for blk in road:
            if blk == "S":
                path[1] += 1
            elif blk == "N":
                path[1] -= 1
            elif blk == "E":
                path[0] += 1
            elif blk == "W":
                path[0] -= 1

            setup_cell_type(cells[path[1]][path[0]], 'r')

    setup_cell_type(cells[start[1]][start[0]], 's')
    setup_cell_type(cells[end[1]][end[0]], 'e')
    return cells


class AsciiArt:
    def __init__(self, config: str | TextIO | List[List[MazeCell]],
                 theme: str = "MIDNIGHT_OCEAN") -> None:
        self.theme = theme
        self.PAD = 2
        if isinstance(config, io.IOBase):
            config = config.read()
        if isinstance(config, str):
            self.maze: List[List[Cell]] = cells_gen(config)
            self.w = len(self.maze[0])
            self.h = len(self.maze)
        elif isinstance(config, list):
            self.maze = config
            self.w = len(self.maze[0])
            self.h = len(self.maze)
        else:
            raise ValueError("Invalid Config For AsciiArt")

    def render(self, show_path: bool = False):
        picker = ThemePicker(self.theme)
        maze_theme = picker.maze_theme().values()
        CELL, ROAD, WALL, OWALLS, PADDING, BACKDROP, SHADOW = maze_theme
        ENTRY, EXIT = picker.locations_theme().values()
        self.PAD = 2

        def generate_blk(color: str, inch: int) -> None:
            return f"{color}" + " " * inch + "\033[49m"

        def display_maze_information() -> None:
            print(f"\n{PADDING}   Width: {len(self.maze[0])}",
                  "  \033[49m    ", end="")
            print(f"{PADDING}   Height: {len(self.maze)}",
                  "  \033[49m    ", end="")
            print(f"{PADDING}   Theme: {self.theme}   \033[49m    ")
        print("\033[?25l ")
        sys.stdout.write("\033[0J\033[H")
        print(CLEAR_LINE, end="", flush=True)

        display_maze_information()

        buff: str = ""
        rendring_width = ((self.PAD * 4) * 2) + (self.w * 6) + 3
        for _ in range(0, 2):
            buff += generate_blk(PADDING, rendring_width)
            buff += "\n"

        for h in range(0, self.h):
            for row in range(0, 3):
                buff += generate_blk(PADDING, self.PAD * 3)
                buff += generate_blk(SHADOW, self.PAD)
                for w in range(0, self.w):
                    cell = self.maze[h][w]
                    if row == 0:
                        buff += generate_blk(WALL, 2)
                        if cell.value >> 0 & 1:
                            buff += generate_blk(WALL, 4)
                        else:
                            if (get_cell_type(cell) == 'r' and show_path
                               and (get_cell_type(self.maze[h - 1][w]) == 'r'
                                    or
                               get_cell_type(self.maze[h - 1][w]) == 's')):
                                buff += generate_blk(ROAD, 4)
                            else:
                                buff += generate_blk(OWALLS, 4)
                    else:
                        if cell.value >> 3 & 1:
                            buff += generate_blk(WALL, 2)
                        else:
                            if (get_cell_type(cell) == 'r' and show_path and
                               get_cell_type(self.maze[h][w - 1]) == 'r'):
                                buff += generate_blk(ROAD, 2)

                            else:
                                buff += generate_blk(OWALLS, 2)
                        if get_cell_type(cell) == 's':
                            buff += generate_blk(ENTRY, 4)
                        elif get_cell_type(cell) == 'o':
                            buff += generate_blk(ENTRY, 4)
                        elif get_cell_type(cell) == 'l':
                            buff += generate_blk(CELL, 4)
                        elif get_cell_type(cell) == 'e':
                            buff += generate_blk(EXIT, 4)
                        elif get_cell_type(cell) == 'r' and show_path:
                            buff += generate_blk(ROAD, 4)
                        else:
                            buff += generate_blk(BACKDROP, 4)
                buff += generate_blk(WALL, 2)
                buff += generate_blk(SHADOW, 1)
                buff += generate_blk(PADDING, self.PAD * 4)
                buff += "\n"

        buff += generate_blk(PADDING, self.PAD * 3)
        buff += generate_blk(SHADOW, self.PAD * 1)

        for cell in self.maze[self.h - 1]:
            buff += generate_blk(WALL, 2)
            if cell.value >> 2 & 1:
                buff += generate_blk(WALL, 4)
            else:
                buff += generate_blk(BACKDROP, 4)
        buff += generate_blk(WALL, 2)
        buff += generate_blk(SHADOW, 1)
        buff += generate_blk(PADDING, self.PAD * 4)
        buff += "\n"

        # bottom badding
        buff += generate_blk(PADDING, self.PAD * 3)
        buff += generate_blk(SHADOW, (self.w * 6) + 5)
        buff += generate_blk(PADDING, self.PAD * 4)
        buff += "\n"
        for _ in range(0, 2):
            buff += generate_blk(PADDING, rendring_width)
            buff += "\n"

        print("\033[?25l ")

        print(buff)
