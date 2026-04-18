from typing import List, TextIO
from .MazeCell import MazeCell
from .ThemePicker import ThemePicker
from .cell_encoding import get_wall_bits, set_cell_type, get_cell_type
import sys
import io


CLEAR_LINE = "\033[K"


def parse_maze_cells(cells_str: str) -> List[List[MazeCell]]:
    """
        Parse a maze string into a 2D grid of MazeCell objects.

        The string format expects:
            - Lines of cell characters forming the grid
            - A comma-separated line for start and end coordinates
            - An optional direction string using N/S/E/W to mark the road path

        Returns:
            A 2D list of MazeCell objects with types encoded in their value.
    """
    cells: List[List[MazeCell]] = []
    locations = []
    road: str = ""

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
                if get_wall_bits(row_cell[x]) == 15:
                    set_cell_type(row_cell[x], 'l')
                x += 1
            cells.append(row_cell)
            y += 1

    start, end = locations

    path = list(start)
    if road:
        for direction in road:
            if direction == "S":
                path[1] += 1
            elif direction == "N":
                path[1] -= 1
            elif direction == "E":
                path[0] += 1
            elif direction == "W":
                path[0] -= 1

            set_cell_type(cells[path[1]][path[0]], 'r')

    set_cell_type(cells[start[1]][start[0]], 's')
    set_cell_type(cells[end[1]][end[0]], 'e')
    return cells


class MazeRenderer:
    """
        Renders a maze grid as colored ASCII blocks in the terminal.

        Supports multiple visual themes and optional path highlighting.

        Args:
            config: A maze string, an open file, or a pre-built 2D MazeCell grid.
            theme:  Name of the color theme to use. Defaults to 'royal_depth'.
    """

    def __init__(self, config: str | TextIO | List[List[MazeCell]],
                 theme: str = "royal_depth") -> None:
        self.theme = theme
        if isinstance(config, io.IOBase):
            config = config.read()
        if isinstance(config, str):
            self.maze: List[List[MazeCell]] = parse_maze_cells(config)
            self.w = len(self.maze[0])
            self.h = len(self.maze)
        elif isinstance(config, list) and isinstance(config[0][0], MazeCell):
            self.maze = config
            self.w = len(self.maze[0])
            self.h = len(self.maze)
        else:
            raise ValueError("Invalid Config For MazeRandering")

    def render(self, show_path: bool = False) -> None:
        picker = ThemePicker(self.theme)
        maze_theme = picker.maze_theme().values()
        CELL, ROAD, WALL, OWALLS, PADDING, BACKDROP, SHADOW, VISITED = maze_theme
        ENTRY, EXIT = picker.locations_theme().values()
        PAD = 2

        def colored_block(color: str, width: int) -> str:
            return f"{color}" + " " * width + "\033[49m"

        def print_maze_stats() -> None:
            print(f"\n{PADDING}   Width: {len(self.maze[0])}",
                  "  \033[49m    ", end="")
            print(f"{PADDING}   Height: {len(self.maze)}",
                  "  \033[49m    ", end="")
            print(f"{PADDING}   Theme: {self.theme}   \033[49m    \n")
        print("\033[?25l ")
        sys.stdout.write("\033[0J\033[H")
        print(CLEAR_LINE, end="", flush=True)

        print_maze_stats()

        frame: str = ""
        frame_width = ((PAD * 4) * 2) + (self.w * 6) + 3
        for _ in range(0, 2):
            frame += colored_block(PADDING, frame_width)
            frame += "\n"

        for h in range(0, self.h):
            for cell_row in range(0, 3):
                frame += colored_block(PADDING, PAD * 3)
                frame += colored_block(SHADOW, PAD)
                for w in range(0, self.w):
                    cell = self.maze[h][w]
                    if cell_row == 0:
                        frame += colored_block(WALL, 2)
                        if cell.value & 1:
                            frame += colored_block(WALL, 4)
                        else:
                            if (get_cell_type(cell) == 'r' and show_path
                               and (get_cell_type(self.maze[h - 1][w]) == 'r'
                                    or
                               get_cell_type(self.maze[h - 1][w]) == 's')):
                                frame += colored_block(ROAD, 4)
                            elif ((get_cell_type(cell) == 's' or get_cell_type(cell) == 'e')
                                  and show_path and (get_cell_type(self.maze[h - 1][w]) == 'r')
                                  or get_cell_type(self.maze[])):
                                    frame += colored_block(ROAD, 4)
                            else:
                                frame += colored_block(OWALLS, 4)
                    else:
                        if cell.value >> 3 & 1:
                            frame += colored_block(WALL, 2)
                        else:
                            if ((get_cell_type(cell) == 'r' or
                                 get_cell_type(cell) == 'e') and show_path and
                               (get_cell_type(self.maze[h][w - 1]) == 'r' or
                                get_cell_type(self.maze[h][w - 1]) == 's' or
                                get_cell_type(self.maze[h][w - 1])== 'e')):
                                frame += colored_block(ROAD, 2)

                            else:
                                frame += colored_block(OWALLS, 2)
                        if get_cell_type(cell) == 's':
                            frame += colored_block(ENTRY, 4)
                        elif get_cell_type(cell) == 'o':
                            frame += colored_block(ENTRY, 4)
                        elif get_cell_type(cell) == 'l':
                            frame += colored_block(CELL, 4)
                        elif get_cell_type(cell) == 'e':
                            frame += colored_block(EXIT, 4)
                        elif get_cell_type(cell) == 'r' and show_path:
                            frame += colored_block(ROAD, 4)
                        elif get_cell_type(cell) == 'v':
                            frame += colored_block(VISITED, 4)
                        else:
                            frame += colored_block(BACKDROP, 4)
                frame += colored_block(WALL, 2)
                frame += colored_block(SHADOW, 1)
                frame += colored_block(PADDING, PAD * 4)
                frame += "\n"

        frame += colored_block(PADDING, PAD * 3)
        frame += colored_block(SHADOW, PAD * 1)

        for cell in self.maze[self.h - 1]:
            frame += colored_block(WALL, 2)
            if cell.value >> 2 & 1:
                frame += colored_block(WALL, 4)
            else:
                frame += colored_block(BACKDROP, 4)
        frame += colored_block(WALL, 2)
        frame += colored_block(SHADOW, 1)
        frame += colored_block(PADDING, PAD * 4)
        frame += "\n"

        frame += colored_block(PADDING, PAD * 3)
        frame += colored_block(SHADOW, (self.w * 6) + 5)
        frame += colored_block(PADDING, PAD * 4)
        frame += "\n"
        for _ in range(0, 2):
            frame += colored_block(PADDING, frame_width)
            frame += "\n"

        print(frame)
