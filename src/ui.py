from typing import List
from pytui import Surface, Label, Tui
from inputWidget import InputWidget, Token
from listWidget import ListWidget

class Ui:
    def __init__(self, fg, bg, surface_bg ) -> None:
        self.tui = Tui()
        self.screen_size = self.tui.get_screen_size()
        self.screen_size[0], self.screen_size[1] = self.screen_size[0] + 3, self.screen_size[1] + 3
        self.screen_margins = (20, 5)

        self.bg = bg
        self.fg = fg
        self.surface_bg = surface_bg

        self.search_bar_size = [self.screen_size[0] - self.screen_margins[0], 3]
        self.search_bar_offset = [(self.screen_size[0] - self.search_bar_size[0]) // 2, (self.screen_size[1] - self.search_bar_size[1]) // 7]
        self.search_bar_margin = (4, 2)

        self.song_list_size = [self.search_bar_size[0], self.screen_size[1] - (self.search_bar_offset[1] + self.search_bar_size[1]) - self.screen_margins[1] // 2]
        self.song_list_offset = [self.search_bar_offset[0], self.search_bar_offset[1] + self.search_bar_size[1]]
        self.song_list_margin = (0, 5)

        self.search_bar, self.search_bar_surf = self._init_inputWidget()
        self.song_list, self.song_list_surf = self._init_listWidget()

        self.root_surf = self.tui.append([2, 2], [-5, -5], " ", 500)

    def _init_inputWidget(self):
        background = self.tui.append(self.search_bar_size, self.search_bar_offset, " ", 50)
        background.fill_bg(*self.surface_bg)
        surface = self.tui.append(
                [self.search_bar_size[0] - self.search_bar_margin[0], self.search_bar_size[1] - self.search_bar_margin[1]],
                [self.search_bar_offset[0] + self.search_bar_margin[0] // 2, self.search_bar_offset[1] + self.search_bar_margin[1] // 2], 
                " ", 51)
        return InputWidget(surface, self.bg, self.fg), surface

    def _init_listWidget(self):
        surface = self.tui.append(
                [self.song_list_size[0] - self.song_list_margin[0], self.song_list_size[1] - self.song_list_margin[1]],
                [self.song_list_offset[0] + self.song_list_margin[0] // 2, self.song_list_offset[1] + self.song_list_margin[1] // 2], 
                " ", 102)
        surface.fill_fg(*self.fg)
        selecter_surface = self.tui.append([self.song_list_size[0] - self.song_list_margin[0], 1], [self.song_list_offset[0] + self.song_list_margin[0] // 2, self.song_list_offset[1] + self.song_list_margin[1] // 2], " ", 101)
        selecter_surface.fill_bg(*self.surface_bg)
        return ListWidget(surface, selecter_surface, self.fg, self.bg), surface

    def update(self):
        # self.song_list.update(*list_values)
        # self.search_bar.render_text(*search_values)
        self.tui.update_screen()

