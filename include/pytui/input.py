from os import system
from sys import path
from typing import List
from wcwidth import wcwidth

path.append("include/pytui/")
from pytui import Label, Tui, Surface, Character


class Input:
    def __init__(self, surface: Surface, text: str = ""):
        self.surface = surface
        self.size = self.surface.size()
        self.offset = self.surface.offset()
        self.text = text
        self.special_keys = {
            chr(127): self._backspace,
            "Up": exit,
        }
        self.keys = self._register_keys()

    def _backspace(self):
        self.text = self.text[:-1]

    def _register_keys(self):
        keys = [" "]
        for ch in range(ord("a"), ord("z") + 1):
            keys.append(chr(ch))
        self.surface.register_keys(keys)
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs)

        return keys

    def _get_input(self):
        for key in self.keys:
            if self.surface.get_event(key):
                self.text += key
        for s_ch in self.special_keys:
            if self.surface.get_event(s_ch):
                self.special_keys[s_ch]()
    def render_text(self):           
        self.surface.fill_ch(" ")
        for i in range(0, len(self.text) - 1):
            self.surface[i].set_ch(self.text[i])

    def get_value(self):
        return self.text

    def update(self):
        self._get_input()
        self.render_text()
        
        




if __name__ == "__main__":
    tui = Tui()
    offset = [5, 5]
    surface: Surface = tui.append([50, 11], offset, " ", 0)
    surface.fill_bg(255, 0, 0)
    input = Input(surface)
    system("clear")
    while True:

        value = input.update()
        tui.update_screen()


    print(f"width {wcwidth('🧮')}")




