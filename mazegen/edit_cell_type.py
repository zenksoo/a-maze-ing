from .MazeCell import MazeCell


def remove_bit(val, index) -> int:
    if val >> index & 1:
        val -= 2 ** index
    return val


def add_bit(val, index) -> int:
    if not (val >> index & 1):
        val += 2 ** index
    return val


def setup_cell_type(cell: MazeCell, new_type: str) -> None:
    """
        set the type of cell
        (left 2 bits in 4 MSB) in first byte in
        cell.value represent type of the cell
            **01 **** : start
            **10 **** : end
            **11 **** : road
            01** **** : locked
            10** **** : origin
            00** **** : normal

    """
    # binary of start: 01** ****
    if new_type.lower() == 'l':
        cell.value = add_bit(cell.value, 6)
        cell.value = remove_bit(cell.value, 7)

    # binary of origin: 10** ****
    elif new_type.lower() == 'o':
        cell.value = add_bit(cell.value, 7)
        cell.value = remove_bit(cell.value, 6)

    # binary of start: **01 ****
    elif new_type.lower() == 's':
        cell.value = remove_bit(cell.value, 5)
        cell.value = add_bit(cell.value, 4)

    # binary of end: **10 ****
    elif new_type.lower() == 'e':
        cell.value = remove_bit(cell.value, 4)
        cell.value = add_bit(cell.value, 5)

    # binary of Road: **11 ****
    elif new_type.lower() == 'r':
        for i in range(4, 6):
            cell.value = add_bit(cell.value, i)

    # binary of normal: 00** ****
    elif new_type.lower() == 'n':
        cell.value = remove_bit(cell.value, 6)
        cell.value = remove_bit(cell.value, 7)


def get_cell_type(cell: MazeCell) -> str:
    """
        get the type of cell as single char
    """
    # binary of locked 01** ****
    if cell.value >> 6 == 0b00000001:
        return 'l'

    # binary of origin 10** ****
    elif cell.value >> 7 == 0b00000001:
        return 'o'

    # binary of start: **01 ****:
    elif cell.value >> 4 == 0b00000001:
        return 's'

    # binary of end: **10 ****
    elif cell.value >> 4 == 0b00000010:
        return 'e'

    # binary of Road: **11 ****
    elif cell.value >> 4 == 0b00000011:
        return 'r'

    # binary of normal: 00** ****
    elif cell.value >> 6 == 0b00000000:
        return 'n'


def walls_value(cell: MazeCell) -> int:
    val = 0
    for i in range(0, 4):
        if (cell.value >> i & 1):
            val += 2 ** i
    return val
