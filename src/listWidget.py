from typing import List
from pytui import Label, Surface
            

class ListWidget:
    def __init__(self, list_surface: Surface, selecter_surface: Surface, fg: List[int], bg: List[int]) -> None:
        self.list_surface: Surface = list_surface
        self.selector_surface: Surface = selecter_surface
        self.list_surface.offset()
        self.selector_surface.fill_bg(0x42, 0x3e, 0x58)
        self.fg = fg
        self.bg = bg
        self.lab = Label(self.list_surface, "", [0, 0])
        self.bottom = 0
        self.margin = 5

    def clear(self):
        text = "\n".join([" " * self.list_surface.size()[0] for _ in range(self.list_surface.size()[1])])
        self.lab.set_text(text)

    def _render(self, elements: List[str], selected):
        self.clear()
        if len(elements) > self.list_surface.size()[1]:
            if self.bottom != 0 and selected <= self.bottom + self.margin:
                self.bottom = selected - self.margin
            elif selected >= (self.bottom + self.list_surface.size()[1]) - self.margin:
                self.bottom = selected - (self.list_surface.size()[1] - self.margin)
        else: 
            self.bottom = 0

        string = "\n".join(elements[self.bottom: self.bottom + self.list_surface.size()[1]])
        self.lab.set_text(string)
        self.lab.update()

    def _move_selected(self, selected):
        self.selector_surface.set_offset(self.list_surface.offset()[0], self.list_surface.offset()[1] + selected)

    def update(self, elements: List[str], selected=0):
        self._render(elements, selected)
        self._move_selected(selected - self.bottom)

