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


class MazeCell():
    def __init__(self, x: int, y: int, hex_val: str = "F") -> None:
        self.value: int = int(hex_val, 16)
        self.neighbor: tuple = ()
        self.coor: tuple[int, int] = (x, y)

    def edit_wall(self, dir: Dir, action: Action):
        if self.value >> dir.value & 1 and action == Action.OPEN:
            self.value -= 2 ** dir.value
        elif not (self.value >> dir.value & 1) and action == Action.CLOSE:
            self.value += 2 ** dir.value

    def get_dir(self) -> Dir:
        x, y = self.coor
        if self.neighbor[1] < y:
            return Dir.N
        elif self.neighbor[1] > y:
            return Dir.S
        elif self.neighbor[0] < x:
            return Dir.W
        elif self.neighbor[0] > x:
            return Dir.E

    def get_neighbor(self,
                     maze: List[List['MazeCell']], dir: Dir) -> 'MazeCell':
        neighbor: MazeCell = None
        x, y = self.coor
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
        next_dirs = [Dir.E, Dir.W, Dir.N, Dir.S]
        for curr_dir, next_dir in zip(curr_dirs, next_dirs):
            self.edit_wall(curr_dir, Action.CLOSE)
            neighbor = self.get_neighbor(maze, curr_dir)
            if neighbor:
                neighbor.edit_wall(next_dir, Action.CLOSE)

    def update_all_walls(self, maze: List[List['MazeCell']]) -> None:
        dir = self.get_dir()
        x, y = self.coor
        curr_dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
        neigh_dirs = [Dir.S, Dir.W, Dir.N, Dir.E]

        for curr_dir, neigh_dir in zip(curr_dirs, neigh_dirs):
            neightbor = self.get_neighbor(maze, curr_dir)
            if curr_dir == dir:
                self.edit_wall(curr_dir, Action.OPEN)
                neightbor.edit_wall(neigh_dir, Action.OPEN)
            elif neightbor and (x, y) != neightbor.neighbor:
                self.edit_wall(curr_dir, Action.CLOSE)
                neightbor.edit_wall(neigh_dir, Action.CLOSE)
