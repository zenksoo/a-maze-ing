from .MazeCell import MazeCell


def clear_bit(val: int, index: int) -> int:
    """ Clear the bit at the specified index in the given integer value.

    Args:
        val (int): The integer value.
        index (int): The index of the bit to clear.

    Returns:
        int: The modified integer value.
    """
    if val >> index & 1:
        val -= 2 ** index
    return val


def set_bit(val: int, index: int) -> int:
    """ Set the bit at the specified index in the given integer value.

    Args:
        val (int): The integer value.
        index (int): The index of the bit to set.

    Returns:
        int: The modified integer value.
    """

    if not (val >> index & 1):
        val += 2 ** index
    return val


def set_cell_type(cell: MazeCell, cell_type: str) -> None:
    """
        Encode a cell type into bits 4-7 of cell.value.

        The four most-significant bits of the first
        byte encode type and access:

            Bits 7-4   Type
            --------   ----
            0000       normal   (n)
            0001       start    (s)
            0010       end      (e)
            0011       road     (r)
            1000       origin   (o)
            1100       visited  (v)
            1111       locked   (l)

        Args:
            cell:      The MazeCell to modify in place.
            cell_type: Single character — one of
            'n', 's', 'e', 'r', 'o', 'v', 'l'.

        Raises:
            ValueError: If cell_type is not a recognised character.
    """
    # binary of locked: 1111 ****
    if cell_type.lower() == 'l':
        for i in range(4, 8):
            cell.value = set_bit(cell.value, i)

    # binary of origin: 1000 ****
    elif cell_type.lower() == 'o':
        for i in range(4, 7):
            cell.value = clear_bit(cell.value, i)
        cell.value = set_bit(cell.value, 7)

    # binary of start: 00001 ****
    elif cell_type.lower() == 's':
        cell.value = set_bit(cell.value, 4)
        for i in range(5, 8):
            cell.value = clear_bit(cell.value, i)

    # binary of end: 0010 ****
    elif cell_type.lower() == 'e':
        cell.value = clear_bit(cell.value, 4)
        cell.value = set_bit(cell.value, 5)
        cell.value = clear_bit(cell.value, 6)
        cell.value = clear_bit(cell.value, 7)

    # binary of Road: 0011 ****
    elif cell_type.lower() == 'r':
        for i in range(4, 6):
            cell.value = set_bit(cell.value, i)
        cell.value = clear_bit(cell.value, 6)
        cell.value = clear_bit(cell.value, 7)

    # binary of normal: 0000 ****
    elif cell_type.lower() == 'n':
        for i in range(4, 8):
            cell.value = clear_bit(cell.value, i)

    # binary of visited: 1100 ****
    elif cell_type.lower() == 'v':
        cell.value = clear_bit(cell.value, 4)
        cell.value = clear_bit(cell.value, 5)
        cell.value = set_bit(cell.value, 6)
        cell.value = set_bit(cell.value, 7)
    else:
        raise ValueError(f"Unknown cell type: '{cell_type}'")


def get_cell_type(cell: MazeCell) -> str | None:
    """ Decode the cell type from bits 4-7 of cell.value.

    Args:
        cell (MazeCell): The maze cell to decode.

    Returns:
        str | None: The cell type as a single character
        ('n', 's', 'e', 'r', 'o', 'v', 'l'),
        or None if the type is unrecognized.
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


def get_wall_bits(cell: MazeCell) -> int:
    """ Get the wall bits (bits 0-3) from cell.value.

    Args:
        cell (MazeCell): The maze cell from which to extract wall bits.

    Returns:
        int: The wall bits as an integer.
    """

    val = 0
    for i in range(0, 4):
        if (cell.value >> i & 1):
            val += 2 ** i
    return val
