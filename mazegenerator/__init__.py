from mazegenerator.maze_generator import MazeGenerator
from mazegenerator.MazeRenderer import MazeRenderer, ThemePicker
from mazegenerator.Menu import Menu


THEMS = [
    "royal_depth",
    "dark_forest",
    "deep_ocean",
    "ember_core",
    "midnight_blue",
    "steel_industrial"
    ]

__all__ = ["MazeGenerator", "Maze",
           "MazeRenderer", "ThemePicker", "Menu"]
