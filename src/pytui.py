from typing import List

from sys import path
path.append("include/pytui/")
import tui

class Character:
    def __init__(self, character: tui.Character) -> None:
        self.char = character

    def set_bg(self, r: int, g: int, b: int):
        return self.char.set_bg(r, g, b)

    def set_fg(self, r: int, g: int, b: int):
        return self.char.set_fg(r, g, b)

    def set_ch(self, ch: str):
        return self.char.set_ch(ch)

    def genrate(self):
        return self.char.genrate()

class Surface:
    def __init__(self, surface: tui.Surface) -> None:
        self.surf = surface

    def fill_bg(self, r: int, g: int, b: int):
        return self.surf.fill_bg(r, g, b)

    def fill_fg(self, r: int, g: int, b: int):
        return self.surf.fill_fg(r, g, b)

    def fill_ch(self, ch: str):
        for i in range(self.size()[0] * self.size()[1]):
            self.__getitem__(i).set_ch(ch)
        

    def set_z(self, z: int):
        return self.surf.set_z(z)

    def get_z(self) -> int:
        return self.surf.get_z()

    def set_offset(self, x: int, y: int):
        return self.surf.set_offset(x, y)

    def offset(self) -> List[int]:
        return self.surf.offset()

    def size(self) -> List[int]:
        return self.surf.size()

    def blit(self, surf):
        return self.surf.blit(surf.surf)

    def register_keys(self, keys: list[str]):
        return self.surf.register_keys(keys)

    def get_event(self, event: str):
        return self.surf.get_event(event)

    def __getitem__(self, index: int):
        return Character(self.surf[index])

class Tui:
    def __init__(self) -> None:
        self.tui = tui.Tui()

    def append(self, size: list[int], offset: list[int], ch: str, z: int):
        return Surface(self.tui.append(size, offset, ch, z))

    def get_screen_size(self): 
        return self.tui.getScreenSize()

    def update_screen(self):
        return self.tui.update()


class Label:
    def __init__ (self, root: Surface, text: str, offset: list[int]) -> None:
        self.label = tui.Label(root.surf, text, offset)
        self.text = text

    def update(self):
        self.label.update(self.text)

    def set_text(self, new_text):
        self.text = new_text
        self.update()
