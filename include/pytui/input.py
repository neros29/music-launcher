from os import system
import string
from sys import path
from typing import List
from wcwidth import wcwidth
import time
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
            "F1": self._exit
        }
        self.curser_shown = False
        self.last_time = time.time()
        self.keys = self._register_keys()
        self.exit = False

    def _exit(self):
        self.text = self.text[:-1]
        self.exit = True

    def _backspace(self):
        self.text = self.text[:-1]

    def _register_keys(self):
        keys = list(string.printable)
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs + keys)
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
        self.surface.fill_fg(15, 15, 15)
        self.surface.fill_bg(200, 200, 200)
        for i in range(0, len(self.text)):
            if i < self.surface.size()[0]:
                if self.text[i] == "s":
                    self.surface[i].set_fg(255, 15, 15)
                    self.surface[i].set_bg(200, 200, 200)
                else:
                    self.surface[i].set_fg(15, 15, 15)
                    self.surface[i].set_bg(200, 200, 200)
                self.surface[i].set_ch(self.text[i])
        if len(self.text) < self.surface.size()[0]:
            self.surface[len(self.text)].set_fg(50, 200, 50)
            self.surface[len(self.text)].set_bg(200, 200, 200)
            if self.curser_shown:
                self.surface[len(self.text)].set_ch("|")

    def curser_flash(self):
        if time.time() >= self.last_time + .5:
            self.curser_shown = False if self.curser_shown else True
            self.last_time = time.time()

    def get_value(self):
        return self.text

    def update(self):
        self._get_input()
        self.curser_flash()
        self.render_text()
        return self.exit
        
        




if __name__ == "__main__":
    tui = Tui()
    size = [100, 11]
    offset = [(tui.get_screen_size()[0] - size[0]) // 2, (tui.get_screen_size()[1] - size[1]) // 2]

    background: Surface = tui.append(size, offset, " ", 0)
    background.fill_bg(15, 15, 15)

    size2 = [size[0] - 2, 1]
    offset2 = [(tui.get_screen_size()[0] - size2[0]) // 2, (tui.get_screen_size()[1] - size2[1]) // 2]
    surface: Surface = tui.append(size2, offset2, " ", 1)
    surface.fill_bg(200, 200, 200)
    surface.fill_fg(15, 15, 15)
    input = Input(surface)
    system("clear")
    while True:
        value = input.update()
        if value:
            break
        tui.update_screen()


    print(f"width {wcwidth('🧮')}")




