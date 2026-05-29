from typing import List
from pytui import Surface, Label, Tui
from inputWidget import InputWidget
from listWidget import ListWidget, Token, Element

class SearchBar(InputWidget):
    def __init__(self, size, offset, tui: Tui, fg, bg) -> None:
        background = tui.append(size, offset, " ", 0)
            #3d4253
        background.fill_bg(0x3d, 0x42, 0x53)
        surface = tui.append([size[0] - 4, size[1] - 2], [offset[0] + 2, offset[1] + 1], " ", 100)
        super().__init__(surface, bg, fg)

class SongList(ListWidget):
    def __init__(self, size, offset, tui: Tui, fg, bg) -> None:
        surface = tui.append(size, offset, " ", 100)
        super().__init__(surface, fg, bg)

class Ui:
    def __init__(self) -> None:
        self.tui = Tui()
        self.screen_size = self.tui.get_screen_size()
        self.bg = [0x15, 0x16, 0x1b]
        self.fg = [0xcf, 0xce, 0xd4]
        self.search_bar_size = [self.screen_size[0] - 10, 3]
        self.search_bar_offset = [(self.screen_size[0] - self.search_bar_size[0]) // 2, (self.screen_size[1] - self.search_bar_size[1]) // 7]


        self.song_list_size = [self.search_bar_size[0], self.screen_size[1] - (self.search_bar_offset[1] + self.search_bar_size[1] + 2) - 2]
        print(self.song_list_size)
        self.song_list_offset = [self.search_bar_offset[0], self.search_bar_offset[1] + self.search_bar_size[1] + 2]

        self.search_bar = SearchBar(self.search_bar_size, self.search_bar_offset, self.tui, self.fg, self.bg)
        self.song_list = SongList(self.song_list_size, self.song_list_offset, self.tui, self.fg, self.bg)

    def update(self, tokens: List[Token], elements: List[Element]):
        self.song_list.update(elements)
        keys = self.search_bar.update(tokens)
        self.tui.update_screen()
        self.screen_size = self.tui.get_screen_size()
        return keys

