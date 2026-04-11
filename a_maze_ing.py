import sys
from mazegen import Maze, MazeGenerator
from config_parser import ConfigParser
from ascii_art import *
from common import Themes

if __name__ == "__main__":
    with open("output_file.txt", 'r') as f:
        ascii_art = AsciiArt(f, Themes.SANDSTORM)
        ascii_art.render()
