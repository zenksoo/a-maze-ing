from .cell_encoding import set_cell_type, get_cell_type, get_wall_bits
from .MazeRenderer import MazeRenderer
from .MazeCell import MazeCell, Dir, Action
from .MazeConfig import MazeConfig
from heapq import heappush, heappop
from typing import List, Any
import random
import time
import sys


CLEAR_DOWN = "\033[J"


class MazeGenerator:
    def __init__(self, w: int,
                 h: int,  entry: tuple[int, int], exit: tuple[int, int],
                 output_file: str, perfect: bool, seed: float | None,
                 theme: str = "DEFAULT",
                 with_animation: bool = False) -> None:
        self.maze: List[List[MazeCell]] = []
        self.theme = theme
        self.width = w
        self.height = h
        self.entry = entry
        self.exit = exit
        self.output_file = output_file,
        self.perfect = perfect
        self.seed = seed
        if not self.seed:
            self.seed = time.time()
        random.seed(self.seed)

        self.with_animation = with_animation
        self.solution: List[tuple[int, int]] = []

    @classmethod
    def from_object(cls, config: MazeConfig, theme: str = "royal_depth",
                    with_animation: bool = False) -> 'MazeGenerator':
        return cls(
            w=config.width,
            h=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
            output_file=config.output_file,
            theme=theme,
            with_animation=with_animation,
        )

    def save_maze_to_file(self) -> None:
        try:
            with open(self.output_file[0], "w") as f:
                for row in self.maze:
                    for cell in row:
                        f.write("0123456789ABCDEF"[get_wall_bits(cell)])
                    f.write("\n")
                f.write("\n")
                f.write(f"{self.entry[0]},{self.entry[1]}\n")
                f.write(f"{self.exit[0]},{self.exit[1]}\n")
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
        except (IOError, Exception) as e:
            raise ValueError(f"Failed writing output file {e}")

    def _add_42_logo(self) -> None:
        """
            Lock the cells that form the '42' logo shape
            in the center of the maze."""
        logo_42 = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 2),
            (2, 3), (2, 4), (4, 0), (5, 0), (6, 0),
            (6, 1), (6, 2), (5, 2), (4, 2), (4, 3),
            (4, 4), (5, 4), (6, 4),
        ]

        for coor in logo_42:
            x, y = coor
            x += int((len(self.maze[0]) - 7) / 2)
            y += int((len(self.maze) - 5) / 2)
            self.maze[y][x].value = 15
            set_cell_type(self.maze[y][x], 'l')

    def build_maze_grid(self) -> None:
        """Initialize the grid and connect cells using the
            origin-shift algorithm setup.

            Creates all MazeCell objects, locks the logo cells,
            then opens walls
            between adjacent cells to prepare for path generation.
        """
        for y in range(0, self.height):
            row_cells = []
            for x in range(0, self.width):
                row_cells.append(MazeCell(x, y))
                set_cell_type(row_cells[x], 'v')
            self.maze.append(row_cells)

        self._add_42_logo()
        if (get_cell_type(self.maze[self.entry[1]][self.entry[0]]) == 'l' or
           get_cell_type(self.maze[self.exit[1]][self.exit[0]]) == 'l'):
            raise ValueError("The (Start | Exit) are in the Locked Cells")

    def origin_shift(self) -> None:
        """Generate a perfect maze using the origin-shift algorithm.

            Moves the origin cell randomly until all three
            corners have been visited,
            then runs a cooldown period to ensure full maze coverage.
        """
        art = MazeRenderer(self.maze, self.theme)
        origin_cell = self.maze[0][0]
        visited = set()

        visited.add((origin_cell.x, origin_cell.y))

        def rand_dir() -> Dir:
            return random.choice([Dir.N, Dir.E, Dir.S, Dir.W])

        while len(visited) < (self.width * self.height - 18):
            next_cell = origin_cell.get_next_cell(self.maze, rand_dir())
            while ((next_cell and get_cell_type(next_cell) == 'l')
                   or not next_cell):
                next_cell = origin_cell.get_next_cell(self.maze, rand_dir())

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

    def imperfect_maze(self) -> None:
        direction = [Dir.N, Dir.E, Dir.S, Dir.W]
        reversed_dir = [Dir.S, Dir.W, Dir.N, Dir.E]

        def random_colsed_wall(cell: MazeCell) -> Dir:
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

                next_cell = target.get_next_cell(self.maze, rnd_dir)

                if next_cell and get_cell_type(next_cell) != 'l':
                    neigh_dir = reversed_dir[direction.index(rnd_dir)]
                    next_cell.edit_wall(neigh_dir, Action.OPEN)
                    target.edit_wall(rnd_dir, Action.OPEN)

    def solve_maze(self, start: MazeCell,
                   end: MazeCell,
                   with_animation: bool = False
                   ) -> List[tuple[int, int]]:
        """Find the shortest path from start to end using A*.

            Returns:
                Ordered list of (x, y) coordinates from start to end,
                or None if no path exists.
        """

        art = MazeRenderer(self.maze, self.theme)
        for row in self.maze:
            for cell in row:
                cell.reset()

        def reconstruct_path(cell: MazeCell | None) -> List[tuple[int, int]]:
            path = []
            while cell:
                path.append((cell.x, cell.y))
                cell = cell.parent
            return path[::-1]

        def heuristic(a: MazeCell, b: MazeCell) -> Any:
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
            open_neighbors = current.get_open_neighbors(self.maze)
            for neighbor in open_neighbors:
                if (get_cell_type(neighbor) != 's' and
                   get_cell_type(neighbor) != 'e'):
                    set_cell_type(neighbor, 'v')

            for neighbor in open_neighbors:

                if (neighbor.x, neighbor.y) in closed_set:
                    continue
                tentative_g = current.g + 1
                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = heuristic(neighbor, end)
                    neighbor.f = neighbor.g + neighbor.h
                    heappush(open_list, neighbor)
            try:
                if with_animation:
                    art.render()
                    time.sleep(0.005)
            except KeyboardInterrupt:
                with_animation = False
                print(CLEAR_DOWN, end='')
                sys.stdout.write("\033[0J\033[H")
        return []

    def mark_solution_path(self, with_animation: bool = False) -> None:
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
        st_x, st_y = self.entry
        set_cell_type(self.maze[st_y][st_x], 's')
        ed_x, ed_y = self.exit
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

    def generate(self) -> None:
        """Run the full maze pipeline — build, generate, solve, and save."""
        self.maze = []
        self.build_maze_grid()
        self.origin_shift()
        if not self.perfect:
            self.imperfect_maze()
        self.find_and_mark_solution()
        self.save_maze_to_file()
