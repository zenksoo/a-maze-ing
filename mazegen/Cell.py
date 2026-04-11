from common import Dir, Action


class Cell:
    def __init__(self) -> None:
        self.top:       Cell = None
        self.right:      Cell = None
        self.bottom:    Cell = None
        self.left:      Cell = None

        self.hex: int = 15
        self.x: int = 0
        self.y: int = 0

    def __edit_wall(self, dir: Dir, action: Action):
        if self.hex >> dir.value & 1 and action == Action.open:
            self.hex -= 2 ** dir.value
        elif not (self.hex >> dir.value & 1) and action == Action.CLOSE:
            self.hex += 2 ** dir.value

    def __get_open_wall(self) -> Dir:
        dirs = [Dir.N, Dir.E, Dir.S, Dir.W]
        for dir in dirs:
            if self.hex >> dir.value & 1:
                return dir

    def get_next_cell(self) -> 'Cell':
        all_neighbers = [self.top, self.right, self.bottom, self.left]
        return all_neighbers[self.__get_open_wall().value]

    def update_walls(self, open_from: Dir):
        self.__edit_wall(open_from, Action.OPEN)
        for i in range(0, 4):
            if Dir(i) == open_from:
                self.__edit_wall(open_from, Action.OPEN)
            else:
                self.__edit_wall(Dir(i), Action.CLOSE)
