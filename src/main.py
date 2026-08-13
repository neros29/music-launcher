from langdef import type_keywords, operator_keywords
from playBackController import PlayBackController
from dbQuery import Playable, Query, Playlist
from lexer import Lexer, token_types
from threading import Thread, Lock
from typing import List, Optional
from inputWidget import Token
from parser import Parser
from load import Load
from config import Config
from ui import Ui
import logging
import wcwidth
import time
import sys
import os

class Main:
    def __init__(self, config: Config) -> None:
        self.config = config
        logging.getLogger('thefuzz').setLevel(logging.ERROR)
        self.running = True

        self.db_path = config.db_path()
        self.socket_file = config.config["socket_file"]
        self._playback_cmd = config.config["player_cmd"]
        self.syntax_colors = {}
        self.fg, self.bg, self.surface_bg = self._get_theme()

        self.pbc_lock = Lock()
        self.pbc: Optional[PlayBackController] = None
        self.t = Thread(target=self._start_pbc, daemon=True)
        self.t.start()
        self.query: Query = Query(self.db_path)
        self.parser = Parser()
        self.lexer = Lexer()
        self.ui = Ui(self.fg, self.bg, self.surface_bg)
        self.text: str = ""
        self.old_text: str = ""
        self.replace: str = ""

        self.old_tokens = []
        self.options = None
        self.old_options = None
        self.old_list_text = []

        self.play_type = "song"
        self.curser_index = 0
        self.old_curser_index = 0
        self.selected = 0
        self.frame_rate = 30
        self.new_key = True
        self.finished = False
        self.saved_ast = None

        self.special_keys = {
                "Backspace": self._backspace,
                "Left": self._move_left,
                "Right": self._move_right,
                "Enter": self._handle_enter,
                "Down": self._move_down,
                "Up": self._move_up,
                "Tab": self._replace,
            }
    def _get_theme(self):
        syntax = self.config.config["theme"]["syntax"]
        self.syntax_colors = {
            token_types.TYPE: syntax["TYPE"],  
            token_types.S_VALUE: syntax["STRING_VALUE"], 
            token_types.VALUE: syntax["VALUE"],  
            token_types.OP: syntax["OP"],  
            token_types.L_OP: syntax["SCOPE"],
            token_types.R_OP: syntax["SCOPE"],
        }
        return self.config.config["theme"]["foreground"], self.config.config["theme"]["background"], self.config.config["theme"]["surface_bg"]


    def _start_pbc(self):
        with self.pbc_lock:
            self.pbc = PlayBackController(self.socket_file, self._playback_cmd)

    def _replace(self):
        if self.replace != "":
            token = self.lexer.split_string(self.text)
            self.text = self.text[:-len(token[-2].value)]
            self.text += self.replace
            self.curser_index = len(self.text)

    def _move_down(self):
        if self.options is not None:
            self.selected = min(len(self.options.playable) -1, self.selected + 1)
        elif self.old_options is not None:
            self.selected = min(len(self.old_options.playable) -1, self.selected + 1)

    def _move_up(self):
        self.selected = max(0, self.selected - 1)

    def _handle_enter(self):
        if self.text == "/exit":
            self.running = False
            return 
        if self.options is not None and len(self.options.playable) > 0:
            index = max(min(len(self.options.playable)-1, self.selected), 0)
            songs = self.options.get_playable(index)
            self.play(songs)
            self.running = False
        elif self.old_options is not None and len(self.old_options.playable) > 0:
            index = max(min(len(self.old_options.playable)-1, self.selected), 0)
            songs = self.old_options.get_playable(index)
            self.play(songs)
            self.running = False



    def _move_left(self):
        self.curser_index = max(0, self.curser_index - 1)

    def _move_right(self):
        self.curser_index = min(len(self.text), self.curser_index + 1)

    def _backspace(self):
        secound = self.text[self.curser_index:]
        first = self.text[:max(0, self.curser_index - 1)]
        self.text = first + secound
        self.curser_index = max(0, self.curser_index - 1)
        self.new_key = True

    def get_options(self, time_left):
        if self.new_key:
            self.finished = False
            tokens = self.lexer.lex(self.text)
            ast = self.parser.parse(tokens)
            self.saved_ast = ast
            if ast is None:
                self.options = None
                return
            results, done = self.query.query(ast, time_left, restart=True)
            self.new_key = False
        elif self.finished:
            return
        else:
            results, done = self.query.query(self.saved_ast, time_left)
        if done:
            self.options = results
            self.finished = True
    def _sanitize_string(self, s: str):
        import string
        for i in string.whitespace:
            s.replace(i, " ")
        return s

    def draw_list(self, start, end):
        width = self.ui.song_list_size[0]
        text = []
        if self.options is None and self.old_options is None:
            return [""]
        elif self.options is None:
            results: Playable = self.old_options
        else:
            results: Playable = self.options
        if False:
            return self.old_list_text
        else:
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

        self.old_options = self.options
        self.old_list_text = text
        return text

    def play(self, songs):
        with self.pbc_lock:
            assert self.pbc is not None, "to fix lsp"
            if self.play_type == "append":
                self.append = False
                self.pbc.add_to_playlists(songs)
            elif self.play_type == "insert-next":
                self.next_song = False
                self.pbc.add_next_song(songs)
            else:
                self.pbc.replace_playlist(songs)

    def _add_character(self, key):
        first = self.text[:self.curser_index]
        secound = key
        third = self.text[self.curser_index:]
        self.text = first + secound + third 
        self.curser_index += 1
        if key == "(" and self.curser_index == len(self.text):
            self.text += ")"
        if key == '"' and self.curser_index == len(self.text):
            self.text += '"'
        if key == "'" and self.curser_index == len(self.text):
            self.text += "'"


    def events(self, keys: List[str]):
        for key in keys:
            if key in self.special_keys:
                self.special_keys[key]()
            else:
                self._add_character(key)
                self.new_key = True

    def draw_text(self):
        if self.old_text == self.text and self.old_curser_index == self.curser_index: 
            return self.old_tokens
        tokens = []
        for token in self.lexer.lex(self.text):
            if not token.virtual:
                for ch in token.value:
                    tokens.append(Token(self.syntax_colors[token.token_type], self.bg, ch))
        
        last_token = self.lexer.split_string(self.text)
        key_word = ""
        all_words = {}
        all_words.update(type_keywords)

        all_words.update(operator_keywords)
        for type_keyword in all_words:
            if len(last_token[-2].value) > 1:
                if type_keyword.startswith(last_token[-2].value):
                    key_word = type_keyword
                    break
        if key_word != "":
            if key_word in type_keywords:
                self.replace = f"{key_word}: "
            elif key_word in operator_keywords:
                self.replace = f"{key_word} "
            for ch in self.replace[len(last_token[-2].value):]:
                tokens.append(Token(self.config.config["theme"]["syntax"]["AUTO_COMPLETE"], self.bg, ch))
        else:
            self.replace = ""
        ch = " "
        if 0 <= self.curser_index < len(self.text) + len(self.replace):
            ch = tokens.pop(self.curser_index).character
        tokens.insert(self.curser_index, Token(self.bg, self.fg, ch, "cursor"))
        self.old_tokens = tokens
        self.old_curser_index = self.curser_index
        return tokens

    def run(self):
        frame_time = 1 / self.frame_rate
        last_frame = time.perf_counter()
        max_ui_time = 0
        max_options_time = 0
        os.system("clear")
        while self.running:
            try:
                text = self.draw_text()
                keys = self.ui.update(text, self.draw_list, self.selected)
                self.events(keys)

                # give the remaining time to get_options
                now = time.perf_counter()
                elapsed = now - last_frame
                max_ui_time = max(max_ui_time, elapsed)
                if elapsed < frame_time:
                    self.get_options(now + (frame_time - elapsed))
                # sleep remaining amont if get_options ends early
                new_now = time.perf_counter()
                max_options_time = max(max_options_time, new_now - now)
                elapsed = new_now - last_frame
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                last_frame = time.perf_counter()

            except KeyboardInterrupt:
                break
        os.system("clear")
        print(max_ui_time)
        print(max_options_time)

if __name__ == "__main__":
    config = Config("music-launcher")
    args = sys.argv
    if len(args) > 1 and args[1] == "load":
        print(f"Loading music into db...")
        load = Load(config.config["music_paths"], config.db_path())
        load.fill_db()
    else:
        print("\x1b[?1h")
        main = Main(config)
        main.run()
        print("\x1b[?25h")

