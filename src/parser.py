import enum
from typing import Dict, List, Optional
from lexer import Token, Lexer, Tokens
import re

class Pair:
    def __init__(self, key: Optional[str] = None, data_type: Optional[str] = None, data = []) -> None:
        self.key = key
        self.data_type = data_type
        self.data = data

    def __repr__(self) -> str:
        if isinstance(self.data, list):
            string = f"('{self.key}' :["
            for i in self.data:
                string += f"{i.__repr__()}"
                if i != self.data[-1]:
                    string += ", "

            return string + "])"
        else:
            return f"('{self.key}': '{self.data}')"


class Operator:
    def __init__(self, data) -> None:
        self.data = data

    def __repr__(self) -> str:
        return f"('operator': '{self.data}')"


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
        self.def_key = "title"

    def _get_value(self, token: Token):
        if token.type == "type":
            value = token.value.replace(":", "").replace(" ", "")
        elif token.type == "value":
            pattern = r"^\s*(\"|')(.*)(\1)\s*$"
            results = re.search(pattern, token.value)
            if results:
                value = results.group(2)
            else:
                value = token.value.strip()
        else:
            value = token.value.strip()
        return value

    def _first_pass(self, tokens: Tokens):
        results = []
        current = Pair()
        scope = Tokens()
        scopes = []
        for token in tokens:
            if scopes == []:
                if token.type == "type":
                    if current.key is None:
                        current.key = self._get_value(token)
                    else:
                        scopes.append("imp")
                        scope.append(token)

                elif token.type == "scopein":
                    scopes.append(self._get_value(token))

                elif token.type == "value":
                    if current.key is None:
                        current.key = self.def_key
                    current.data_type = "value"
                    current.data = self._get_value(token)
                    results.append(current)
                    current = Pair()

                elif token.type == "operator":
                    results.append(Operator(self.operator_keywords[token.value.strip()]))
                    current = Pair()

                elif len(scope.tokens) > 0:
                    if current.key is None:
                        current.key = "songs"
                    current.data_type = "scope"
                    current.data = self._first_pass(scope)
                    results.append(current)
                    current = Pair()
                    scope = Tokens()

                    
            elif token.type == "scopein":
                scopes.append(self._get_value(token))
                scope.append(token)

            elif token.type == "scopeout":
                scopes.pop()
                if token.value == "EOF":
                    scopes = []
                scope.append(token)

            else:
                scope.append(token)

        if len(scope.tokens) > 0:
            if current.key is None:
                current.key = "songs"
            current.data_type = "scope"
            current.data = self._first_pass(scope)
            results.append(current)
            current = Pair()

        if len(results) == 1:
            return results[0]
        return results

    def _secound_pass(self, ast: Pair):
        assert isinstance(ast, Pair), f"{ast=}"
        if ast.data_type == "scope":
            data = []
            assert isinstance(ast.data, List), f"{ast.data=}"
            for index, pair in enumerate(ast.data):
                if index % 2 != 0:
                    if isinstance(pair, Operator):
                        data.append(pair)
                    else:
                        data.append(Operator("and"))
                        data.append(self._secound_pass(pair))
                else:
                    assert isinstance(pair, Pair), f"{pair}, {ast}"
                    data.append(self._secound_pass(pair))
            ast.data = data
        return ast


    def parse(self, tokens: Tokens) -> Optional[Pair]:
        result = self._secound_pass(self._first_pass(tokens))
        if result:
            return result

if __name__ == "__main__":
    string = 'songs: artist: ironmouse (title: "left right*" or title : "devil")'
    # string = input(">")
    correct_ast = Pair("songs", "scope", [Pair("artist", "fuzz", "ironmouse"), Operator("and"), Pair("songs", "scope", [Pair("title", "re", "left right*"), Operator("or"), Pair("title", "re", "devil")])])
    print(f"{string=}")
    parser = Parser()
    tk = Lexer(parser.type_keywords, parser.operator_keywords, parser.seperators)
    tokens: Tokens = tk.lex(string)
    print(f"{tokens=}")
    secound = parser._first_pass(tokens)
    print(f"{secound=}")
    results = parser.parse(tokens)
    print(f"{results=}")
    print(f"results={correct_ast}")
