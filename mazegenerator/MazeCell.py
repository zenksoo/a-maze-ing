from typing import List
from enum import Enum


class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


class Action(Enum):
    OPEN = 0
    CLOSE = 1


class MazeCell:
    """
        A single cell in the maze grid

        Wall state is encoded in the 4 LSBs of value
            bit 0 → North
            bit 1 → East
            bit 2 → South
            bit 3 → West

        A* pathfinding state (g, h, f, parent) lives here too
        and must be reset via reset() before each new search.

        Args:
            x:       Column index in the maze grid.
            y:       Row index in the maze grid.
            hex_val: Hex character encoding the initial wall state. Defaults to 'F' (all walls closed).
    """
    def __init__(self, x: int, y: int, hex_val: str = "F") -> None:

        self.value: int = int(hex_val, 16)
        self.neighbor: tuple[int, int] = (-1, -1)
        self.x: int = x
        self.y: int = y

        self.g: float = float('inf')
        self.h = 0
        self.f: float = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

    def reset(self) -> None:
        """Reset A* state. Must be called before each new pathfinding search."""
        self.g: float = float('inf')
        self.h = 0
        self.f: float = float('inf')
        self.parent = None

    def edit_wall(self, dir: Dir, action: Action) -> None:
        """
            Open or close a single wall on this cell.

            Args:
                direction: Which wall to modify.
                action:    OPEN removes the wall, CLOSE adds it.
        """
        if self.value >> dir.value & 1 and action == Action.OPEN:
            self.value -= 2 ** dir.value
        elif not (self.value >> dir.value & 1) and action == Action.CLOSE:
            self.value += 2 ** dir.value

    def get_dir(self) -> Dir | None:
        x, y = (self.x, self.y)
        if self.neighbor[1] < y:
            return Dir.N
        elif self.neighbor[1] > y:
            return Dir.S
        elif self.neighbor[0] < x:
            return Dir.W
        elif self.neighbor[0] > x:
            return Dir.E
        return None

    def get_next_cell(self, maze: List[List['MazeCell']],
                     dir: Dir) -> 'MazeCell' | None:
        """
            Return the adjacent cell in a given direction, or None if out of bounds.
            Args:
                maze: The full 2D maze grid.
                dir:  Direction to step toward.
        """
        neighbor: MazeCell | None = None
        x, y = (self.x, self.y)
        if dir == Dir.E and x + 1 < len(maze[0]):
            neighbor = maze[y][x + 1]
        elif dir == Dir.W and x - 1 >= 0:
            neighbor = maze[y][x - 1]
        elif dir == Dir.N and y - 1 >= 0:
            neighbor = maze[y - 1][x]
        elif dir == Dir.S and y + 1 < len(maze):
            neighbor = maze[y + 1][x]

        return neighbor

    def close_all(self, maze: List[List['MazeCell']]) -> None:
        curr_dirs = [Dir.N, Dir.S, Dir.E, Dir.W]
        opposite_dirs = [Dir.E, Dir.W, Dir.N, Dir.S]
        for curr_dir, next_dir in zip(curr_dirs, opposite_dirs):
            self.edit_wall(curr_dir, Action.CLOSE)
            neighbor = self.get_next_cell(maze, curr_dir)
            if neighbor:
                neighbor.edit_wall(next_dir, Action.CLOSE)

    def sync_walls(self, maze: List[List['MazeCell']]) -> None:
        """Open the wall toward this cell's neighbor and close all others."""
        dir = self.get_dir()
        x, y = (self.x, self.y)
        curr_dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
        neigh_dirs = [Dir.S, Dir.W, Dir.N, Dir.E]

        for curr_dir, neigh_dir in zip(curr_dirs, neigh_dirs):
            neighbor = self.get_next_cell(maze, curr_dir)
            if curr_dir == dir:
                self.edit_wall(curr_dir, Action.OPEN)
                neighbor.edit_wall(neigh_dir, Action.OPEN)
            elif neighbor and (x, y) != neighbor.neighbor:
                self.edit_wall(curr_dir, Action.CLOSE)
                neighbor.edit_wall(neigh_dir, Action.CLOSE)
