from .MazeCell import MazeCell, Dir, Action
from .cell_encoding import set_cell_type, get_cell_type, get_wall_bits
from .MazeRenderer import MazeRenderer
from .config_parser import parse
from typing import List
import random
import time
from heapq import heappush, heappop
import sys


CLEAR_DOWN = "\033[J"


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
            maze[y][x].value = 15
            set_cell_type(maze[y][x], 'l')


def get_next_cell(maze: List[List[MazeCell]],
                  curr: MazeCell, dir: Dir
                 ) -> 'MazeCell' | None:
    """
        Return the adjacent cell in a given direction, or None if out of bounds.
        Args:
            maze: The full 2D maze grid.
            dir:  Direction to step toward.
    """
    neighbor: MazeCell | None = None
    x, y = (curr.x, curr.y)
    if dir == Dir.E and x + 1 < len(maze[0]):
        neighbor = maze[y][x + 1]
    elif dir == Dir.W and x - 1 >= 0:
        neighbor = maze[y][x - 1]
    elif dir == Dir.N and y - 1 >= 0:
        neighbor = maze[y - 1][x]
    elif dir == Dir.S and y + 1 < len(maze):
        neighbor = maze[y + 1][x]

    return neighbor

class MazeGenerator:
    def __init__(self, config_file_name: str, theme: str = "DEFAULT",
                 with_animation: bool = False) -> None:

        self.maze: List[List[MazeCell]] = []
        self.theme = theme
        self.config = parse(config_file_name)
        self.with_animation = with_animation
        self.seed = self.config.get("SEED")
        self.entry: tuple[int, int] = self.config["ENTRY"]
        self.exit: tuple[int, int] = self.config["EXIT"]
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
                set_cell_type(row_cells[x], 'v')
            self.maze.append(row_cells)

        lock_logo_cells(self.maze)

    def generate(self) -> None:
        """Generate a perfect maze using the origin-shift algorithm.

            Moves the origin cell randomly until all three corners have been visited,
            then runs a cooldown period to ensure full maze coverage.
        """
        art = MazeRenderer(self.maze, self.theme)
        origin_cell = self.maze[len(self.maze) - 1][len(self.maze[0]) - 1]
        visited = set()

        visited.add((origin_cell.x, origin_cell.y))

        def rand_dir(part: int = 0) -> Dir:
            if part == 1:
                return random.choice([Dir.E, Dir.N])
            elif part == 2:
                return random.choice([Dir.N, Dir.S])
            else:
                return random.choice([Dir.N, Dir.E, Dir.S, Dir.W])


        while len(visited) < (self.config["WIDTH"] * self.config["HEIGHT"] - 18):
            next_cell = get_next_cell(self.maze, origin_cell, rand_dir())
            while ((next_cell and get_cell_type(next_cell) == 'l')
                or not next_cell):
                next_cell = get_next_cell(self.maze, origin_cell, rand_dir())

            origin_cell.neighbor = (next_cell.x, next_cell.y)
            origin_cell = next_cell
            origin_cell.sync_walls(self.maze)
            set_cell_type(origin_cell, 'o')
            try:
                if self.with_animation:
                    art.render()
            except KeyboardInterrupt:
                self.with_animation = False
                print(CLEAR_DOWN, end='')
                sys.stdout.write("\033[0J\033[H")
            set_cell_type(origin_cell, 'n')
            visited.add((origin_cell.x, origin_cell.y))

        if (get_cell_type(self.maze[self.entry[1]][self.entry[0]]) == 'l' or
            get_cell_type(self.maze[self.exit[1]][self.exit[0]]) == 'l'):
            raise ValueError("The (Start | Exit) Point are in the Locked Cells")


    def imperfect_maze(self) -> None:
        w = len(self.maze[0]) - 1
        h = len(self.maze) - 1

        dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
        reversed_dirs = [Dir.S, Dir.W, Dir.N, Dir.E]
        def random_colsed_wall(cell: MazeCell):
            tmp_dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
            dir = random.choice(tmp_dirs)
            while tmp_dirs and not (cell.value >> dir.value & 1):
                dir = random.choice(tmp_dirs)
                tmp_dirs.remove(dir)
            return dir

        entry_cell = self.maze[self.entry[1]][self.entry[0]]
        exit_cell = self.maze[self.exit[1]][self.exit[0]]

        for cell in [exit_cell, entry_cell]:
            targets = [e[1] for e in cell.get_all_neighbors(self.maze)]
            for target in targets:
                rnd_dir = random_colsed_wall(target)

                next_cell = get_next_cell(self.maze, target, rnd_dir)

                if next_cell and get_cell_type(next_cell) != 'l':
                    next_cell.edit_wall(reversed_dirs[dirs.index(rnd_dir)], Action.OPEN)
                    target.edit_wall(rnd_dir, Action.OPEN)


    def solve_maze(self, start: MazeCell,
                   end: MazeCell,
                   with_animation: bool = False
                   ) -> List[tuple[int, int]] | None:
        """Find the shortest path from start to end using A*.

            Returns:
                Ordered list of (x, y) coordinates from start to end,
                or None if no path exists.
        """

        art = MazeRenderer(self.maze, self.theme)
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
            open_neighbors: List[MazeCell] = current.get_open_neighbors(self.maze)
            for neighbor in open_neighbors:
                if (get_cell_type(neighbor) != 's' and
                    get_cell_type(neighbor) != 'e'):
                    set_cell_type(neighbor, 'v')
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
            try:
                if with_animation:
                    art.render()
                    time.sleep(0.005)
            except KeyboardInterrupt:
                with_animation = False
                print(CLEAR_DOWN, end='')
                sys.stdout.write("\033[0J\033[H")
        return None

    def mark_solution_path(self, with_animation: bool = False):
        art = MazeRenderer(self.maze, self.theme)
        for x, y in self.solution[1:-1]:
            set_cell_type(self.maze[y][x], 'r')
            try:
                if with_animation:
                    art.render(True)
                    time.sleep(0.002)
            except KeyboardInterrupt:
                pass

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

    def run(self) -> None:
        """Run the full maze pipeline — build, generate, solve, and save.

            Args:
                seed: Optional seed override. Falls back to config or current time.
        """
        try:
            self.maze = []
            self.build_maze_grid()
            self.generate()
            if not self.config["PERFECT"]:
                self.imperfect_maze()
            self.find_and_mark_solution()
            self.__save_maze_to_file()
        except KeyboardInterrupt:
            pass

