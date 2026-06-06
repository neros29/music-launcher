import os
from typing import List, Optional
from inputWidget import Token
from langdef import type_keywords, operator_keywords
from dbQuery import Append, Query, Playlist, Song
from playBackController import PlayBackController
from threading import Thread, Lock
from parser import Parser
from lexer import Lexer, token_types
import logging
import time
from ui import Ui

class Main:
    def __init__(self) -> None:
        print("\x1b[?1h")
        logging.getLogger('thefuzz').setLevel(logging.ERROR)
        self.log = open("logs/log", "a")
        self.running = True

        self.db_path = "/home/neros/Documents/projects/music/data/db.json"
        self.socket_file = "/tmp/mpv"
        self._mpv_cmd = f"mpv --input-ipc-server={self.socket_file} --idle=yes --player-operation-mode=pseudo-gui"

        self.pbc_lock = Lock()
        self.pbc: Optional[PlayBackController] = None
        self.t = Thread(target=self._start_pbc, daemon=True)
        self.t.start()
        self.query: Query = Query(self.db_path)
        self.parser = Parser()
        self.lexer = Lexer()
        self.ui = Ui(self.log)

        self.text: str = ""
        self.old_text: str = ""
        self.replace: str = ""

        self.old_tokens = []
        self.options = []
        self.old_options = []
        self.old_list_text = []
        self.songs = []

        self.append = False
        self.curser_index = 0
        self.old_curser_index = 0
        self.selected = 0
        self.frame_rate = 60

        self.special_keys = {
                "Backspace": self._backspace,
                "Left": self._move_left,
                "Right": self._move_right,
                "Enter": self._handle_enter,
                "Down": self._move_down,
                "Up": self._move_up,
                "Tab": self._replace,
            }

    def _start_pbc(self):
        with self.pbc_lock:
            self.pbc = PlayBackController(self.socket_file, self._mpv_cmd)

    def _replace(self):
        if self.replace != "":
            token = self.lexer.split_string(self.text)
            self.text = self.text[:-len(token[-2].value)]
            self.text += self.replace
            self.curser_index = len(self.text)

    def _move_down(self):
        self.selected = min(len(self.songs) -1, self.selected + 1)

    def _move_up(self):
        self.selected = max(0, self.selected - 1)

    def _handle_enter(self):
        if self.text == "/exit":
            self.running = False
            return 
        if len(self.songs) > 0:
            index = max(min(len(self.songs)-1, self.selected), 0)
            songs = self.songs[index]
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
        self.get_options()

    def get_options(self):
        tokens = self.lexer.lex(self.text)
        ast = self.parser.parse(tokens)
        if ast is None:
            self.options = None
            return
        self.options = self.query.query(ast)

    def draw_list(self):
        width = self.ui.song_list_size[0]
        text = []
        results = self.options
        if self.old_options == results:
            return self.old_list_text
        if results is None:
            text.append(f"Invalid query")
        else:
            if type(results) == Playlist:
                self.songs = [i.path for i in results]
                text.append(f"playing custom playlist from query")
            if type(results) == Append:
                self.append = True
            index = 0
            songs = []
            max_name_len = (width // 2) - 5
            max_artist_len = (width // 3) - 5
            for result in results:
                if type(result) == Playlist:
                    name = f"playlist: {result.name}"
                    if len(name) > max_name_len:
                        name = name[: max_name_len ] + "..."
                    artist = f"artist: {result.artist}"
                    if len(artist) > max_artist_len:
                        artist = artist[:max_artist_len] + "..."

                    tracks = f"track count: {len(result.songs):03d}"
                    first_space = (width // 2) - len(name)
                    secound_space = (width - (first_space + len(name) + len(artist) + len(tracks)))
                    playlist_text = name + " "* first_space + artist + " " * secound_space + tracks
                    text.append(playlist_text)
                    songs.append([i.path for i in result])
                    index += 1
                elif type(result) == Song:
                    name = f"song: {result.get('title')}"
                    if len(name) > max_name_len:
                        name = name[: max_name_len] + "..."
                    artist = f"artist: {result.get('artist')}"
                    if len(artist) > max_artist_len:
                        artist = artist[:max_artist_len] + "..."
                    duration = f"duration: {(result.get('duration') / 60):.2f}"
                    first_space = (width // 2) - len(name)
                    secound_space = (width - (first_space + len(name) + len(artist) + len(duration)))
                    playlist_text = name + " "* first_space + artist + " " * secound_space + duration
                    text.append(playlist_text)
                    songs.append([result.path])
                    index += 1
            self.songs = songs
        self.old_options = self.options
        self.old_list_text = text
        return text

    def play(self, songs):
        with self.pbc_lock:
            print(f"suff {self.append}", file=self.log)
            if self.append:
                self.append = False
                self.pbc.add_to_playlists(songs)
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
                self.get_options()

    def draw_text(self):
        if self.old_text == self.text and self.old_curser_index == self.curser_index: 
            return self.old_tokens
        tokens = []
        colors = {
            token_types.TYPE: [0xd2, 0x8c, 0x89],  
            token_types.S_VALUE: [0x3e, 0x87, 0xa3], 
            token_types.VALUE: [0xe2, 0xb3, 0x70],  
            token_types.OP: [0x81, 0xa8, 0xe6],  
            token_types.L_OP: [0x81, 0xa8, 0xe6],
            token_types.R_OP: [0x81, 0xa8, 0xe6],
        }
        for token in self.lexer.lex(self.text):
            if not token.virtual:
                for ch in token.value:
                    tokens.append(Token(colors[token.token_type], self.ui.bg, ch))
        
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
                tokens.append(Token([0x91, 0x88, 0xa8], self.ui.bg, ch))
        else:
            self.replace = ""
        ch = " "
        if 0 <= self.curser_index < len(self.text) + len(self.replace):
            ch = tokens.pop(self.curser_index).character
        tokens.insert(self.curser_index, Token(self.ui.bg, self.ui.fg, ch, "cursor"))
        self.old_tokens = tokens
        self.old_curser_index = self.curser_index
        return tokens

    def run(self):
        frame_max = 0
        max_text = ""
        to_print = ""
        frame_time = 1 / self.frame_rate
        last_frame = time.perf_counter()
        os.system("clear")
        while self.running:
            try:
                text = self.draw_text()
                elements = self.draw_list()
                keys = self.ui.update(text, elements, self.selected)
                self.events(keys)
                now = time.perf_counter()
                elapsed = now - last_frame
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                last_frame = time.perf_counter()
            except KeyboardInterrupt:
                break
            # except Exception as e:
            #     to_print += f"Error {e} occured\n"
            #     to_print += f"Text dump is '{self.text}'\n"
            #     break
        os.system("clear")
        print(to_print, end="")
        print(frame_max)
        print(max_text)

if __name__ == "__main__":
    main = Main()
    main.run()

