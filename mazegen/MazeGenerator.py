from typing import List
from .MazeCell import MazeCell, Dir, Action
from .edit_cell_type import setup_cell_type, get_cell_type, walls_value
from mazegen.ascii_art import AsciiArt
from .config_parser import parse
import random
import time
from math import sqrt
from heapq import heappush, heappop


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
            setup_cell_type(maze[y][x], 'l')


class MazeGenerator:
    def __init__(self, config_file_name: str, theme: str = "DEFAULT",
                 with_animation: bool = False) -> None:
        self.maze: List[List[MazeCell]] = []
        self.theme = theme
        self.config = parse(config_file_name)
        self.with_animation = with_animation
        self.seed = self.config.get("SEED")
        self.art: AsciiArt | None = None
        self.solution: List[tuple[int, int]] = []

    def __output_file_generator(self) -> None:
        with open(self.config["OUTPUT_FILE"], "w") as f:
            for row in self.maze:
                for cell in row:
                    f.write("0123456789ABCDEF"[walls_value(cell)])
                f.write("\n")
            f.write("\n")
            f.write(f"{self.config["ENTRY"][0]},{self.config["ENTRY"][1]}\n")
            f.write(f"{self.config["EXIT"][0]},{self.config["EXIT"][1]}\n")
            start = self.solution[0]
            for road_part in self.solution[1:]:
                if start[0] < road_part[0]:
                    f.write("E")
                elif start[0] > road_part[0]:
                    f.write("W")
                elif start[1] > road_part[1]:
                    f.write("N")
                elif start[1] < road_part[1]:
                    f.write("S")
                start = road_part

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
                x, y = (cell.x, cell.y)
                next_cell = cell.get_next_cell(self.maze, Dir.E)
                if next_cell and get_cell_type(next_cell) != 'l':
                    cell.edit_wall(Dir.E, Action.OPEN)
                    next_cell.edit_wall(Dir.W, Action.OPEN)
                elif next_cell and get_cell_type(next_cell) == 'l':
                    tmp_cell = cell
                    while next_cell and get_cell_type(next_cell) == 'l':
                        next_cell = tmp_cell.get_next_cell(self.maze, Dir.S)
                        if get_cell_type(next_cell) == 'l':
                            tmp_cell.neighbor = (x - 1, y)
                            tmp_cell = self.maze[y][x - 1]
                        x -= 1
                    if next_cell and get_cell_type(next_cell) != 'l':
                        tmp_cell.edit_wall(Dir.S, Action.OPEN)
                        next_cell.edit_wall(Dir.N, Action.OPEN)
                elif not next_cell:
                    next_cell = cell.get_next_cell(self.maze, Dir.S)
                    if next_cell:
                        cell.edit_wall(Dir.S, Action.OPEN)
                        next_cell.edit_wall(Dir.N, Action.OPEN)
                if next_cell:
                    if cell.neighbor == (-1, -1):
                        cell.neighbor = (next_cell.x, next_cell.y)
                    setup_cell_type(next_cell, 'n')

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
        self.art = AsciiArt(self.maze, self.theme)
        active_cell = self.maze[len(self.maze) - 1][len(self.maze[0]) - 1]

        def rand_dir() -> Dir:
            directions = [Dir.N, Dir.E, Dir.S, Dir.W]
            return random.choice(directions)

        visited_corners: List[int] = [0, 0, 0]
        finall_delay: int | float = 4
        while (not all(visited_corners) or
               (all(visited_corners) and finall_delay > 0)):
            x, y = (active_cell.x, active_cell.y)
            next_cell = active_cell.get_next_cell(self.maze, rand_dir())
            while ((next_cell and get_cell_type(next_cell) == 'l')
                   or not next_cell):
                next_cell = active_cell.get_next_cell(self.maze, rand_dir())

            active_cell.neighbor = (next_cell.x, next_cell.y)
            active_cell.update_all_walls(self.maze)

            if (x, y) == (0, 0):
                visited_corners[0] = 1
            elif (x, y) == (len(self.maze[0]) - 1, 0):
                visited_corners[1] = 1
            elif (x, y) == (0, len(self.maze) - 1):
                visited_corners[2] = 1

            active_cell = next_cell
            setup_cell_type(active_cell, 'o')

            if self.with_animation:
                self.art.render()
            setup_cell_type(active_cell, 'n')
            if all(visited_corners):
                finall_delay -= 0.02

    def astar(self, start: MazeCell, end: MazeCell, with_animation: bool = False) -> None:
        self.art = AsciiArt(self.maze, self.theme)
        for row in self.maze:
            for cell in row:
                cell.reset()

        def reconstruct_path(cell):
            path = []
            while cell:
                path.append((cell.x, cell.y))
                cell = cell.parent
            return path[::-1]

        def heuristic(a, b):
            return abs(a.x - b.x) + abs(a.y - b.y)

        def get_all_neighbors(curr: MazeCell) -> List:
            all_neighbors = []
            x, y = (curr.x, curr.y)
            if not curr.value  & 1 and y - 1 >= 0:
                all_neighbors.append(self.maze[y - 1][x])
            if not curr.value >> 1 & 1 and x + 1 < len(self.maze[0]):
                all_neighbors.append(self.maze[y][x + 1])
            if not curr.value >> 2 & 1 and y + 1 < len(self.maze):
                all_neighbors.append(self.maze[y + 1][x])
            if not (curr.value >> 3 & 1) and x - 1 >= 0:
                all_neighbors.append(self.maze[y][x - 1])

            for ele in all_neighbors:
                if get_cell_type(ele) != 's' and get_cell_type(ele) != 'e':
                    setup_cell_type(ele, 'v')
            return all_neighbors

        start.g = 0
        start.h = heuristic(start, end)
        start.f = start.h

        openlist = [start]
        closed = set()

        while openlist:
            current = heappop(openlist)

            if current == end:
                return reconstruct_path(current)

            closed.add((current.x, current.y))
            all_neighbors: List[MazeCell] = get_all_neighbors(current)
            all_neighbors = [(e.x, e.y) for e in all_neighbors]

            for nx, ny in all_neighbors:
                neighbor = self.maze[ny][nx]

                if neighbor in closed:
                    continue
                next_step = current.g + 1
                if next_step < neighbor.g:
                    neighbor.parent = current
                    neighbor.g      = next_step
                    neighbor.h      = heuristic(neighbor, end)
                    neighbor.f      = neighbor.g + neighbor.h
                    heappush(openlist, neighbor)
            if with_animation:
                self.art.render()
                time.sleep(0.01)
        return None

    def setup_road(self, with_animation: bool = False):
        for x, y in self.solution[1:-1]:
            setup_cell_type(self.maze[y][x], 'r')
            if with_animation:
                self.art.render(True)
                time.sleep(0.02)

    def maze_solution(self, with_animation: bool = False) -> None:
            st_x, st_y = self.config["ENTRY"]
            setup_cell_type(self.maze[st_y][st_x], 's')
            ed_x, ed_y = self.config["EXIT"]
            setup_cell_type(self.maze[ed_y][ed_x], 'e')
            start = self.maze[st_y][st_x]
            end = self.maze[ed_y][ed_x]

            self.solution = self.astar(start, end, with_animation)
            if not self.solution:
                raise ValueError("NO Path between Entry and Exit")
            self.setup_road(with_animation)
            for row in self.maze:
                for cell in row:
                    if get_cell_type(cell) == 'v':
                        setup_cell_type(cell, 'n')

    def generate(self, seed: float | None = None) -> None:
        if seed:
            self.seed = seed
        elif not self.config.get("SEED"):
            self.seed = time.time()
        random.seed(self.seed)
        self.maze = []
        self.init_maze()
        self.origin_shift()
        self.maze_solution()
        self.__output_file_generator()




