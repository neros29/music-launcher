import wcwidth

from dbQuery import Playable, Playlist, Song
from listWidget import ListWidget
from pytui import Surface
from typing import Optional
from logging import getLogger

logger = getLogger(__name__)

class ListSelection:
    def __init__(self, list_widget: ListWidget) -> None:
        self.list_widget = list_widget
        self.surface = self.list_widget.list_surface

        self.width, self.height = self.list_widget.get_size()
        self.bg = self.list_widget.bg
        self.options: Optional[Playable] = None
        self.selected = 0
        self.list_widget.set_genrator(self.draw_list)
        self.special_keys = {
                "Down": self._move_down,
                "Up": self._move_up,
            }
        self._register_keys()

    def _register_keys(self):
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs)

    def _move_down(self):
        if self.options is not None:
            self.selected = min(self.list_widget.height, self.selected + 1)

    def _move_up(self):
        self.selected = max(0, self.selected - 1)

    def events(self):
        for key in self.special_keys:
            if self.surface.get_event(key):
                logger.debug("Received special key '%s' calling ListSelection.'%s'", key, self.special_keys[key].__name__)
                self.special_keys[key]()

    def update(self, list_options: Playable):
        self.options = list_options
        self.events()
        self.list_widget.update(self.selected)
        if self.options is not None and len(self.options.playable) > 0:
            if self.selected >= 0 and self.selected <= len(self.options.playable) -1:
                return self.options.get_playable(self.selected)
        return None

    def _sanitize_string(self, s: str):
        import string
        for i in string.whitespace:
            s.replace(i, " ")
        return s

    def draw_list(self, start, end, width):
        text = []
        assert self.options is not None, "This should not happen"
        results: Playable = self.options

        self.play_type = results.get_playable_type()
        first_row = (width // 2) - 5
        secound_row = (width // 3) - 5
        third_row = width - (first_row + secound_row)
        header = True
        for result in results.playable[start: end - 1]:
            if type(result) == Playlist:
                if header:
                    line = f"{'Playlist Name':<{first_row}}{'Predominant Artist':<{secound_row}}{'Track Count':>{third_row}}"
                first = f"{self._sanitize_string(result.name)}"
                secound = f"{self._sanitize_string(result.artist)}"
                third = f"{len(result.songs):03d}"
            else:
                if header:
                    line = f"{'Song Name':<{first_row}}{'Artist':<{secound_row}}{'Track Duration':>{third_row}}"
                first = f"{self._sanitize_string(result.get('title'))}"
                secound = f"{self._sanitize_string(result.get('artist')[0])}"
                third = f"{(result.get('duration') / 60):.2f}"
            first_wc_err = (wcwidth.wcswidth(first) - len(first))
            secound_wc_err = (wcwidth.wcswidth(secound) - len(secound))
            if wcwidth.wcswidth(first) + 1 > first_row:
                cut = (first_row - 4) - first_wc_err
                first = first[: cut] + "..."
                first +=(first_row - wcwidth.wcswidth(first)) * " "
            if wcwidth.wcswidth(secound) + 1 > secound_row:
                cut = (secound_row - 4) - secound_wc_err
                secound = secound[:cut] + "..."
                secound += (secound_row - wcwidth.wcswidth(secound)) * " "
            if header:
                text.append(line)
                header = False
            line = f"{first:<{first_row - first_wc_err}}{secound:<{secound_row - secound_wc_err}}{third:>{third_row}}"
            text.append(line)

        return text

