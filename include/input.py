from os import system
import string
from sys import path
from typing import Dict, List
from wcwidth import wcwidth
import time
path.append("pytui/")
from pytui import Label, Tui, Surface, Character


class Input:
    def __init__(self, surface: Surface, bg: List, fg: List):
        self.surface = surface
        self.fg = fg
        self.bg = bg
        self.size = self.surface.size()
        self.offset = self.surface.offset()
        self.text = ""
        self.special_keys = {
            chr(127): "Backspace",
        }
        self.curser_shown = False
        self.last_time = time.time()
        self.keys = self._register_keys()
        self.colors = []

    def _register_keys(self):
        keys = list(string.printable)
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs + keys)
        return keys

    def _get_input(self):
        inputs = []
        for key in self.keys:
            if self.surface.get_event(key):
                inputs.append(key)
        for key in self.special_keys:
            if self.surface.get_event(key):
                inputs.append(self.special_keys[key])
        return inputs

    def render_text(self):           
        self.surface.fill_ch(" ")
        self.surface.fill_fg(self.fg[0], self.fg[1], self.fg[2])
        self.surface.fill_bg(self.bg[0], self.bg[1], self.bg[2])
        for i in range(0, len(self.text)):
            if i < self.surface.size()[0]:
                color = self.colors[i]
                if color is None:
                    color = [self.fg, self.bg]
                if color is not None:
                    self.surface[i].set_fg(color[0][0], color[0][1], color[0][2])
                    self.surface[i].set_bg(color[1][0], color[1][1], color[1][2])
                else:
                    self.surface[i].set_fg(15, 15, 15)
                    self.surface[i].set_bg(200, 200, 200)
                self.surface[i].set_ch(self.text[i])
        if len(self.text) < self.surface.size()[0]:
            self.surface[len(self.text)].set_fg(50, 50, 255)
            self.surface[len(self.text)].set_bg(200, 200, 200)
            if self.curser_shown:
                self.surface[len(self.text)].set_ch("|")

    def curser_flash(self):
        if time.time() >= self.last_time + .5:
            self.curser_shown = False if self.curser_shown else True
            self.last_time = time.time()

    def update(self, text: str, colors: list):
        self.text = text
        self.colors = colors
        assert len(self.text) == len(self.colors)
        self.curser_flash()
        self.render_text()
        return self._get_input()
        

if __name__ == "__main__":
    def parse_text(text: str, key_words: Dict): 
        colors = [None for _ in range(0, len(text))]
        words = text.split(" ")
        index = 0
        for word in words:
            for key_word in key_words:
                if word == key_word:
                    for i in range(0, len(word)):
                        colors[index + i] = key_words[key_word]
            index += len(word) + 1
        return colors

    tui = Tui()
    size = [100, 3]
    offset = [(tui.get_screen_size()[0] - size[0]) // 2, (tui.get_screen_size()[1] - size[1]) // 2]

    background: Surface = tui.append(size, offset, " ", 0)
    background.fill_bg(200, 200, 200)

    size2 = [size[0] - 2, 1]
    offset2 = [(tui.get_screen_size()[0] - size2[0]) // 2, (tui.get_screen_size()[1] - size2[1]) // 2]
    surface: Surface = tui.append(size2, offset2, " ", 1)
    bg = [200, 200, 200]
    fg = [15, 15, 15]
    surface.fill_bg(bg[0], bg[1], bg[2])
    surface.fill_fg(fg[0], fg[1], fg[2])
    input = Input(surface, bg, fg)
    system("clear")
    key_words = {
            "if": [[255, 0, 0], bg],
            "for": [[0, 255, 0], bg],
            "else": [[0, 0, 255], bg],
            "clear": [bg, fg]
            }
    text = ""
    while True:
        try:
            values = input.update(text, parse_text(text, key_words))
            for key in values:
                if key == "Backspace":
                    text = text[:-1]
                    continue
                text += key
            tui.update_screen()
        except KeyboardInterrupt:
            break
