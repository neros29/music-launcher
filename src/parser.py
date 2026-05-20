from typing import Dict, List, Optional
from enum import Enum, auto
import re

class ParserState(Enum):
    """Defines the possible states of our query parser."""
    SEARCHING = auto()   # Looking for the start of a key or value
    KEY = auto()    # Currently inside a key


class Parser:
    def __init__(self) -> None:
        self.song_key_words = ["artist", "title", "playlists", "date", "genre", "duration"]
        self.type_key_words = ["playlists", "songs", "all"]
        self.all_key_words = self.type_key_words + self.song_key_words
        self.operators = ["&", "|"]

    def _first_pass(self, string: str):
        tokens = []
        buffer = ""
        delimiters = [" ", ":"] + self.operators
        for char in string:
            if char in delimiters:
                if len(buffer) > 0:
                    tokens.append(buffer)
                tokens.append(char)
                buffer = ""
            else:
                buffer += char
        if len(buffer) > 0:
            tokens.append(buffer)
        return tokens

    def _secound_pass(self, tokens: List):
        state = ParserState.SEARCHING
        new_tokens = []
        key_buffer = ""
        value_buffer = ""
        operator_buffer = ""
        for token in tokens:
            if state == ParserState.SEARCHING:
                if token.lower() in self.all_key_words:
                    key_buffer += token
                    state = ParserState.KEY
                elif token in self.operators:
                    operator_buffer += token
                else:
                    value_buffer += token
            elif state == ParserState.KEY:
                if token == ":":
                    if value_buffer.strip():
                        new_tokens.append({"value": value_buffer.strip()})
                        value_buffer = ""
                    if operator_buffer.strip():
                        new_tokens.append({"operator": operator_buffer.replace(" ", "")})
                        operator_buffer = ""
                    if key_buffer.strip():
                        new_tokens.append({"key": key_buffer.replace(" ", "").lower()})
                        key_buffer = ""
                    state = ParserState.SEARCHING
                elif token == " ":
                    key_buffer += token
                else:
                    value_buffer += operator_buffer
                    operator_buffer = ""
                    value_buffer += key_buffer
                    key_buffer = ""
                    value_buffer += token
                    state = ParserState.SEARCHING
        value_buffer += operator_buffer
        assert key_buffer == ""
        if value_buffer:
            new_tokens.append({"value": value_buffer.strip()})
        return new_tokens

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
    string = 'artist: "*iron*" title:Arent we all teh worst | title : \'Left*\'' 
    string = 'album: "Hybrid Theory"'
    correct_results = {r"results": r"playlists", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}, r"or", {r"key": r"title", r"re": "Left*"}]}
    parser = Parser()
    first = parser._first_pass(string) 
    secound = parser._secound_pass(first) 
    third = parser._third_pass(secound)
    result = parser._final_pass(third)
    print(f"{string=}")
    print(f"{first=}")
    print(f"{secound=}")
    print(f"{third=}")
    print(f"{result=}")
    print(f"{correct_results=}")
    correct = result == correct_results
    print(f"{correct=}")
