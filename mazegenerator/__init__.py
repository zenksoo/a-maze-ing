from mazegenerator.MazeGenerator import MazeGenerator
from mazegenerator.MazeRenderer import MazeRenderer, ThemePicker, Menu
from mazegenerator.MazeConfig import MazeConfig


THEMS = [
    "royal_depth",
    "dark_forest",
    "deep_ocean",
    "ember_core",
    "midnight_blue",
    "steel_industrial"
    ]

__all__ = ["MazeGenerator", "Maze", "MazeConfig",
           "MazeRenderer", "ThemePicker", "Menu"]
