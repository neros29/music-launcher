from typing import List
from pytui import Surface, Label, Tui
from inputWidget import InputWidget, Element, Token
from listWidget import ListWidget

class SearchBar(InputWidget):
    def __init__(self, size, offset, tui: Tui, fg, bg, background_bg) -> None:
        background = tui.append(size, offset, " ", 0)
        background.fill_bg(background_bg[0], background_bg[1], background_bg[2])
        surface = tui.append([size[0] - 4, size[1] - 2], [offset[0] + 2, offset[1] + 1], " ", 100)
        super().__init__(surface, bg, fg)

class SongList(ListWidget):
    def __init__(self, size, offset, tui: Tui, fg, bg, selecter_bg) -> None:
        surface = tui.append(size, offset, " ", 100)
        selecter = tui.append([size[0], 1], offset, " ", 98)
        selecter.fill_bg(selecter_bg[0], selecter_bg[1], selecter_bg[2])
        super().__init__(surface, selecter, fg, bg)

class Ui:
    def __init__(self, fg, bg, surface_bg ) -> None:
        self.tui = Tui()
        self.screen_size = self.tui.get_screen_size()
        self.bg = bg
        self.fg = fg
        self.surface_bg = surface_bg
        self.search_bar_size = [self.screen_size[0] - 10, 3]
        self.search_bar_offset = [(self.screen_size[0] - self.search_bar_size[0]) // 2, (self.screen_size[1] - self.search_bar_size[1]) // 7]
        self.old_tokens = None
        self.old_elements = None
        self.old_selected = None
        self.max = 0


        self.song_list_size = [self.search_bar_size[0], self.screen_size[1] - (self.search_bar_offset[1] + self.search_bar_size[1] + 2) - 2]
        self.song_list_offset = [self.search_bar_offset[0], self.search_bar_offset[1] + self.search_bar_size[1] + 2]

        self.search_bar = SearchBar(self.search_bar_size, self.search_bar_offset, self.tui, self.fg, self.bg, self.surface_bg)
        self.song_list = SongList(self.song_list_size, self.song_list_offset, self.tui, self.fg, self.bg, self.surface_bg)

    def update(self, tokens: List[Token], elements, selected):
        self.old_elements = elements
        self.old_selected = selected
        self.song_list.update(elements, selected)
        if self.old_tokens != tokens:
            self.old_tokens = tokens
            self.search_bar.render_text(tokens)
        self.tui.update_screen()
        return self.search_bar.get_input()

