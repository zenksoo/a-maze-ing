from typing import List, Dict
from .MazeCell import MazeCell
from .Maze import Maze
from common import Dir, Action, Themes, CellType
import time
import importlib
import random


def get_neighbor(maze: List[List[MazeCell]],
                 curr_cell: MazeCell,
                 dir: Dir) -> MazeCell:

    neighbor: MazeCell = None
    if dir == Dir.E and curr_cell.x + 1 < len(maze[0]):
        neighbor = maze[curr_cell.y][curr_cell.x + 1]
    elif dir == Dir.W and curr_cell.x - 1 >= 0:
        neighbor = maze[curr_cell.y][curr_cell.x - 1]
    elif dir == Dir.N and curr_cell.y - 1 >= 0:
        neighbor = maze[curr_cell.y - 1][curr_cell.x]
    elif dir == Dir.S and curr_cell.y + 1 < len(maze):
        neighbor = maze[curr_cell.y + 1][curr_cell.x]

    return neighbor


def close_all(maze: List[List[MazeCell]],
              curr_cell: MazeCell) -> None:
    curr_dirs = [Dir.N, Dir.S, Dir.E, Dir.W]
    next_dirs = [Dir.E, Dir.W, Dir.N, Dir.S]
    for curr, next in zip(curr_dirs, next_dirs):
        curr_cell.edit_wall(curr, Action.CLOSE)
        neighbor = get_neighbor(maze, curr_cell, curr)
        if neighbor:
            neighbor.edit_wall(next, Action.CLOSE)


def get_dir(cell: MazeCell) -> Dir:
    if cell.neighbor[1] < cell.y:
        return Dir.N
    elif cell.neighbor[1] > cell.y:
        return Dir.S
    elif cell.neighbor[0] < cell.x:
        return Dir.W
    elif cell.neighbor[0] > cell.x:
        return Dir.E


def update_all(maze: List[List[MazeCell]],
               curr_cell: MazeCell) -> None:
    dir = get_dir(curr_cell)
    curr_dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
    neigh_dirs = [Dir.S, Dir.W, Dir.N, Dir.E]

    for cdir, ndir in zip(curr_dirs, neigh_dirs):
        neightbor = get_neighbor(maze, curr_cell, cdir)
        if cdir == dir:
            curr_cell.edit_wall(cdir, Action.OPEN)
            neightbor.edit_wall(ndir, Action.OPEN)
        elif neightbor and (curr_cell.x, curr_cell.y) != neightbor.neighbor:
            curr_cell.edit_wall(cdir, Action.CLOSE)
            neightbor.edit_wall(ndir, Action.CLOSE)

def draw_fourty_two(maze: List[List[MazeCell]]) -> None:
    st_x = int((len(maze[0]) - 7) / 2)
    st_y = int((len(maze) - 5) / 2)

    four = [
        (st_x, st_y),
        (st_x, st_y + 1),
        (st_x, st_y + 2),
        (st_x + 1, st_y + 2),
        (st_x + 2, st_y + 2),
        (st_x + 2, st_y + 3),
        (st_x + 2, st_y + 4)
    ]

    st_x += 4
    two = [
        (st_x, st_y),
        (st_x + 1, st_y),
        (st_x + 2, st_y),
        (st_x + 2, st_y + 1),
        (st_x + 2, st_y + 2),
        (st_x + 1, st_y + 2),
        (st_x , st_y + 2),
        (st_x , st_y + 3),
        (st_x , st_y + 4),
        (st_x + 1, st_y + 4),
        (st_x + 2, st_y + 4),
    ]


    for num in [four, two]:
        for block in num:
            x, y = block
            close_all(maze, maze[y][x])
            maze[y][x].type = CellType.LOCKED


