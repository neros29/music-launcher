from typing import List
from pytui import Label, Surface, Tui
import time
import os

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

class Element:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Element):
            return self.tokens == value.tokens
        return NotImplemented
    def __iter__(self):
        for i in self.tokens:
            yield i
            

class ListWidget:
    def __init__(self, surface: Surface, fg: List[int], bg: List[int]) -> None:
        self.surface: Surface = surface
        self.fg = fg
        self.bg = bg
        self.current_elements: List[Element] = []

    def clear(self):
        self.surface.fill_ch(" ")
        self.surface.fill_bg(self.bg[0], self.bg[1], self.bg[2])
        self.surface.fill_fg(self.fg[0], self.fg[1], self.fg[2])

    def _render(self, elements: List[Element]):
        self.clear()
        for y, element in enumerate(elements):
            if y > self.surface.size()[1]:
                break
            for x, token in enumerate(element):
                if x < self.surface.size()[0]:
                    index = y * self.surface.size()[0] + x
                    color = token.color
                    self.surface[index].set_fg(color[0][0], color[0][1], color[0][2])
                    self.surface[index].set_bg(color[1][0], color[1][1], color[1][2])
                    self.surface[index].set_ch(token.character)

    def update(self, elements: List[Element]):
        if elements != self.current_elements:
            self._render(elements)
            self.current_elements = elements

