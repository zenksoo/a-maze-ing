from .MazeCell import MazeCell

def remove_bit(val, index) -> int:
    if val >> index & 1:
        val -= 2 ** index
    return val


def add_bit(val, index) -> int:
    if not (val >> index & 1):
        val += 2 ** index
    return val

def setup_cell_bits(cell: MazeCell, new_type: str) -> None:
    """
        (4 MSB) in first byte in cell.value represent type of the cell
            0001 : start
            0010 : end
            1111 : locked
            0011 : road
            1100 : origin
            0000 : normal cell
    """
    # binary of start: 0001 1111
    if new_type.lower() == 's':
        for i in range(5, 8):
            cell.value = remove_bit(cell.value, i)
        cell.value = add_bit(cell.value, 4)

    # binary of end: 0010 1111
    elif new_type.lower() == 'e':
        for i in range(6, 8):
            cell.value = remove_bit(cell.value, i)
        cell.value = add_bit(cell.value, 5)
        cell.value = remove_bit(cell.value, 4)

    # binary of locked: 1111 1111
    elif new_type.lower() == 'l':
        for i in range(4, 8):
            cell.value = add_bit(cell.value, i)

    # binary of Road: 0011 1111
    elif new_type.lower() == 'r':
        for i in range(4, 6):
            cell.value = add_bit(cell.value, i)
        for i in range(6, 8):
            cell.value = remove_bit(cell.value, i)

    # binary of origin: 1100 1111
    elif new_type.lower() == 'o':
        for i in range(4, 6):
            cell.value = remove_bit(cell.value, i)
        for i in range(6, 8):
            cell.value = add_bit(cell.value, i)
    # binary of normal: 0000 1111
    elif new_type.lower() == 'n':
        for i in range(4, 8):
            cell.value = remove_bit(cell.value, i)


def get_cell_type(cell: MazeCell) -> str:
        # binary of start: 0001 1111

    shifted_value = cell.value >> 4
    if shifted_value == 0b00000001:
        return 's'

    # binary of end: 0010 1111
    elif shifted_value == 0b00000010:
        return 'e'

    # binary of locked: 1111 1111
    elif shifted_value == 0b00001111:
        return 'l'

    # binary of Road: 0011 1111
    elif shifted_value == 0b00000011:
        return 'r'

    # binary of origin: 1100 1111
    elif shifted_value == 0b00001100:
        return 'o'

    # binary of normal: 0000 1111
    elif shifted_value == 0b00000000:
        return 'n'


def walls_value(cell: MazeCell) -> int:
    val = 0
    for i in range (0, 4):
        if (cell.value >> i & 1):
            val += 2 ** i
    return val


