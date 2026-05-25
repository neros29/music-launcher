from typing import Dict, List, Optional
import re

class Pair:
    def __init__(self, key: str, data_type: str, data) -> None:
        self.key = key
        self.data_type = data_type
        self.data = data

class Operator:
    def __init__(self, data) -> None:
        self.data = data


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
    string = 'artist: "*iron*" (title: title or artist i : & | and outher or or or title : "Left*")'
    string = input(">")
    print(f"{string=}")
    parser = Parser()
    tk = Tokenizer(parser.type_keywords, parser.operator_keywords, parser.seperators)
    raw_tokens = parser._first_pass(string) 
    tokens: Tokens = tk.tokenize(raw_tokens)
    colorized = ""
    colors = {
            "type": "\x1b[38;2;255;0;0m",
            "string": "\x1b[38;2;0;255;0m",
            "value": "\x1b[38;2;255;255;0m",
            "operator": "\x1b[38;2;0;0;255m",
            "scopein": "\x1b[38;2;0;0;255m",
            "scopeout": "\x1b[38;2;0;0;255m",
            "ws": "",
            }
    for token in tokens:
        colorized += colors[token.type] + token.value + "\x1b[0m"

    print(f"string='{colorized}'")
    print(f"{tokens=}")
    # third = parser._third_pass(secound)
    # print(f"{third=}")
    # result = parser._final_pass(third)
    # print(f"{result=}")
