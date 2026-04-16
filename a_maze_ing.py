from mazegen import MazeGenerator, AsciiArt, Menu
from mazegen.ascii_art import THEMS
import termios
import sys
import tty


SAVE_CURSOR = "\033[s"
RESTORE_CURSOR = "\033[u"
CLEAR_LINE = "\033[K"
CLEAR_DOWN = "\033[J"


def start_printing() -> None:
    print(RESTORE_CURSOR, end='', flush=True)
    print(CLEAR_DOWN, end='', flush=True)
    print("\033[?25h")


def render_maze(maze: MazeGenerator, show_path: bool = False) -> None:
    art = AsciiArt(open(maze.config["OUTPUT_FILE"], "r"), maze.theme)
    art.render(show_path)


def get_key() -> str:
    fd = sys.stdin.fileno()
    original = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, original)
    return ch


def display_menu(theme, type: int = 0):
    menu = Menu(theme)
    if type == 1:
        for i, theme_name in zip(range(0, len(THEMS)), THEMS):
            menu.banner(f"[{i}] {theme_name.lower()}")
        menu.banner("[q] Exit")
    else:
        menu.banner("\033[1m [r] Re-generate")
        menu.banner("[a] Maze Animation")
        menu.banner("[s] Show/Hide Path")
        menu.banner("[c] Change Theme")
        menu.banner("[q] Exit")
    print("\n\n")


def change_theme_menu(theme) -> str | None:
    while True:
        start_printing()
        display_menu(theme, 1)
        ch = get_key()
        if ch.lower() == "q":
            return None
        try:
            theme_idx = int(ch)
            if 0 > theme_idx or theme_idx >= len(THEMS):
                continue
            else:
                return THEMS[theme_idx]
        except ValueError:
            continue


def main_menu(maze: MazeGenerator, art: AsciiArt) -> None:
    show_path = False
    print(SAVE_CURSOR, end='', flush=True)
    while True:
        start_printing()
        display_menu(maze.theme)
        ch = get_key()
        if ch == "r":
            maze.with_animation = False
            maze.generate()
            render_maze(maze)
        elif ch == "a":
            animate = 'y'
            if len(maze.maze) * len(maze.maze[0]) > 1000:
                start_printing()
                print("\033[34mthe size of maze is large,",
                      "continue ? (y/n): \033[39m")
                animate = get_key()
            if (animate.lower() == "y"
               or len(maze.maze) * len(maze.maze[0]) <= 1000):
                print(CLEAR_DOWN, end='', flush=True)
                maze.with_animation = True
                maze.generate(maze.seed)
                render_maze(maze)
                maze.with_animation = False
        elif ch == "s":
            if show_path:
                show_path = False
            else:
                show_path = True
            render_maze(maze, show_path)
        elif ch == "c":
            new_theme = change_theme_menu(maze.theme)
            if new_theme:
                maze.theme = new_theme
                render_maze(maze)
        elif ch.lower() == 'q':
            print(CLEAR_DOWN, end='')
            sys.stdout.write("\033[0J\033[H")
            break


def a_maze_ing(theme: str):
    print(CLEAR_DOWN, end='', flush=True)
    sys.stdout.write("\033[0J\033[H")
    if len(sys.argv) != 2:
        raise ValueError("argvvvv")
    maze = MazeGenerator(sys.argv[1], theme, False)
    maze.generate()
    with open(maze.config["OUTPUT_FILE"], 'r') as f:
        art = AsciiArt(f, maze.theme)
        art.render(False)
    main_menu(maze, art)


if __name__ == "__main__":
    a_maze_ing(THEMS[0])
