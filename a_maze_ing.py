import sys
from mazegen import MazeGenerator
from config_parser import ConfigParser
from ascii_art import AsciiArt


THEMS = []

def a_maze_ing(theme: str):
    if len(sys.argv) != 2:
        raise ValueError("argvvvv")
    with open(sys.argv[1], 'r') as f:
        maze = MazeGenerator(ConfigParser.parse(f), theme, False)

    # maze.theme = Themes.LAVA
    maze.generate()
    ascii_art = AsciiArt(maze.maze, maze.theme)
    ascii_art.render(False)
    print(maze.seed, file=open("seed.log", 'w'))


if __name__ == "__main__":
    # a_maze_ing("LAVA")
    with open("output_file.txt") as f:
        art = AsciiArt(f, "lava")
        art.render(False)
