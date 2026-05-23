from typing import Dict, List, Optional
from enum import Enum, auto
import re

class Pair:
    def __init__(self, key: str, data_type: str, data) -> None:
        self.key = key
        self.data_type = data_type
        self.data = data

class Operator:
    def __init__(self, data) -> None:
        self.data = data

class Token:
    def __init__(self, token_type: str, start_idx: int, end_idx: int, value: str) -> None:
        self.type = token_type
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.value = value

class Tokens:
    def __init__(self, raw: str) -> None:
        self.tokens: List[Token] = []
        self.raw = raw

    def append(self, token: Token):
        self.tokens.append(token)

    def __getitem__(self, index: int):
        return self.tokens[index]

    def __iter__(self):
        for i in self.tokens:
            yield i

    def __repr__(self) -> str:
        results = "["
        for i in range(0, len(self.tokens)):
            results += f"({self.tokens[i].start_idx}: '{self.tokens[i].type}' = '{self.tokens[i].value}')"
            if i != len(self.tokens) -1:
                results += ", "
            else:
                results += "]"

        return results

class Tokenizer:
    def __init__(self, type_keywords, operator_keywords, seperators) -> None:
        self.type_keywords = type_keywords
        self.operator_keywords = operator_keywords
        self.seperators = seperators

        self.scope_stack = []

        self.tokens = None

        self.buffer = ""
        self.start_idx = 0

        self.string = False
        self.escape = False
        self.operator = False
        self.key = False
    
    def add_token(self, token_type, token):
        assert self.tokens is not None, "This should not happen"
        self.tokens.append(Token(token_type, self.start_idx - len(token), self.start_idx, token))

    def clear_buffer(self):
        self.buffer = ""

    def init(self, raw_tokens: List[str]):
        self.tokens = Tokens("".join(raw_tokens))
        self.buffer = ""
        self.start_idx = 0
        self.string = False
        self.escape = False

    def check_sep(self, token):
        sep_type = self.seperators[token]
        if sep_type == "esc":
            self.escape = True
        elif sep_type == "string" and self.buffer.strip() == "":
            self.buffer = ""
            self.string = token
        elif sep_type == "scopein":
            self.tokens.append(Token("scopein", self.start_idx, self.start_idx + len(token), token))
        elif sep_type == "scopeout":
            self.tokens.append(Token("scopeout", self.start_idx, self.start_idx + len(token), token))
        else:
            self.buffer += token

    def flush_key(self):
        offset = 0
        if isinstance(self.key, str):
            offset += len(self.key)
            self.tokens.append(Token("type", self.start_idx - offset, self.start_idx - offset + len(self.key), self.key))
            self.key = False
        if isinstance(self.operator, str):
            offset += len(self.operator)
            self.tokens.append(Token("operator", self.start_idx - offset, self.start_idx - offset + len(self.operator), self.operator))
            self.operator = False
        if self.buffer.strip():
            offset += len(self.buffer)
            self.tokens.append(Token("value", (self.start_idx +1)- offset, self.start_idx - offset + len(self.buffer), self.buffer))
            self.clear_buffer()
    
    def undo_key(self):
        if isinstance(self.operator, str):
            self.buffer += self.operator
            self.operator = False
        if isinstance(self.key, str):
            self.buffer += self.key
            self.key = False
        
    def tokenize(self, raw_tokens: List[str]):
        self.init(raw_tokens)
        for token in raw_tokens:
            if self.escape:
                self.buffer += token
                self.escape = False
            elif isinstance(self.string, str):
                if token in self.seperators:
                    sep_type = self.seperators[token]
                    if sep_type == "string" and token == self.string:
                        self.tokens.append(Token("string", self.start_idx - (len(self.buffer) + 1), self.start_idx + 1, self.buffer))
                        self.clear_buffer()
                        self.string = False
                    else:
                        self.check_sep(token)
                else:
                    self.buffer += token

            elif isinstance(self.key, str):
                if token in self.seperators:
                    if self.seperators[token] == "ws":
                        self.key += token
                    elif self.seperators[token] == "sep":
                        # self.key += token
                        self.flush_key()
                    else:
                        self.undo_key()
                        self.buffer += token

            elif isinstance(self.operator, str):
                if token in self.seperators and self.seperators[token] == "ws":
                    self.operator += token
                elif token in self.type_keywords:
                    self.key = token
                elif token not in self.seperators:
                    if isinstance(self.operator, str):
                        self.buffer += self.operator
                        self.operator = False
            else:
                if token in self.seperators:
                    self.check_sep(token)
                elif token in self.type_keywords:
                    self.key = token
                elif token in self.operator_keywords:
                    self.operator = token
                else:
                    self.buffer += token

            # print(f"{self.start_idx=} {token=}")
            self.start_idx += len(token)
        if self.buffer:
            self.add_token("value", self.buffer)
        self.tokens.tokens.sort(key=lambda x: x.start_idx)
        return self.tokens

