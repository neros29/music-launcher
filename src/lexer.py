from typing import List, Optional
from copy import deepcopy
from langdef import basic_types, token_types
import langdef

    
class Token:
    def __init__(self, start_idx: tuple, value: str, basic_type: Optional[basic_types] = None, token_type: Optional[token_types] = None, virtual = False) -> None:
        self.token_type: Optional[token_types] = token_type
        self.virtual: bool = virtual
        self.basic_type: Optional[basic_types] = basic_type
        self.start_idx: tuple = start_idx
        self.value: str = value

    def set_token_type(self, token_type: token_types):
        self.token_type = token_type
    
    def __repr__(self) -> str:
        return self.value

    def __add__(self, other):
        if isinstance(other, Token):
            token = Token(self.start_idx, self.value + other.value)
            if self.token_type:
                token.token_type = self.token_type
            return token

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Token):
            return self.value == value.value

        if isinstance(value, str):
            return self.value == value
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)

class Tokens:
    def __init__(self) -> None:
        self.data: List[Token] = []

    def append(self, token: Token):
        self.data.append(token)

    def insert(self, index, token: Token):
        self.data.insert(index, token)

    def clear(self):
        self.data.clear()

    def pop(self) -> Token:
        return self.data.pop()

    def __setitem__(self, index: int, token: Token):
        self.data[index] = token

    def __getitem__(self, index: int):
        return self.data[index]

    def __iter__(self):
        for i in self.data:
            yield i

    def __repr__(self) -> str:
        results = "["
        for i in range(0, len(self.data)):
            results += f"['{self.data[i].basic_type.name if self.data[i].token_type is None else self.data[i].token_type.name}': '{self.data[i].value}']"
            if i != len(self.data) -1:
                results += ", "
        results += "]"

        return results

