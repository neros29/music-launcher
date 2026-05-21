import os
from typing import List
from listWidget import Element, Token
from queryRunner import QueryRunner
from query import Query, Playlist, Song
from queue import Queue
from playBackController import PlayBackController
from threading import Thread, Lock
from parser import Parser
from copy import deepcopy
import logging
import time
from ui import Ui

class Main:
    def __init__(self) -> None:
        logging.getLogger('thefuzz').setLevel(logging.ERROR)
        self.log = open("logs/log", "a")
        self.parser = Parser()
        self.db_path = "/home/neros/Documents/projects/music/data/db.json"
        self.query = Query(self.db_path)
        self.qr = QueryRunner(self.query)
        self.ui = Ui()
        self.pbc = PlayBackController("/tmp/mpv")

        self.text: str = ""
        self.options_lock = Lock()
        self.options = []
        self.ast_qeue =  Queue()
        self.worker_thread = Thread(target=self.worker, daemon=True)
        self.worker_thread.start()
        self.songs = []
        self.curser_index = 0
        self.selected = 0

        self.running = True
        self.special_keys = {
                "Backspace": self._backspace,
                "Left": self._move_left,
                "Right": self._move_right,
                "Enter": self._handle_enter,
                "Down": self._move_down,
                "Up": self._move_up,
            }

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
        first = self.text[:self.curser_index -1]
        second = self.text[self.curser_index:]
        self.text = first + second
        self.curser_index = max(0, self.curser_index - 1)

    def get_options(self):
        ast = self.parser.parse(self.text)
        if ast is None:
            self.options = None
            return
        self.ast_qeue.put(ast)

    def worker(self):
        while True:
            ast = self.ast_qeue.get()
            values = self.qr.run(ast)
            self.options_lock.acquire()
            self.options = deepcopy(values)
            self.options_lock.release()

    def draw_list(self):
        width = self.ui.song_list_size[0]
        text = []
        self.options_lock.acquire()
        results = deepcopy(self.options)
        self.options_lock.release()
        if results is None:
            text.append(f"Invalid query")
        else:
            if type(results) == Playlist:
                self.songs = [results.get_playable()]
                text.append(f"playing custom playlist from query")
            index = 0
            songs = []
            for result in results:
                if type(result) == Playlist:
                    name = f"playlist: {result.playlist_name}"
                    artist = f"artist: {result.artist}"
                    tracks = f"tack count: {len(result.data):03d}"
                    first_space = ((width - len(artist)) // 2) - len(name)
                    secound_space = (width - (first_space + len(name) + len(artist) + len(tracks)))
                    playlist_text = name + " "* first_space + artist + " " * secound_space + tracks
                    text.append(playlist_text)
                    songs.append(result.get_playable())
                    index += 1
                elif type(result) == Song:
                    name = f"song: {result.get_values('title')[0]}"
                    artist = f"artist: {result.get_values('artist')[0]}"
                    duration = f"duration: {len(result.get_values('duration')[0])}"
                    first_space = ((width - len(artist)) // 2) - len(name)
                    secound_space = (width - (first_space + len(name) + len(artist) + len(duration)))
                    playlist_text = name + " "* first_space + artist + " " * secound_space + duration
                    text.append(playlist_text)
                    songs.append([result.name])
                    index += 1
            self.songs = songs
        results = []
        selected = min(len(text) - 1, self.selected)
        for y, line in enumerate(text):
            element = []
            for ch in line:
                if y == selected:
                    element.append(Token(self.ui.fg, [self.ui.bg[0] - 70, self.ui.bg[1] - 70, self.ui.bg[2] - 30], ch))
                else:
                    element.append(Token(self.ui.fg, self.ui.bg, ch))
            results.append(Element(element))
        return results

    def play(self, songs):
        self.pbc.replace_playlist(songs)

    def _add_character(self, key):
        first = self.text[:self.curser_index]
        secound = key
        third = self.text[self.curser_index:]
        self.text = first + secound + third
        self.curser_index += 1

    def events(self, keys: List[str]):
        for key in keys:
            if key in self.special_keys:
                self.special_keys[key]()
            else:
                self._add_character(key)
                self.get_options()

    def draw_text(self):
        tokens = []
        for num, ch in enumerate(self.text):
            tokens.append(Token(self.ui.fg, self.ui.bg, ch))
        ch = " "
        if 0 <= self.curser_index < len(self.text):
            ch = tokens.pop(self.curser_index).character
        tokens.insert(self.curser_index, Token(self.ui.bg, self.ui.fg, ch, "cursor"))
        return tokens

    def run(self):
        frame_max = 0
        os.system("clear")
        while self.running:
            try:
                start = time.time()
                keys = self.ui.update(self.draw_text(), self.draw_list())
                frame_max = max(frame_max, time.time() - start)
                self.events(keys)
            except KeyboardInterrupt:
                break
        os.system("clear")
        print(frame_max)

if __name__ == "__main__":
    main = Main()
    main.run()

