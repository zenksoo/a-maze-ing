from typing import List, Any
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
            hex_val: Hex character encoding the initial wall state.
            Defaults to 'F' (all walls closed).
    """
    def __init__(self, x: int, y: int, hex_val: str = "F") -> None:

        self.value: int = int(hex_val, 16)
        self.neighbor: tuple[int, int] = (-1, -1)
        self.x: int = x
        self.y: int = y

        self.g: float = float('inf')
        self.h = 0
        self.f: float = float('inf')
        self.parent: MazeCell | None = self

    def __lt__(self, other: 'MazeCell') -> Any:
        return self.f < other.f

    def reset(self) -> None:
        """
            Reset A* state. Must be called before
            each new pathfinding search.
        """
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
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

    def get_all_neighbors(self, maze: List[List['MazeCell']]
                          ) -> List[tuple[Dir, 'MazeCell']]:
        all_neighbors = []
        x, y = (self.x, self.y)
        if y - 1 >= 0:
            all_neighbors.append((Dir.N, maze[y - 1][x]))
        if x + 1 < len(maze[0]):
            all_neighbors.append((Dir.E, maze[y][x + 1]))
        if y + 1 < len(maze):
            all_neighbors.append((Dir.S, maze[y + 1][x]))
        if x - 1 >= 0:
            all_neighbors.append((Dir.W, maze[y][x - 1]))
        return all_neighbors

    def sync_walls(self, maze: List[List['MazeCell']]) -> None:
        """Open the wall toward this cell's neighbor and close all others."""
        all_neighbors = self.get_all_neighbors(maze)
        origin = [Dir.N, Dir.E, Dir.S, Dir.W]
        reversed_dirs = [Dir.S, Dir.W, Dir.N, Dir.E]
        for dir, node in all_neighbors:
            if node.neighbor == (self.x, self.y):
                node.edit_wall(reversed_dirs[origin.index(dir)], Action.OPEN)
                self.edit_wall(dir, Action.OPEN)
            else:
                node.edit_wall(reversed_dirs[origin.index(dir)], Action.CLOSE)
                self.edit_wall(dir, Action.CLOSE)

    def get_open_neighbors(self, maze: List[List['MazeCell']]
                           ) -> List['MazeCell']:
        all_neighbors = []
        x, y = (self.x, self.y)
        if not self.value & 1 and y - 1 >= 0:
            all_neighbors.append(maze[y - 1][x])
        if not self.value >> 1 & 1 and x + 1 < len(maze[0]):
            all_neighbors.append(maze[y][x + 1])
        if not self.value >> 2 & 1 and y + 1 < len(maze):
            all_neighbors.append(maze[y + 1][x])
        if not (self.value >> 3 & 1) and x - 1 >= 0:
            all_neighbors.append(maze[y][x - 1])
        return all_neighbors

    def get_next_cell(self, maze: List[List['MazeCell']],
                      dir: Dir) -> 'MazeCell' | None:
        """
            Return the adjacent cell in a given direction,
            or None if out of bounds.
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
