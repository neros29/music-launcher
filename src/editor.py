from atexit import register
from inputWidget import InputWidget, Token as iToken
from langdef import type_keywords, operator_keywords
from lexer import Token, Tokens, Lexer
from pytui import Surface
from typing import Optional
from logging import getLogger
import string

logger = getLogger(__name__)

class Editor:
    def __init__(self, input_widget: InputWidget, syntax_colors: dict, inital_cursor_pos: Optional[list] = None) -> None:
        self.input_widget = input_widget
        self.surface = self.input_widget.surface

        self.width, self.height = self.input_widget.get_size()
        self.bg = self.input_widget.bg

        self.syntax_colors = syntax_colors
        self.lexer = Lexer()
        self.text: str = ""
        self.old_text: str = ""
        self.replace: str = ""
        self.curser_index = 0
        self.old_curser_index = 0
        self.new_key = False
        self.special_keys = {
                chr(127): self._backspace,
                "Left": self._move_left,
                "Right": self._move_right,
                chr(0x09): self._replace,
            }
        self.keys = self._register_keys()

    def _register_keys(self):
        keys = list(string.printable)
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs + keys)
        return keys

    def draw_text(self):
        tokens = []
        for token in self.lexer.lex(self.text):
            if not token.virtual:
                for ch in token.value:
                    tokens.append(iToken(self.syntax_colors[token.token_type], self.bg, ch))
        
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
                tokens.append(iToken(self.syntax_colors["AUTO_COMPLETE"], self.bg, ch))
        else:
            self.replace = ""
        ch = " "
        self.old_tokens = tokens
        self.old_text = self.text
        return tokens

    def _replace(self):
        if self.replace != "":
            token = self.lexer.split_string(self.text)
            self.text = self.text[:-len(token[-2].value)]
            self.text += self.replace
            self.curser_index = len(self.text)

    def _add_character(self, key):
        if len(self.text) < self.width - 1:
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

    def events(self):
        for key in self.special_keys:
            if self.surface.get_event(key):
                logger.debug("Received special key '%s' calling Editor.'%s'", key, self.special_keys[key].__name__)
                self.special_keys[key]()
        for key in self.keys:
            if self.surface.get_event(key):
                logger.debug("Received key '%s' calling Editor._add_character", key)
                self._add_character(key)
                self.new_key = True

    def update(self):
        self.events()
        tokens = self.draw_text()
        self.input_widget.render_text(tokens, (self.curser_index, 0))
        return self.text