class Parser:
    def __init__(self) -> None:
        self.type_keywords = {
                "artist": "artist",
                "title": "title",
                "playlists": "playlists",
                "playlist": "playlists",
                "album": "playlists",
                "albums": "playlists",
                "date": "date",
                "genre": "genre",
                "duration": "duration",
                "songs": "songs",
                "song": "songs"
                }
        self.operator_keywords = {
                "and": "and",
                "or": "or",
                "|": "or",
                "&": "and"
                }

        self.seperators= {
                " ": "ws",
                "\n": "ws",
                "\t": "ws",
                "\\": "esc",
                '"': "string",
                "'": "string",
                ":": "sep",
                "(": "scopein",
                ")": "scopeout"
                }

    def _first_pass(self, string: str):
        tokens = []
        buffer = ""
        for char in string:
            if char in self.seperators:
                if len(buffer) > 0:
                    tokens.append(buffer)
                tokens.append(char)
                buffer = ""
            else:
                buffer += char
        if len(buffer) > 0:
            tokens.append(buffer)
        return tokens

    def _third_pass(self, tokens: List):
        new_tokens = []
        state = ParserState.SEARCHING
        buffer = {}
        for token in tokens:
            if state == ParserState.SEARCHING:
                if "key" in token:
                    buffer["key"] = token["key"]
                    state = ParserState.KEY
                else:
                    new_tokens.append(token)
            elif state == ParserState.KEY:
                if "value" in token:
                    # Group 1 captures which quote was used; \1 ensures the exact same quote ends the string
                    string = re.search(r"^([\"'])(.*)\1$", token["value"])
                    if string:
                        buffer["re"] = string.group(2)
                    else:
                        buffer["fuzz"] = token["value"]
                    new_tokens.append({"pair": buffer})
                    buffer = {}
                    state = ParserState.SEARCHING
                else:
                    new_tokens.append({"key": buffer["key"]})
                    buffer = {}
                    if "key" in token:
                        buffer["key"] = token["key"]
                        state = ParserState.KEY
                    else:
                        new_tokens.append(token)
                        state = ParserState.SEARCHING
        return new_tokens

    def _final_pass(self, tokens: List):
        ast = {}
        query = []
        for token in tokens:
            if not len(query) % 2 == 0:
                if "operator" in token and token["operator"] == "|":
                    query.append("or")
                elif "operator" in token and token["operator"] == "&":
                    query.append("and")

                elif "pair" in token:
                    query.append("and")
                    if token["pair"]["key"] not in self.song_key_words:
                        token["pair"]["key"] = "title"
                    query.append(token["pair"])
            else:
                if "pair" in token:
                    if token["pair"]["key"] not in self.song_key_words:
                        token["pair"]["key"] = "title"
                    query.append(token["pair"])
                elif "key" in token:
                    ast["results"] = token["key"]
        if query == []:
            return None
        ast["query"] = query
        if "results" not in ast or ast["results"] not in self.type_key_words:
            ast["results"] = "playlists"
        return ast
            
    def parse(self, string: str) -> Optional[Dict]:
        result = self._final_pass(self._third_pass(self._secound_pass(self._first_pass(string))))
        if result:
            return result

if __name__ == "__main__":
    string = input(">")
    correct_ast = Pair("songs", "scope", [Pair("artist", "fuzz", "ironmouse"), Operator("and"), Pair("songs", "scope", [Pair("title", "re", "left right*"), Operator("or"), Pair("title", "re", "devil")])])
    print(f"{string=}")
    parser = Parser()
    tk = Tokenizer(parser.type_keywords, parser.operator_keywords, parser.seperators)
    raw_tokens = parser._first_pass(string) 
    print(f"{raw_tokens=}")
    tokens: Tokens = tk.tokenize(raw_tokens)
    print(f"{tokens=}")
    colorized = ""
    index = 0
    token_idx = 0
    colors = {
            "type": "\x1b[38;2;255;0;0m",
            "string": "\x1b[38;2;0;255;0m",
            "value": "\x1b[38;2;255;255;0m",
            "operator": "\x1b[38;2;0;0;255m",
            "scopein": "\x1b[38;2;0;0;255m",
            "scopeout": "\x1b[38;2;0;0;255m",
            }
    while index < len(string): 
        if tokens[token_idx].start_idx == index:
            token = tokens[token_idx]
            orig = string[token.start_idx: token.end_idx]
            index += len(orig)
            token_idx += 1
            colorized += colors[token.type] + orig + "\x1b[0m"
        else:
            colorized += string[index]
            index += 1
    print(colorized)

    # third = parser._third_pass(secound)
    # print(f"{third=}")
    # result = parser._final_pass(third)
    # print(f"{result=}")
