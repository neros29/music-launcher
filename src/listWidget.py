from typing import List
from pytui import Label, Surface, Tui
import time
import os

            

class ListWidget:
    def __init__(self, surface: Surface, surface1: Surface, fg: List[int], bg: List[int]) -> None:
        self.surface: Surface = surface
        self.surface1: Surface = surface1
        self.surface.offset()
        self.surface1.fill_bg(0x42, 0x3e, 0x58)
        self.fg = fg
        self.bg = bg
        self.current_elements: List[str] = []
        self.lab = Label(self.surface, "", [0, 0])
        self.bottom = 0
        self.margin = 5

    def clear(self):
        text = "\n".join([" " * self.surface.size()[0] for _ in range(self.surface.size()[1])])
        self.lab.set_text(text)

    def _render(self, elements: List[str], selected):
        self.clear()
        if len(elements) > self.surface.size()[1]:
            if self.bottom != 0 and selected <= self.bottom + self.margin:
                self.bottom = selected - self.margin
            elif selected >= (self.bottom + self.surface.size()[1]) - self.margin:
                self.bottom = selected - (self.surface.size()[1] - self.margin)
        else: 
            self.bottom = 0

        string = "\n".join(elements[self.bottom: self.bottom + self.surface.size()[1]])
        self.lab.set_text(string)
        self.lab.update()

    def _move_selected(self, selected):
        self.surface1.set_offset(self.surface.offset()[0], self.surface.offset()[1] + selected)

    def update(self, elements: List[str], selected=0):
        # if elements != self.current_elements:
        self._render(elements, selected)
        self.current_elements = elements
        self._move_selected(selected - self.bottom)

