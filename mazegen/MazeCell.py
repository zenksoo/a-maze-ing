from common import Dir, Action, CellType, Cell
from typing import List



class MazeCell(Cell):
    def __init__(self, x: int, y: int,hex_val: str = "F") -> None:
        super().__init__(hex_val)
        self.neighbor: tuple = ()
        self.x = x
        self.y = y


    def edit_wall(self, dir: Dir, action: Action):
        if self.value >> dir.value & 1 and action == Action.OPEN:
            self.value -= 2 ** dir.value
        elif not (self.value >> dir.value & 1) and action == Action.CLOSE:
            self.value += 2 ** dir.value
        self.n, self.e, self.s, self.w =  self.hex_to_bool(self.value)

    def __get_open_wall(self) -> Dir:
        dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
        for dir in dirs:
            if self.value >> dir.value & 1:
                return dir

    def get_next_cell(self) -> 'Cell':
        all_neighbers = [self.top, self.right, self.bottom, self.left]
        return all_neighbers[self.__get_open_wall().value]

    def update_walls(self, open_from: Dir):
        self.edit_wall(open_from, Action.OPEN)
        for i in range(0, 4):
            if Dir(i) == open_from:
                self.edit_wall(open_from, Action.OPEN)
            else:
                self.edit_wall(Dir(i), Action.CLOSE)
