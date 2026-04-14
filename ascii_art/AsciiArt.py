from typing import List, TextIO
from ascii_art.ThemePicker import ThemePicker
import sys
import io


class AsciiCell:
    def __init__(self, hex_val: str = "F") -> None:
        self.value: int = int(hex_val, 16)



def remove_bit(val, index) -> int:
    if val >> index & 1:
        val -= 2 ** index
    return val


def add_bit(val, index) -> int:
    if not (val >> index & 1):
        val += 2 ** index
    return val

def setup_cell_bits(cell: AsciiCell, new_type: str) -> None:
    """
        (left 2 bits in 4 MSB) in first byte in cell.value represent type of the cell
            **01 **** : start
            **10 **** : end
            **11 **** : road
            **00 **** : origin
    """
    # binary of start: **01 ****
    if new_type.lower() == 'l':
        cell.value = add_bit(cell.value, 8)

    elif new_type.lower() == 'o':
        cell.value = add_bit(cell.value, 9)

    # binary of start: **01 ****
    elif new_type.lower() == 's':
        cell.value = remove_bit(cell.value, 5)
        cell.value = add_bit(cell.value, 4)
        cell.value = remove_bit(cell.value, 8)

    # binary of end: **10 ****
    elif new_type.lower() == 'e':
        cell.value = remove_bit(cell.value, 4)
        cell.value = add_bit(cell.value, 5)
        cell.value = remove_bit(cell.value, 8)

    # binary of Road: **11 ****
    elif new_type.lower() == 'r':
        for i in range(4, 6):
            cell.value = add_bit(cell.value, i)
        cell.value = remove_bit(cell.value, 8)

    # binary of normal: **00 ****
    elif new_type.lower == 'n':
        cell.value = remove_bit(cell.value, 9)


def get_cell_type(cell: AsciiCell) -> str:
    # binary of locked cell is the LSB of the next byte: *******1 ********
    if cell.value >> 8 == 0b00000001:
        return 'l'

    elif cell.value >> 9 == 0b00000001:
        return 'o'

    # binary of start: **01 ****:
    elif cell.value >> 4 == 0b00000001:
        return 's'

    # binary of end: **10 ****
    elif cell.value >> 4 == 0b00000010:
        return 'e'

    # binary of Road: **11 ****
    elif cell.value >> 4 == 0b00000011:
        return 'r'

    # binary of normal: **00 ****
    elif cell.value >> 9 == 0b00000000:
        return 'n'

def walls_value(cell: AsciiCell) -> int:
    val = 0
    for i in range (0, 4):
        if (cell.value >> i & 1):
            val += 2 ** i
    return val


def cells_gen(cells_str: str) -> List[List[AsciiCell]]:
    cells: List[List[AsciiCell]] = []
    locations: List[tuple] = []
    road: str = None

    x = y = 0
    for line in cells_str.splitlines():
        row_cell: List[AsciiArt] = []
        if "," in line:
            locations.append(tuple(map(int, line.split(",")),))
        elif any(c in "NSW" for c in line):
            road = line
        elif line:
            x = 0
            for cell in line:
                row_cell.append(AsciiCell(cell))
                if walls_value(row_cell[x]) == 15:
                    setup_cell_bits(row_cell[x], 'l')
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

            setup_cell_bits(cells[path[1]][path[0]], 'r')

    setup_cell_bits(cells[start[1]][start[0]], 's')
    setup_cell_bits(cells[end[1]][end[0]], 'e')
    return cells


def print_blk(color: str, inch: int) -> None:
    DEFAULT = "\033[49m"
    sys.stdout.write(f"{color}" + " " * inch + DEFAULT)
    sys.stdout.flush()


class AsciiArt:
    def __init__(self, config: str | TextIO | List[List[AsciiCell]],
                 theme: str = "MIDNIGHT_OCEAN") -> None:
        self.theme = theme
        self.PAD = 2
        if isinstance(config, io.IOBase):
            config = config.read()
        if isinstance(config, str):
            self.maze: List[List[AsciiCell]] = cells_gen(config)
            self.width = len(self.maze[0])
            self.height = len(self.maze)
        elif isinstance(config, list):
            self.maze = config
            self.width = len(self.maze[0])
            self.height = len(self.maze)
        else:
            raise ValueError("The Config Must be String or File")

    def render(self, show_path: bool = False):
        picker = ThemePicker(self.theme)
        maze_theme = picker.maze_theme().values()
        CELL, ROAD, WALL, PADDING, BACKDROP, SHADOW = maze_theme
        ENTRY, EXIT = picker.locations_theme().values()
        self.PAD = 2

        # top padding
        sys.stdout.write("\033[0J\033[H")
        sys.stdout.flush()
        for _ in range(0, 2):
            print_blk(PADDING, ((self.PAD * 4) * 2) + (self.width * 6) + 3)
            print(flush=True)

        for h in range(0, self.height):
            for j in range(0, 3):
                print_blk(PADDING, self.PAD * 4)
                for w in range(0, self.width):
                    cell = self.maze[h][w]
                    if j == 0:
                        print_blk(WALL, 2)
                        if cell.value >> 0 & 1:
                            print_blk(WALL, 4)
                        else:
                            print_blk(BACKDROP, 4)
                    else:
                        if cell.value >> 3 & 1:
                            print_blk(WALL, 2)
                        else:
                            print_blk(BACKDROP, 2)
                        if get_cell_type(cell) == 's':
                            print_blk(ENTRY, 4)
                        elif get_cell_type(cell) == 'o':
                            print_blk(ENTRY, 4)
                        elif get_cell_type(cell) == 'l':
                            print_blk(CELL, 4)
                        elif get_cell_type(cell) == 'e':
                            print_blk(EXIT, 4)
                        elif get_cell_type(cell) == 'r' and show_path:
                            print_blk(ROAD, 4)
                        else:
                            print_blk(BACKDROP, 4)
                print_blk(WALL, 2)
                print_blk(SHADOW, 1)
                print_blk(PADDING, self.PAD * 4)
                sys.stdout.write("\n")

        print_blk(PADDING, self.PAD * 4)
        for cell in self.maze[self.height - 1]:
            print_blk(WALL, 2)
            if cell.value >> 2 & 1:
                print_blk(WALL, 4)
            else:
                print_blk(BACKDROP, 4)
        print_blk(WALL, 2)
        print_blk(SHADOW, 1)
        print_blk(PADDING, self.PAD * 4)
        sys.stdout.write("\n")

        # bottom badding
        print_blk(PADDING, self.PAD * 4)
        print_blk(SHADOW, (self.width * 6) + 3)
        print_blk(PADDING, self.PAD * 4)
        sys.stdout.write("\n")
        for _ in range(0, 2):
            print_blk(PADDING, ((self.PAD * 4) * 2) + (self.width * 6) + 3)
            sys.stdout.write("\n")

    def animation_menu(self):
        pass
