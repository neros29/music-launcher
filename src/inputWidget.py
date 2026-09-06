import string
from typing import  List, Optional
import time
from pytui import  Surface
from logging import getLogger

class Token:
    def __init__(self, fg, bg, ch, token_type="text", flash = None) -> None:
        self.color = [fg, bg]
        self.character = ch if len(ch) == 1 else ch[0]
        self.type = token_type
        self.flash = flash

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Token):
            colors = self.color == value.color
            characters = self.character == value.character
            types = self.type == value.type
            flashs = self.flash == value.flash
            return colors and characters and types and flashs
        return NotImplemented
    def __repr__(self):
        return self.character

class InputWidget:
    def __init__(self, surface: Surface, bg: List, fg: List, curser: Optional[Token] = None):
        self.surface = surface
        self.fg = fg
        self.bg = bg
        self.curser = curser if curser is not None else Token(self.bg, self.fg, " ")
        self.last_time = time.time()
        self.width, self.hight = self.surface.size()
        self.current_surf: List[Optional[Token]] = [None for _ in range(self.width) for _ in range(self.hight)]

    def render_text(self, tokens: List[Token], curser_pos: tuple[int, int]):           
        token_idx = 0
        for y in range(self.hight):
            for x in range(self.width):
                token = tokens[token_idx] if len(tokens) > token_idx else Token(self.fg, self.bg, " ")
                if x == curser_pos[0] and y == curser_pos[1]:
                    token.color = self.curser.color
                token_idx += 1
                idx = y * self.width + x
                color = token.color
                if self.current_surf[idx] != token:
                    self.surface[idx].set_fg(*color[0])
                    self.surface[idx].set_bg(*color[1])
                    self.surface[idx].set_ch(token.character)
                    self.current_surf[idx] = token