class Lexer:
    def __init__(self) -> None:
        self.seperators = langdef.seperators
        self.type_keywords = langdef.type_keywords
        self.operator_keywords = langdef.operator_keywords
        self.defualts = langdef.defulats
        self.valid_syntax_paths = langdef.valid_syntax_paths

        self.results: Tokens = Tokens()
        self.tokens: Tokens = Tokens()

        self.iter: int = 0
        self.state = 0
        self.buffer: Optional[Token] = None
        self.guess: token_types = token_types.TYPE
        self.last_guess = 0
        self.iter_stack: List[int] = []
        self.last_guess_stack: List[int] = []

    def split_string(self, string: str):
        results = Tokens()
        results.append(Token((-1, 0), "", basic_types.SOF, token_types.SOF, virtual=True))
        buffer = ""
        for index, char in enumerate(string):
            if char in self.seperators:
                if len(buffer) > 0:
                    results.append(Token((index - len(buffer), 0), buffer, basic_types.WORD))
                results.append(Token(((index + 1) - len(char), 0), char, self.seperators[char]))
                buffer = ""
            else:
                buffer += char
        if len(buffer) > 0:
            results.append(Token((len(string) - len(buffer), 0), buffer, basic_types.WORD))
        results.append(Token((len(string), 0), "", basic_types.EOF, token_types.EOF, virtual=True))
        return results

    def _get_valid_paths(self):
        token = self.results[-1]
        if token.token_type is not None:
            return self.valid_syntax_paths[token.token_type]
        raise SyntaxError(f"Token '{token}' has no token_type")

    def _guess_path(self):
        paths = self._get_valid_paths()
        if self.last_guess >= len(paths):
            self._undo_guess()
        else:
            self.guess = paths[self.last_guess]
            self.last_guess += 1

    def _undo_guess(self):
        self.results.pop()
        self.iter = self.iter_stack.pop()
        self.last_guess = self.last_guess_stack.pop()
        self._guess_path()

    def _new_guess(self):
        self.last_guess_stack.append(self.last_guess)
        self.last_guess = 0
        self.iter_stack.append(self.iter)
        self._guess_path()

    def _buffer_add(self):
        if self.buffer is not None:
            self.buffer += self.tokens[self.iter]
        else:
            self.buffer = self.tokens[self.iter]

    def _in_TYPE(self):
        while True:
            BEFORE_KEY_WORD = 0
            AFTER_KEY_WORD  = 1
            token = self.tokens[self.iter]
            if self.state == BEFORE_KEY_WORD:
                valid = [basic_types.WS, basic_types.WORD]
                if token.basic_type in valid:
                    if token.basic_type == basic_types.WORD:
                        if token.value in self.type_keywords:
                            self.state = AFTER_KEY_WORD
                        else:
                            return False
                    self._buffer_add()
                    self.iter += 1
                    continue
            elif self.state == AFTER_KEY_WORD:
                valid = [basic_types.WS, basic_types.SEP]
                if token.basic_type in valid:
                    if token.basic_type == basic_types.SEP:
                        self._buffer_add()
                        return True
                    self._buffer_add()
                    self.iter += 1
                    continue
            return False

    def _in_OP(self):
        while True:
            token = self.tokens[self.iter]
            valid = [basic_types.WS, basic_types.WORD]
            if token.basic_type in valid:
                if token.basic_type == basic_types.WORD:
                    if token.value in self.operator_keywords:
                        self._buffer_add()
                        return True
                    else:
                        return False
                self._buffer_add()
                self.iter += 1
                continue
            return False

    def _in_EOF(self):
        token = self.tokens[self.iter]
        if token.basic_type == basic_types.EOF:
            self.buffer = token
            return True
        return False

    def _in_S_VALUE(self):
        while True:
            BEFORE_STRING = 0
            IN_D_STRING = 1
            IN_S_STRING = 2
            token = self.tokens[self.iter]
            if self.state == BEFORE_STRING:
                valid = [basic_types.WS, basic_types.D_QUOTES, basic_types.S_QUOTES]
                if token.basic_type in valid:
                    if token.basic_type == basic_types.D_QUOTES:
                        self.state = IN_D_STRING
                    elif token.basic_type == basic_types.S_QUOTES:
                        self.state = IN_S_STRING
                    self._buffer_add()
                    self.iter += 1
                    continue
            elif self.state != BEFORE_STRING:
                if self.state == IN_S_STRING:
                    quote_type = basic_types.S_QUOTES
                elif self.state == IN_D_STRING:
                    quote_type = basic_types.D_QUOTES
                else: 
                    quote_type = basic_types.D_QUOTES
                if token.basic_type == quote_type:
                    self._buffer_add()
                    return True
                elif token.basic_type == basic_types.ESC:
                    self._buffer_add()
                    self.iter += 1
                elif token.basic_type == basic_types.EOF:
                    return False
                self._buffer_add()
                self.iter += 1
                continue
            return False

    def _in_VALUE(self):
        while True:
            token = self.tokens[self.iter]
            if token.basic_type == basic_types.EOF:
                return False
            if len(self.results.data) > 0:
                if self.results[-1].token_type == token_types.VALUE:
                    self.results[-1] += token
                else:
                    self._buffer_add()
            else:
                raise SyntaxError("How did this happen?")
            if token.basic_type == basic_types.ESC:
                self.iter += 1
                continue
            return True

    def _in_L_OP(self):
        while True:
            token = self.tokens[self.iter]
            valid = [basic_types.WS, basic_types.L_OP]
            if token.basic_type in valid:
                if token.basic_type == basic_types.L_OP:
                    self._buffer_add()
                    return True
                self._buffer_add()
                self.iter += 1
                continue
            return False

    def _in_R_OP(self):
        while True:
            token = self.tokens[self.iter]
            valid = [basic_types.WS, basic_types.R_OP]
            if token.basic_type in valid:
                if token.basic_type == basic_types.R_OP:
                    self._buffer_add()
                    return True
                self._buffer_add()
                self.iter += 1
                continue
            return False

    def _run_func(self):
        self.funcs = {
                token_types.TYPE: self._in_TYPE,
                token_types.EOF: self._in_EOF,
                token_types.S_VALUE: self._in_S_VALUE,
                token_types.VALUE: self._in_VALUE,
                token_types.L_OP: self._in_L_OP,
                token_types.R_OP: self._in_R_OP,
                token_types.OP: self._in_OP,
                }
        while True:
            if self.guess in self.funcs:
                if self.funcs[self.guess]():
                    if self.buffer:
                        self.buffer.set_token_type(self.guess)
                        self.results.append(self.buffer) 
                    if self.guess == token_types.EOF:
                        break
                    self.buffer = None
                    self.state = 0
                    self.iter += 1
                    self._new_guess()
                    continue
                else:
                    self.buffer = None
                    self.state = 0
                    self._guess_path()
                    if self.iter_stack:
                        self.iter = self.iter_stack[-1]
                    continue
                        
            else:
                print(f"No function for {self.guess=}")

    def lex(self, string: str):
        self.iter = 0
        self.results.clear()
        self.tokens = self.split_string(string)
        if self.tokens[self.iter].basic_type == basic_types.SOF:
            self.tokens[self.iter].set_token_type(token_types.SOF)
            self.results.append(self.tokens[self.iter])
            self.iter += 1
            self._new_guess()
        self._run_func()
        return deepcopy(self.results)

if __name__ == "__main__":
    string = 'playlists: artist: "*iron*" (title: king and title: "Left*")'
    string = "playlists: (artist: ironmouse (title: 'king*"
    tk = Lexer()
    import time
    print(f"{string=}")
    start = time.time()
    tokens: Tokens = tk.lex(string)
    print(f"{time.time() - start=}")
    print(f"{tokens=}")
    colorized = ""
    colors = {
            token_types.TYPE: "\x1b[38;2;255;0;0m",
            token_types.S_VALUE: "\x1b[38;2;0;255;0m",
            token_types.VALUE: "\x1b[38;2;255;255;0m",
            token_types.OP: "\x1b[38;2;0;0;255m",
            token_types.L_OP: "\x1b[38;2;0;0;255m",
            token_types.R_OP: "\x1b[38;2;0;0;255m",
            }
    for token in tokens:
        if not token.virtual:
            colorized += colors[token.token_type] + token.value + "\x1b[0m"
    print(f"string='{colorized}'")

