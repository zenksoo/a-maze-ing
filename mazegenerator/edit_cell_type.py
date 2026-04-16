from .MazeCell import MazeCell


def remove_bit(val: int, index: int) -> int:
    if val >> index & 1:
        val -= 2 ** index
    return val


def add_bit(val: int, index: int) -> int:
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
    # binary of locked: 1111 ****
    if new_type.lower() == 'l':
        for i in range(4, 8):
            cell.value = add_bit(cell.value, i)

    # binary of origin: 1000 ****
    elif new_type.lower() == 'o':
        for i in range(4, 7):
            cell.value = remove_bit(cell.value, i)
        cell.value = add_bit(cell.value, 7)

    # binary of start: 00001 ****
    elif new_type.lower() == 's':
        cell.value = add_bit(cell.value, 4)
        for i in range(5, 8):
            cell.value = remove_bit(cell.value, i)

    # binary of end: 0010 ****
    elif new_type.lower() == 'e':
        cell.value = remove_bit(cell.value, 4)
        cell.value = add_bit(cell.value, 5)
        cell.value = remove_bit(cell.value, 6)
        cell.value = remove_bit(cell.value, 7)


    # binary of Road: 0011 ****
    elif new_type.lower() == 'r':
        for i in range(4, 6):
            cell.value = add_bit(cell.value, i)
        cell.value = remove_bit(cell.value, 6)
        cell.value = remove_bit(cell.value, 7)

    # binary of normal: 0000 ****
    elif new_type.lower() == 'n':
        for i in range(4, 8):
            cell.value = remove_bit(cell.value, i)

    # binary of visited: 1100 ****
    elif new_type.lower() == 'v':
        cell.value  = remove_bit(cell.value, 4)
        cell.value  = remove_bit(cell.value, 5)
        cell.value  = add_bit(cell.value, 6)
        cell.value  = add_bit(cell.value, 7)


def get_cell_type(cell: MazeCell) -> str | None:
    """
        get the type of cell as single char
    """
    # binary of locked 1111 ****
    if cell.value >> 4 == 0b1111:
        return 'l'

    # binary of origin 1000 ****
    elif cell.value >> 4 == 0b1000:
        return 'o'

    # binary of start: 0001 ****:
    elif cell.value >> 4 == 0b0001:
        return 's'

    # binary of end: 0010 ****
    elif cell.value >> 4 == 0b0010:
        return 'e'

    # binary of Road: 0011 ****
    elif cell.value >> 4 == 0b0011:
        return 'r'

    # binary of normal: 0000 ****
    elif cell.value >> 4 == 0b0000:
        return 'n'

    elif cell.value >> 4 == 0b1100:
        return 'v'

    return None


def walls_value(cell: MazeCell) -> int:
    val = 0
    for i in range(0, 4):
        if (cell.value >> i & 1):
            val += 2 ** i
    return val
