import termios
import sys
import tty


try:
    from pydantic import ValidationError
    from mazegenerator import MazeGenerator, Menu, MazeConfig, THEMS
    from mazegenerator import MazeRenderer
except ImportError as e:
    print("\033[41m  ERROR  \033[49m ", end="")
    print(f"\033[31mMissing dependency:\033[0m {e}")
    print("Run: make install")
    sys.exit(1)


SAVE_CURSOR = "\033[s"
RESTORE_CURSOR = "\033[u"
CLEAR_LINE = "\033[K"
CLEAR_DOWN = "\033[J"


def get_key() -> str:
    fd = sys.stdin.fileno()
    original = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, original)
    return ch


def get_config() -> MazeConfig:
    """ Parse the maze configuration from a file specified as a command-line argument.
    The configuration file should be in key=value format, containing required keys:
    WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT.
    """
    argc = len(sys.argv)
    if argc != 2:
        raise ValueError("Usage: python a-maze-ing.py <config_file>")
    try:
        with open(sys.argv[1]) as f:
            return MazeConfig.from_file(f)
    except FileNotFoundError:
        raise ValueError(f"Config file '{sys.argv[1]}' not found.")
    except PermissionError:
        msg = f"Error opening config file `{sys.argv[1]}`"
        raise ValueError(msg, "Permission denied.")
    except OSError as e:
        raise ValueError(f"Error opening config file '{sys.argv[1]}': {e}")


def start_printing() -> None:
    print(RESTORE_CURSOR, end='', flush=True)
    print(CLEAR_DOWN, end='', flush=True)
    print("\033[?25h")


def render_maze(maze: MazeGenerator, show_path: bool = False) -> None:
    art = MazeRenderer(maze.maze, maze.theme)
    art.render(show_path)


def display_menu(theme: str, type: int = 0) -> None:
    """Display the main menu.

    Args:
        theme (str): The current theme.
        type (int, optional): The type of menu to display. Defaults to 0.
    """
    menu = Menu(theme)
    if type == 1:
        for i, theme_name in zip(range(0, len(THEMS)), THEMS):
            menu.banner(f"[{i}] {theme_name.lower()}  ")
            print("    ", end="")
        menu.banner("[q] Exit")
    else:
        all_options = {
            "[r]": "Re-generate",
            "[R]": "Re-Gen by Animation",
            "[s]": "Show Solution",
            "[S]": "Animated Solution",
            "[c]": "Change Theme",
            "[W]": "Write To File",
            "[q]": "Exit"
        }
        for key, val in all_options.items():
            menu.banner(f"{key} {val}")
            print(end="    ")
    print("\n\n Action : ", end="")


def change_theme_menu(theme: str) -> str | None:
    """Display a menu for changing the maze theme.

    Args:
        theme (str): The current theme.

    Returns:
        str | None: The new theme if selected, or None if the user chooses to exit.
    """
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


def re_generate_by_animation(maze: MazeGenerator) -> None:
    """ Re-generate the maze with animation. If the maze is large, prompt the user for confirmation.

    Args:
        maze (MazeGenerator): The maze generator instance.
    """
    animate = 'y'
    if len(maze.maze) * len(maze.maze[0]) > 1000:
        start_printing()
        print("\033[31mthe size of maze is large,",
              "continue ? (y/n): \033[39m")
        animate = get_key()
    if (animate.lower() == "y" or
       len(maze.maze) * len(maze.maze[0]) <= 1000):
        print(CLEAR_DOWN, end='', flush=True)
        maze.with_animation = True
        maze.generate()
        render_maze(maze)
        maze.with_animation = False


def main_menu(maze: MazeGenerator, art: MazeRenderer) -> None:
    """Display the main menu and handle user input.

    Args:
        maze (MazeGenerator): The maze generator instance.
        art (MazeRenderer): The maze renderer instance.
    """
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
        elif ch == "R":
            re_generate_by_animation(maze)

        elif ch == "s":
            if show_path:
                show_path = False
            else:
                show_path = True
            render_maze(maze, show_path)
        elif ch == "S":
            maze.find_and_mark_solution(True)

        elif ch == "c":
            new_theme = change_theme_menu(maze.theme)
            if new_theme:
                maze.theme = new_theme
                render_maze(maze)

        elif ch.lower() == 'w':
            maze.save_maze_to_file()

        elif ch.lower() == 'q':
            print(CLEAR_DOWN, end='')
            sys.stdout.write("\033[0J\033[H")
            break


if __name__ == "__main__":
    sys.stdout.write("\033[0J\033[H")
    print(CLEAR_LINE, end='', flush=True)

    try:
        mzconf = get_config()
        print(mzconf)
    except ValidationError as e:
        print("\033[41m  ERROR  \033[49m ", end="")
        print(f"Maze config Error: {e.errors()[0]["msg"]}")
        exit(1)
    except ValueError as e:
        print("\033[41m  ERROR  \033[49m ", end="")
        print(f"Maze config Error: {e}")
        exit(1)

    try:
        maze = MazeGenerator.from_object(mzconf, THEMS[0], False)
        maze.generate()
        art = MazeRenderer(maze.maze, maze.theme)
        art.render(False)
        main_menu(maze, art)
    except (Exception, IOError) as e:
        print("\033[41m  ERROR  \033[49m ", end="")
        print(e)
        exit(1)
