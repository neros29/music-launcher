import os
import string
from typing import Dict, List, Optional
from copy import deepcopy
import time
from pytui import Label, Tui, Surface
from listWidget import ListWidget, Token, Element
from queryRunner import QueryRunner
from query import Query, Playlist, Data, Song


class InputWidget:
    def __init__(self, surface: Surface, bg: List, fg: List):
        self.surface = surface
        self.fg = fg
        self.bg = bg
        self.special_keys = {
            chr(127): "Backspace",
            chr(10): "Enter",
            "Left": "Left",
            "Right": "Right",
            "Up": "Up",
            "Down": "Down"
        }
        self.curser_shown = True
        self.last_time = time.time()
        self.keys = self._register_keys()

    def _register_keys(self):
        keys = list(string.printable)
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs + keys)
        return keys

    def _get_input(self):
        inputs = []
        for key in self.special_keys:
            if self.surface.get_event(key):
                inputs.append(self.special_keys[key])
        for key in self.keys:
            if self.surface.get_event(key):
                inputs.append(key)
        return inputs
    def clear(self):
        self.surface.fill_ch(" ")
        self.surface.fill_fg(self.fg[0], self.fg[1], self.fg[2])
        self.surface.fill_bg(self.bg[0], self.bg[1], self.bg[2])

    def render_text(self, tokens: List[Token]):           
        self.clear()
        for num, token in enumerate(tokens, start=0):
            if num < self.surface.size()[0]:
                color = token.color
                self.surface[num].set_fg(color[0][0], color[0][1], color[0][2])
                self.surface[num].set_bg(color[1][0], color[1][1], color[1][2])
                if token.type == "cursor":
                    self._toggle_curser_shown(token.flash)
                    if self.curser_shown:
                        self.surface[num].set_ch(token.character)
                else:
                    self.surface[num].set_ch(token.character)

    def _toggle_curser_shown(self, flash_time: Optional[float]):
        if flash_time == None:
            self.curser_shown = True
            return 
        if time.time() >= self.last_time + flash_time:
            self.curser_shown = False if self.curser_shown else True
            self.last_time = time.time()

    def update(self, tokens: List):
        self.render_text(tokens)
        return self._get_input()
        
