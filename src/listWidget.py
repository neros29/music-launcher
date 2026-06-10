from typing import List
from pytui import Label, Surface
            

class ListWidget:
    def __init__(self, list_surface: Surface, selecter_surface: Surface, fg: List[int], bg: List[int]) -> None:
        self.list_surface: Surface = list_surface
        self.selector_surface: Surface = selecter_surface
        self.list_surface.offset()
        self.fg = fg
        self.bg = bg
        self.lab = Label(self.list_surface, "", [0, 0])
        self.bottom = 0
        self.margin = 5


    def _render(self, elements: List[str], selected):
        if len(elements) > self.list_surface.size()[1]:
            if self.bottom != 0 and selected <= self.bottom + self.margin: # if selected is margin from the top
                self.bottom = selected - self.margin
            elif selected >= (self.bottom + self.list_surface.size()[1]) - self.margin: # if selected is margin from the bottom
                self.bottom = selected - (self.list_surface.size()[1] - self.margin)
        else: 
            self.bottom = 0
        string = elements[0] + "\n" if len(elements) > 0 else "" # get the header if there are any elements.
        string += "\n".join(elements[(self.bottom + 1): (self.bottom + 1) + self.list_surface.size()[1]])
        diff = self.list_surface.size()[1] - len(string.split("\n"))
        for _ in range(diff):
            string += " " * self.list_surface.size()[0] + "\n"
        self.lab.set_text(string)
        self.lab.update()

    def _move_selected(self, selected):
        self.selector_surface.set_offset(self.list_surface.offset()[0], self.list_surface.offset()[1] + selected + 1)

    def update(self, elements: List[str], selected=0):
        self._render(elements, selected)
        self._move_selected(selected - self.bottom)

