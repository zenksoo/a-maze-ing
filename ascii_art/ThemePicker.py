from common import Themes
from typing import Dict
import tomllib
from pathlib import Path


PARENT_PATH = Path(__file__).parent


class ThemePicker:
    def __init__(self, theme: Themes) -> None:
        theme_path: str = f"{PARENT_PATH}/themes/{theme.name.lower()}.toml"
        with open(theme_path, 'rb') as f:
            self.theme = tomllib.load(f)

    @staticmethod
    def __get_rgb_bg(hex_color: str) -> str:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        return f"\033[48;2;{r};{g};{b}m"

    @staticmethod
    def __get_text_color(hex_color: str) -> str:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        return f"\033[38;2;{r};{g};{b}m"

    def edit_hex_theme(self, theme: Dict) -> None:
        for key, val in theme.items():
            theme[key] = self.__get_rgb_bg(val)

    def maze_theme(self) -> Dict:
        self.edit_hex_theme(self.theme["maze_colors"])
        return self.theme["maze_colors"]

    def locations_theme(self) -> Dict:
        self.edit_hex_theme(self.theme["locations"])
        return self.theme["locations"]

    def menu_theme(self) -> Dict:
        menu_colors = self.theme["menu_colors"]
        for key, val in menu_colors.items():
            if key == "bg":
                menu_colors[key] = self.__get_rgb_bg(val)
            else:
                menu_colors[key] = self.__get_text_color(val)
        return self.theme["menu_colors"]
