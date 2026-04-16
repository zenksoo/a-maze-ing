from .ThemePicker import ThemePicker


class Menu:
    def __init__(self, theme: str) -> None:
        self.theme = theme
        self.bg = None
        self.text = None
        self.button = None
        self.init_theme()

    def init_theme(self) -> None:
        picker = ThemePicker(self.theme)
        self.theme = picker.menu_theme()

    def banner(self, txt: str, end: bool = False) -> None:
        print(f"{self.theme["bg"]}{self.theme["text"]} ",
              f"{txt}  \033[49m", end="   ")
