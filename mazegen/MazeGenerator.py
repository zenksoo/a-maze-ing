from typing import List, Dict
from .MazeCell import MazeCell, Dir, Action
from .edit_cell_bits import *
import importlib
import random
import time


def lock_fortytwo_blocks(maze: List[List[MazeCell]]) -> None:
    st_x = int((len(maze[0]) - 7) / 2)
    st_y = int((len(maze) - 5) / 2)

    ROUR = [
        (st_x, st_y),
        (st_x, st_y + 1),
        (st_x, st_y + 2),
        (st_x + 1, st_y + 2),
        (st_x + 2, st_y + 2),
        (st_x + 2, st_y + 3),
        (st_x + 2, st_y + 4)
    ]

    st_x += 4
    TWO = [
        (st_x, st_y),
        (st_x + 1, st_y),
        (st_x + 2, st_y),
        (st_x + 2, st_y + 1),
        (st_x + 2, st_y + 2),
        (st_x + 1, st_y + 2),
        (st_x, st_y + 2),
        (st_x, st_y + 3),
        (st_x, st_y + 4),
        (st_x + 1, st_y + 4),
        (st_x + 2, st_y + 4),
    ]

    for num in [ROUR, TWO]:
        for block in num:
            x, y = block
            maze[y][x].close_all(maze)
            setup_cell_bits(maze[y][x], 'l')


def rand_dir() -> Dir:
    all_choise = [Dir.N, Dir.E, Dir.S, Dir.W]
    return random.choice(all_choise)


class MazeGenerator:
    def __init__(self, config: Dict, theme: str = "DEFAULT",
                 with_animation: bool = False) -> None:
        self.maze: List[List[MazeCell]] = []
        self.theme = theme
        self.config = config
        self.with_animation = with_animation
        self.seed = self.config.get("SEED")
        if not self.seed:
            self.seed = int(time.time())

        random.seed(self.seed)

    def __output_file_generator(self) -> None:
        with open("test.txt", "w") as f:
            for row in self.maze:
                for cell in row:
                    f.write("0123456789ABCDEF"[walls_value(cell)])
                f.write("\n")
            f.write("\n")
            f.write(f"{self.config["ENTRY"][0]},{self.config["ENTRY"][1]}\n")
            f.write(f"{self.config["EXIT"][0]},{self.config["EXIT"][1]}\n")

    def init_maze(self) -> None:
        """
        initialize the maze for origin shift algo
        open all the cells from right
            - if the next right block is locked try to open from bottom
            - if the next bottom block is locked move back to (x - n, y)
                to find the bottom block that not locked and open it

            the open means i open from direction of the current cell and from
            direction of next block [ right | bottom ]
        """
        for y in range(0, self.config["HEIGHT"]):
            row_cells = []
            for x in range(0, self.config["WIDTH"]):
                row_cells.append(MazeCell(x, y))
            self.maze.append(row_cells)

        lock_fortytwo_blocks(self.maze)
        entry = self.config["ENTRY"]
        exit = self.config["EXIT"]

        if (get_cell_type(self.maze[entry[1]][entry[0]]) == 'l' or
            get_cell_type(self.maze[exit[1]][exit[0]]) == 'l'):
            raise ValueError("invalid coordinate")


        for row in self.maze:
            for cell in row:
                if get_cell_type(cell) == 'l':
                    continue
                next_cell = cell.get_neighbor(self.maze, Dir.E)
                if next_cell and get_cell_type(next_cell) != 'l':
                    cell.edit_wall(Dir.E, Action.OPEN)
                    next_cell.edit_wall(Dir.W, Action.OPEN)
                elif next_cell and get_cell_type(next_cell) == 'l':
                    tmp_cell = cell
                    x, y = (cell.x, cell.y)
                    while next_cell and get_cell_type(next_cell) == 'l':
                        next_cell = tmp_cell.get_neighbor(self.maze, Dir.S)
                        if get_cell_type(next_cell) == 'l':
                            tmp_cell.neighbor = (x - 1, y)
                        tmp_cell = self.maze[y][x - 1]
                        x -= 1
                    if next_cell and get_cell_type(next_cell) != 'l':
                        self.maze[y][x].edit_wall(Dir.S, Action.OPEN)
                        next_cell.edit_wall(Dir.N, Action.OPEN)
                elif not next_cell:
                    next_cell = cell.get_neighbor(self.maze, Dir.S)
                    if next_cell:
                        cell.edit_wall(Dir.S, Action.OPEN)
                        next_cell.edit_wall(Dir.N, Action.OPEN)
                if next_cell:
                    setup_cell_bits(next_cell, 'o')
                    if cell.neighbor == ():
                        cell.neighbor = (next_cell.x, next_cell.y)
                    setup_cell_bits(next_cell, 'n')

    def origin_shift(self) -> None:
        """
            ORIGIN SHIFT ALGO TO GENERATE THE BERFECT MAZE BY SEED
                if you give them wrong seed generate random seed depends on
                your wrong seed
                if you don't give them seed it take random seed and use them
            the origin cell have four dirs to choise someone randomly depends
              on seed
                - after choising direction i get the neighber that next the
                origin cell from this direction
                - i choise another neighbor:
                    - if neightbor is locked or none choise another one
                    - if the neighbor of the choising neighbor is the origin
                    cell
            start from the origin cell and start move the origin flag to the
            next neighbor

        """
        origin = self.maze[len(self.maze) - 1][len(self.maze[0]) - 1]

        if self.with_animation:
            from ascii_art import AsciiArt
            art = AsciiArt(self.maze, self.theme)

        corns = [0, 0, 0, 4]
        while not all(corns) or (all(corns) and corns[3] > 0):
            neighbor = origin.get_neighbor(self.maze, rand_dir())
            while ((neighbor and get_cell_type(neighbor) == 'l')
                   or not neighbor):
                neighbor = origin.get_neighbor(self.maze, rand_dir())

            origin.neighbor = (neighbor.x, neighbor.y)
            origin.update_all_walls(self.maze)
            setup_cell_bits(origin, 'o')

            if (origin.x, origin.y) == (0, 0):
                corns[0] = 1
            elif (origin.x, origin.y) == (len(self.maze[0]) - 1, 0):
                corns[1] = 1
            elif (origin.x, origin.y) == (0, len(self.maze) - 1):
                corns[2] = 1
            try:
                if self.with_animation:
                    art.render()
            except KeyboardInterrupt:
                self.with_animation = False
            setup_cell_bits(origin, 'n')
            origin = neighbor
            if all(corns):
                corns[3] -= 0.002

    def generate(self) -> None:
        if self.with_animation:
            try:
                _ = importlib.import_module("ascii_art.AsciiArt")
            except ImportError:
                self.with_animation = False
        try:
            self.init_maze()
            self.origin_shift()
            x, y = self.config["ENTRY"]
            setup_cell_bits(self.maze[y][x], 's')
            x, y = self.config["EXIT"]
            setup_cell_bits(self.maze[y][x], 'e')
            self.__output_file_generator()
        except Exception as e:
            print(f"Maze Generator Failed: {e}")
