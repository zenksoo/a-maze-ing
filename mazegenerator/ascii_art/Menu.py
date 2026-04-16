from .ThemePicker import ThemePicker
from typing import Dict, Any


class Menu:
    def __init__(self, theme: str) -> None:
        self.theme_name: str = theme
        self.theme: Dict[Any, Any] = {}
        self.bg = None
        self.text = None
        self.button = None
        self.init_theme()

    def init_theme(self) -> None:
        picker = ThemePicker(self.theme_name)
        self.theme = picker.menu_theme()

    def banner(self, txt: str, end: bool = False) -> None:
        print(f"{self.theme["bg"]}{self.theme["text"]} ",
              f"{txt}  \033[49m", end="   ")
