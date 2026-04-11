from common import Themes
from typing import Dict, List
import tomllib
from pathlib import Path

PARENT_PATH = Path(__file__).parent


def color_picker() -> Dict:
    pass

class ThemePicker:
    def __init__(self, theme: Themes) -> None:
        theme_path: str = f"{PARENT_PATH}/themes/{theme.name.lower()}.toml"

        with open(theme_path, 'rb') as f:
            self.thm = tomllib.load(f)

    @staticmethod
    def __get_rgb_bg(hex_color: str) -> str:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        return f"\033[48;2;{r};{g};{b}m"

    def maze_theme(self) -> Dict:
        maze_color: Dict = self.thm["maze_colors"]
        for key, val in maze_color.items():
            maze_color[key] = self.__get_rgb_bg(val)

        return maze_color

    def locations_theme(self) -> Dict:
        pass
