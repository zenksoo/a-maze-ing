from .MazeCell import MazeCell, Dir, Action
from .cell_encoding import set_cell_type, get_cell_type, get_wall_bits
from .MazeRenderer import MazeRenderer
from .config_parser import parse
from typing import List
import random
import time
from heapq import heappush, heappop


def lock_logo_cells(maze: List[List[MazeCell]]) -> None:
    """Lock the cells that form the '42' logo shape in the center of the maze."""
    st_x = int((len(maze[0]) - 7) / 2)
    st_y = int((len(maze) - 5) / 2)

    FOUR_COORDS = [
        (st_x, st_y),
        (st_x, st_y + 1),
        (st_x, st_y + 2),
        (st_x + 1, st_y + 2),
        (st_x + 2, st_y + 2),
        (st_x + 2, st_y + 3),
        (st_x + 2, st_y + 4)
    ]

    st_x += 4
    TWO_COORDS = [
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

    for num in [FOUR_COORDS, TWO_COORDS]:
        for block in num:
            x, y = block
            maze[y][x].close_all(maze)
            set_cell_type(maze[y][x], 'l')


class MazeGenerator:
    def __init__(self, config_file_name: str, theme: str = "DEFAULT",
                 with_animation: bool = False) -> None:
        self.maze: List[List[MazeCell]] = []
        self.theme = theme
        self.config = parse(config_file_name)
        self.with_animation = with_animation
        self.seed = self.config.get("SEED")
        self.art: MazeRenderer | None = None
        self.entry: tuple[int, int] = [-1, -1]
        self.exit: tuple[int, int] = [-1, -1]
        self.solution: List[tuple[int, int]] = []
        if not self.seed:
            self.seed = time.time()
        random.seed(self.seed)

    def __save_maze_to_file(self) -> None:
        with open(self.config["OUTPUT_FILE"], "w") as f:
            for row in self.maze:
                for cell in row:
                    f.write("0123456789ABCDEF"[get_wall_bits(cell)])
                f.write("\n")
            f.write("\n")
            f.write(f"{self.config["ENTRY"][0]},{self.config["ENTRY"][1]}\n")
            f.write(f"{self.config["EXIT"][0]},{self.config["EXIT"][1]}\n")
            curr_cell = self.solution[0]
            for next_cell in self.solution[1:]:
                if curr_cell[0] < next_cell[0]:
                    f.write("E")
                elif curr_cell[0] > next_cell[0]:
                    f.write("W")
                elif curr_cell[1] > next_cell[1]:
                    f.write("N")
                elif curr_cell[1] < next_cell[1]:
                    f.write("S")
                curr_cell = next_cell

    def build_maze_grid(self) -> None:
        """Initialize the grid and connect cells using the origin-shift algorithm setup.

            Creates all MazeCell objects, locks the logo cells, then opens walls
            between adjacent cells to prepare for path generation.
        """
        for y in range(0, self.config["HEIGHT"]):
            row_cells = []
            for x in range(0, self.config["WIDTH"]):
                row_cells.append(MazeCell(x, y))
            self.maze.append(row_cells)

        lock_logo_cells(self.maze)

        self.entry = self.config["ENTRY"]
        self.exit = self.config["EXIT"]

        if (get_cell_type(self.maze[self.entry[1]][self.entry[0]]) == 'l' or
                get_cell_type(self.maze[self.exit[1]][self.exit[0]]) == 'l'):
            raise ValueError("The Start | Exit Coordinate in the Locked Cells")

        for row, y in zip(self.maze, range(0, len(self.maze))):
            for cell, x in zip(row, range(0, len(row))):
                if get_cell_type(cell) == 'l':
                    continue
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
                    set_cell_type(next_cell, 'n')

    def origin_shift(self) -> None:
        """Generate a perfect maze using the origin-shift algorithm.

            Moves the origin cell randomly until all three corners have been visited,
            then runs a cooldown period to ensure full maze coverage.
        """
        self.art = MazeRenderer(self.maze, self.theme)
        origin_cell = self.maze[len(self.maze) - 1][len(self.maze[0]) - 1]
        visited = set()

        visited.add((origin_cell.x, origin_cell.y))

        def rand_dir() -> Dir:
            directions = [Dir.N, Dir.E, Dir.S, Dir.W]
            return random.choice(directions)

        corner_flags: List[int] = [0, 0, 0]
        cooldown: int | float = 4
        while len(visited) < (self.config["WIDTH"] * self.config["HEIGHT"] - 18):
            x, y = (origin_cell.x, origin_cell.y)
            next_cell = origin_cell.get_next_cell(self.maze, rand_dir())
            while ((next_cell and get_cell_type(next_cell) == 'l')
                   or not next_cell):
                next_cell = origin_cell.get_next_cell(self.maze, rand_dir())

            origin_cell.neighbor = (next_cell.x, next_cell.y)
            origin_cell.sync_walls(self.maze)

            if (x, y) == (0, 0):
                corner_flags[0] = 1
            elif (x, y) == (len(self.maze[0]) - 1, 0):
                corner_flags[1] = 1
            elif (x, y) == (0, len(self.maze) - 1):
                corner_flags[2] = 1

            origin_cell = next_cell
            set_cell_type(origin_cell, 'o')
            if self.with_animation:
                self.art.render()
            set_cell_type(origin_cell, 'n')
            if all(corner_flags):
                cooldown -= 0.02
            visited.add((origin_cell.x, origin_cell.y))

    def solve_maze(self, start: MazeCell,
                   end: MazeCell,
                   with_animation: bool = False
                   ) -> List[tuple[int, int]] | None:
        """Find the shortest path from start to end using A*.

            Returns:
                Ordered list of (x, y) coordinates from start to end,
                or None if no path exists.
        """

        self.art = MazeRenderer(self.maze, self.theme)
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

        def get_open_neighbors(curr: MazeCell) -> List:
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

            for neighbor in all_neighbors:
                if (get_cell_type(neighbor) != 's' and
                    get_cell_type(neighbor) != 'e'):
                    set_cell_type(neighbor, 'v')
            return all_neighbors

        start.g = 0
        start.h = heuristic(start, end)
        start.f = start.h

        open_list = [start]
        closed_set = set()

        while open_list:
            current = heappop(open_list)

            if current == end:
                return reconstruct_path(current)

            closed_set.add((current.x, current.y))
            open_neighbors: List[MazeCell] = get_open_neighbors(current)
            open_neighbors = [(e.x, e.y) for e in open_neighbors]

            for nx, ny in open_neighbors:
                neighbor = self.maze[ny][nx]

                if (neighbor.x, neighbor.y) in closed_set:
                    continue
                tentative_g = current.g + 1
                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g      = tentative_g
                    neighbor.h      = heuristic(neighbor, end)
                    neighbor.f      = neighbor.g + neighbor.h
                    heappush(open_list, neighbor)
            if with_animation:
                self.art.render()
                time.sleep(0.0025)
        return None

    def mark_solution_path(self, with_animation: bool = False):
        for x, y in self.solution[1:-1]:
            set_cell_type(self.maze[y][x], 'r')
            if with_animation:
                self.art.render(True)
                time.sleep(0.002)

    def find_and_mark_solution(self, with_animation: bool = False) -> None:
            st_x, st_y = self.config["ENTRY"]
            set_cell_type(self.maze[st_y][st_x], 's')
            ed_x, ed_y = self.config["EXIT"]
            set_cell_type(self.maze[ed_y][ed_x], 'e')
            start = self.maze[st_y][st_x]
            end = self.maze[ed_y][ed_x]

            self.solution = self.solve_maze(start, end, with_animation)
            if not self.solution:
                raise ValueError("NO Path between Entry and Exit")
            self.mark_solution_path(with_animation)
            for row in self.maze:
                for cell in row:
                    if get_cell_type(cell) == 'v':
                        set_cell_type(cell, 'n')

    def run(self, seed: float | None = None) -> None:
        """Run the full maze pipeline — build, generate, solve, and save.

            Args:
                seed: Optional seed override. Falls back to config or current time.
        """
        if seed:
            self.seed = seed
        elif not self.config.get("SEED"):
            self.seed = time.time()

        self.maze = []
        self.build_maze_grid()
        self.origin_shift()
        self.find_and_mark_solution()
        self.__save_maze_to_file()
