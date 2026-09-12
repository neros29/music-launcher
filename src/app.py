from typing import Optional
import traceback
import logging
import time
import os

from editor import Editor
from selection import ListSelection
from player import Player

from config import Config
from dbQuery import Playable, Query, Playlist
from langdef import type_keywords, operator_keywords
from lexer import Lexer, token_types
from parser import Parser
from ui import Ui


logger = logging.getLogger(__name__)

class Main:
    def __init__(self, config: Config) -> None:
        logger.info("Starting initialization")
        self.config = config
        self.running = True

        self.db_path = config.db_path()
        self.socket_file = config.config["socket_file"]
        self.playback_cmd = config.config["player_cmd"]

        self.syntax_colors = {}
        self.fg, self.bg, self.surface_bg = self._get_theme()

        self.query: Query = Query(self.db_path)
        self.parser = Parser()
        self.lexer = Lexer()
        self.ui = Ui(self.fg, self.bg, self.surface_bg)

        self.options = None
        self.old_options = None

        self.editor = Editor(self.ui.search_bar, self.syntax_colors)
        self.selector = ListSelection(self.ui.song_list)
        self.player = Player(self.ui.root_surf, self.socket_file, self.playback_cmd)


        self.selected = Optional[list]
        self.text = ""
        self.frame_rate = 60

        self.finished = False
        self.saved_ast = None

    def _get_theme(self):
        syntax = self.config.config["theme"]["syntax"]
        self.syntax_colors = {
            token_types.TYPE: syntax["TYPE"],  
            token_types.S_VALUE: syntax["STRING_VALUE"], 
            token_types.VALUE: syntax["VALUE"],  
            token_types.OP: syntax["OP"],  
            token_types.L_OP: syntax["SCOPE"],
            token_types.R_OP: syntax["SCOPE"],
            "AUTO_COMPLETE": syntax["AUTO_COMPLETE"],
        }
        return self.config.config["theme"]["foreground"], self.config.config["theme"]["background"], self.config.config["theme"]["surface_bg"]




    def get_options(self, time_left):
        if self.editor.new_key:
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
            if self.saved_ast is None:
                self.options = None
                return
            results, done = self.query.query(self.saved_ast, time_left)
            logger.debug("Query ran for %s with results: %s, and done: %s", time_left, results, done)
        if done:
            self.options = results
            self.finished = True

    def smart_sleep(self, last_frame):
        frame_time = 1 / self.frame_rate

        # give the remaining time to get_options
        now = time.perf_counter()
        elapsed = now - last_frame
        if elapsed < frame_time:
            self.get_options(now + (frame_time - elapsed))

        # sleep remaining amount if get_options ends early
        new_now = time.perf_counter()
        elapsed = new_now - last_frame
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)
        return time.perf_counter()

    def run(self):
        last_frame = time.perf_counter()
        os.system("clear")
        logger.info("Starting main loop")
        error = None
        try:
            while self.running:
                try:
                    self.ui.update()
                    self.text = self.editor.update()
                    if self.options is not None:
                        self.selected = self.selector.update(self.options)
                        self.old_options = self.options
                    elif self.old_options is not None:
                        self.selected = self.selector.update(self.old_options)
                    if self.player.update(self.selected):
                        self.running = False
                    last_frame = self.smart_sleep(last_frame)
                except KeyboardInterrupt:
                    break
        except Exception as e:
            error = traceback.format_exc();
            logger.exception("Exception caught in main thread: ")
        finally:
            os.system("clear")
            if error is not None:
                print("Program crashed with error:")
                print(error)