class MazeGenerator:
    def __init__(self, config: Dict, theme: Themes = Themes.DEFAULT) -> None:
        self.maze: List[List[MazeCell]] = []
        self.theme: Themes = theme
        self.show_path = False
        self.height = config["HEIGHT"]
        self.width = config["WIDTH"]
        self.seed = config.get("SEED")


    def __output_file_generator(self) -> None:
        with open("test.txt", "w") as f:
            for row in self.maze:
                for cell in row:
                    f.write("0123456789ABCDEF"[cell.value])
                f.write("\n")


    def init_maze(self, animation: bool = False) -> None:
        for y in range(0, self.height):
            row_cells = []
            for x in range(0, self.width):
                row_cells.append(MazeCell(x, y))
            self.maze.append(row_cells)

        # try to import maze randering for display if find them generate maze by animation if no skip
        if animation:
            from ascii_art import AsciiArt
            art = AsciiArt(self.maze, self.theme)

        draw_fourty_two(self.maze)

        # initialize the maze for origin shift algo
        # open all the cells from right
        #      - if the next right block is locked try to open from bottom
        #           - if the next bottom block is locked move back from curr_cell.x to find the bottom block that not locked and open it
        for row in self.maze:
            for cell in row:
                if cell.type != CellType.LOCKED:
                    next_cell = get_neighbor(self.maze, cell, Dir.E)
                    if next_cell and next_cell.type != CellType.LOCKED:
                        cell.edit_wall(Dir.E, Action.OPEN)
                        next_cell.edit_wall(Dir.W, Action.OPEN)
                    elif next_cell and next_cell.type == CellType.LOCKED:
                        next_cell = get_neighbor(self.maze, cell, Dir.S)
                        x = cell.x
                        while next_cell and next_cell.type == CellType.LOCKED:
                            x -= 1
                            next_cell = get_neighbor(self.maze, self.maze[cell.y][x], Dir.S)
                        if next_cell and next_cell.type != CellType.LOCKED:
                            self.maze[cell.y][x].edit_wall(Dir.S, Action.OPEN)
                            next_cell.edit_wall(Dir.N, Action.OPEN)
                    elif not next_cell:
                        next_cell = get_neighbor(self.maze, cell, Dir.S)
                        if next_cell:
                            cell.edit_wall(Dir.S, Action.OPEN)
                            next_cell.edit_wall(Dir.N, Action.OPEN)
                    if next_cell:
                        next_cell.type = CellType.ORIGIN
                        cell.neighbor = (next_cell.x, next_cell.y)
                        try:
                            if animation:
                                art.render()
                                time.sleep(0.000000000001)
                        except KeyboardInterrupt:
                            animation = False
                        next_cell.type = CellType.NORMAL

        neig = get_neighbor(self.maze, self.maze[0][2], Dir.N)

    def origin_shift(self, animation: bool = False) -> None:
        origin = self.maze[len(self.maze) - 1][len(self.maze[0]) - 1]

        if animation:
            from ascii_art import AsciiArt
            art = AsciiArt(self.maze, self.theme)

        origin.type = CellType.ORIGIN
        seed = self.seed
        while seed > 0:
            random.seed(seed)
            all_choise = [Dir.N, Dir.E, Dir.S, Dir.W]
            neighbor = get_neighbor(self.maze, origin, random.choice(all_choise))
            while neighbor and neighbor.type == CellType.LOCKED:
                neighbor = get_neighbor(self.maze, origin, random.choice(all_choise))
            while not neighbor:
                neighbor = get_neighbor(self.maze, origin, random.choice(all_choise))
            while neighbor.neighbor == () and neighbor.neighbor == (origin.x, origin.y):
                neighbor = get_neighbor(self.maze, origin, random.choice(all_choise))

            origin.neighbor = (neighbor.x, neighbor.y)
            update_all(self.maze, origin)
            origin = neighbor
            origin.type = CellType.ORIGIN
            seed -= 0.001
            try:
                if animation:
                    art.render()
                    time.sleep(0.0001)
            except KeyboardInterrupt:
                animation = False
            origin.type = CellType.NORMAL
    def generate(self) -> None:
        try:
            _ = importlib.import_module("ascii_art.AsciiArt")
            animation = True
        except ImportError:
            animation = False
        self.init_maze(animation)
        self.origin_shift(animation)
        self.__output_file_generator()
