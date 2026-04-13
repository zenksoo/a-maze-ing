import sys
from mazegen import Maze, MazeGenerator
from config_parser import ConfigParser
from ascii_art import AsciiArt, ThemePicker
from common import Themes
from ascii_art.AsciiArt import print_blk


# def clear():
#     sys.stdout.write("\033[2J\033[H")
#     sys.stdout.flush()

# def display_all_themes(maze_width: int, theme: Themes) -> None:
#     themes = [t.name for t in Themes]
#     menu_colors = ThemePicker(theme)
#     TEXT, BUTTON, BG = menu_colors.menu_theme().values()
#     i = 0
#     for thm in themes:
#         print_blk(BG, 2 * 4)
#         print(BG, f"{TEXT}[{i}] - {thm}\033[49m", end="")
#         print_blk(BG, (maze_width * 6 + 3) - len(thm) - 7)
#         print_blk(BG, 2 * 4)
#         print()
#         i += 1
#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     print_blk(BG, 2 * 4)
#     return int(input(f"{BG}choise: "))

# def menu(maze_width: int, theme: Themes) -> None:
#     messages = [
#         "Re-generate a new maze and display it.",
#         "Show/Hide a valid shortest path from the entrance to the exit",
#         "set specific colours to display the “42” pattern",
#         "choise another theme"
#     ]
#     menu_colors = ThemePicker(theme)
#     TEXT, BUTTON, BG = menu_colors.menu_theme().values()

#     i = 0
#     for msg in messages:
#         print_blk(BG, 2 * 4)
#         print(BG, f"{TEXT}[{i}] - {msg}\033[49m", end="")
#         print_blk(BG, (maze_width * 6 + 3) - len(msg) - 7)
#         print_blk(BG, 2 * 4)
#         print()
#         i += 1

#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     print_blk(BG, 2 * 4)
#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     print_blk(BG, ((2 * 4) * 2) + (maze_width * 6) + 3), print()
#     return int(input(f"{BG}choise: "))


# def display_road(maze: MazeGenerator, change_mode) -> None:
#     with open("output_file.txt", 'r') as f:
#         ascii_art = AsciiArt(f, maze.theme)
#         if change_mode:
#             if maze.show_path:
#                 ascii_art.render(False)
#                 maze.show_path = False
#             else:
#                 ascii_art.render(True)
#                 maze.show_path = True
#         else:
#             ascii_art.render(maze.show_path)

def a_maze_ing(theme: Themes = Themes.CRIMSON):
    if len(sys.argv) != 2:
        raise ValueError("argvvvv")
    with open(sys.argv[1], 'r') as f:
        maze = MazeGenerator(ConfigParser.parse(f), theme)

    print(maze.seed)

    maze.generate()
    ascii_art = AsciiArt(maze.maze, maze.theme)
    ascii_art.render(True)

    # action = menu(maze.width, maze.theme)
    # while action != 5:
    #     if action == 0:
    #         clear()
    #         a_maze_ing(maze.theme)
    #     elif action == 1:
    #         while action == 1:
    #             clear()
    #             display_road(maze, True)
    #             action = menu(maze.width, maze.theme)
    #     elif action == 3:
    #         action = display_all_themes(maze.width, maze.theme)
    #         maze.theme = Themes(action)
    #         display_road(maze, False)
    #     else:
    #         break

if __name__ == "__main__":
    a_maze_ing()
