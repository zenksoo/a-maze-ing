import sys
from mazegen import MazeGenerator
from config_parser import ConfigParser
from ascii_art import AsciiArt
from common import Themes


def a_maze_ing(theme: Themes = Themes.ROYAL_PURPLE):
    if len(sys.argv) != 2:
        raise ValueError("argvvvv")
    with open(sys.argv[1], 'r') as f:
        maze = MazeGenerator(ConfigParser.parse(f), theme, False)

    # maze.theme = Themes.LAVA
    maze.generate()
    ascii_art = AsciiArt(maze.maze, maze.theme)
    ascii_art.render(False)


if __name__ == "__main__":
    a_maze_ing(Themes.LAVA)
    # with open("test.txt") as f:
    #     art = AsciiArt(f, Themes.LAVA)
    #     art.render(True)
