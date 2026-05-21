from os import system
import string
from typing import Dict, List, Optional
import json
import time

from sys import path
path.append("include/pytui/")
from pytui import Label, Tui, Surface, Character

class Token:
    def __init__(self, fg, bg, ch, token_type="text", flash = None) -> None:
        self.color = [fg, bg]
        self.character = ch
        self.type = token_type
        self.flash = flash

class Input:
    def __init__(self, surface: Surface, bg: List, fg: List):
        self.surface = surface
        self.fg = fg
        self.bg = bg
        self.special_keys = {
            chr(127): "Backspace",
            chr(10): "Enter"
        }
        self.curser_shown = True
        self.last_time = time.time()
        self.keys = self._register_keys()
        self.current_tokens: List[Token] = []

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
        if tokens != self.current_tokens:
            self.render_text(tokens)
            self.current_tokens = tokens
        return self._get_input()
        

if __name__ == "__main__":
    from parser import Parser
    file = open("log.txt", "a")
    parser = Parser()

    def parse_text(text: str, key_words: Dict): 
        words = parser._first_pass(text)
        tokens = parser._secound_pass(parser._first_pass(text))
        results: List[Token] = []
        color = [fg, bg]
        for word in words:
            for token in tokens:
                if "key" in token and token["key"] in word:
                    key_word = "songs"
                    if token["key"] in parser.type_key_words:
                        key_word = "type"
                    color = key_words[key_word]
                    break
                elif word in parser.operators:
                    color = key_words["operator"]
                    break
                else:
                    color = [fg, bg]
            for ch in word:
                results.append(Token(color[0], color[1], ch))
        results.append(Token(fg, bg, "|", token_type="cursor", flash=0.5))
        return results

    def get_music(text: str, last_text):
        ast = parser.parse(text)
        if ast.__repr__() != last_text:
            background.fill_ch(" ")
            if ast == None:
                lab.set_text("None")
                last_text = "None"
            else:
                lab.set_text(ast.__repr__())
                last_text = ast.__repr__()
            lab.update()
        return last_text

    tui = Tui()
    size = [200, 3]
    offset = [(tui.get_screen_size()[0] - size[0]) // 2, (tui.get_screen_size()[1] - size[1]) // 2]
    background: Surface = tui.append(size, offset, " ", 0)
    background.fill_bg(200, 200, 200)
    background.fill_fg(5, 5, 5)
    lab = Label(background, "Hello wold", [1, 2])

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
            "songs": [[255, 0, 0], bg],
            "type": [[0, 255, 0], bg],
            "operator": [[0, 0, 255], bg]
            }
    text = ""
    last_text = "" 
    running = True
    while running:
        try:
            values = input.update(parse_text(text, key_words))
            for key in values:
                if key == "Backspace":
                    text = text[:-1]
                    continue
                if key == "Enter":
                    running = False
                text += key
            last_text = get_music(text, last_text)
            tui.update_screen()
        except KeyboardInterrupt:
            break
    file.close()
