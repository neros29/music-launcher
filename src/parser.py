from typing import Optional
from lexer import Token, Tokens, token_types, basic_types, Lexer

class Pair:
    def __init__(self, key: Optional[str] = None, data_type: Optional[str] = None, data = []) -> None:
        self.key = key
        self.data_type = data_type
        self.data = data

    def __repr__(self) -> str:
        if isinstance(self.data, list):
            string = f"('{self.key}': ["
            for i in self.data:
                string += f"{i.__repr__()}"
                if i != self.data[-1]:
                    string += ", "

            return string + "])"
        else:
            return f"('{self.key}': '{self.data}')"


class Parser:
    def __init__(self, type_keywords, operator_keywords) -> None:
        self.type_keywords = type_keywords
        self.operator_keywords = operator_keywords
        self.valid_output_paths = {
                token_types.SOF     : [token_types.TYPE, token_types.EOF],
                token_types.TYPE    : [token_types.L_OP, token_types.VALUE, token_types.S_VALUE],
                token_types.VALUE   : [token_types.OP, token_types.R_OP, token_types.EOF],
                token_types.S_VALUE : [token_types.OP, token_types.R_OP,  token_types.EOF],
                token_types.OP      : [token_types.TYPE],
                token_types.L_OP    : [token_types.TYPE],
                token_types.R_OP    : [token_types.TYPE, token_types.R_OP, token_types.EOF],
                }
        self.tokens = Tokens()
        self.results = Pair()
        self.scope_stack = []
        self.index = 0
        self.defulats = {
                token_types.TYPE: " artist:",
                token_types.L_OP: "(",
                token_types.R_OP: ")",
                token_types.OP: " and ",
                }

    def _get_valid_paths(self):
        token = self.tokens[self.index -1]
        if token.token_type is not None:
            return self.valid_output_paths[token.token_type]
        raise SyntaxError(f"Token '{token}' has no token_type")

    def _insert_token(self, token_type: token_types):
        self.tokens.insert(self.index, Token((self.tokens[self.index - 1].start_idx[0], self.tokens[self.index - 1].start_idx[1] + 1), self.defulats[token_type], token_type=token_type, virtual=True))
        self._manage_scope()
        # self.index += 1

    def _manage_scope(self):
        token = self.tokens[self.index]
        if token.token_type == token_types.R_OP:
            if len(self.scope_stack) > 0:
                self.scope_stack.pop()

        if token.token_type == token_types.L_OP:
            self.scope_stack.append(token.value)

    def _fix_tokens(self):
        valid = None
        while True:
            token = self.tokens[self.index]
            if token.basic_type == basic_types.EOF:
                if 0 < len(self.scope_stack):
                    self.scope_stack.pop()
                    self._insert_token(token_types.R_OP)
                    self.index += 1
                    continue
                else:
                    break
            self._manage_scope()
            if valid is not None and token.token_type not in valid:
                self._insert_token(valid[0])

            self.index += 1
            valid = self._get_valid_paths()

    #TODO:  artist: selena gomez and aritst: ironmouse -> songs: (artist: selena gomez and aritst: ironmouse)
    def _get_type(self, token: Token):
        return self.type_keywords[token.value.replace(":", "").replace(" ", "")]

    def _get_value(self, token: Token):
        return token.value.strip().replace("\\", "")

    def _get_s_value(self, token: Token):
        return token.value.strip()[1:-1]

    def _get_pair(self):
        pairs = []
        pair = Pair()

        while True:
            token = self.tokens[self.index]
            if token.token_type == token_types.L_OP:
                if pair.data == []:
                    self.index += 1
                    pair.data = self._get_pair()
                    pair.data_type = "scope"
                    pairs.append(pair)
                    pair = Pair()
                    continue
            elif token.token_type == token_types.R_OP:
                break

            elif token.token_type == token_types.EOF:
                break

            elif token.token_type == token_types.TYPE:
                pair.key = self._get_type(token)

            elif token.token_type == token_types.VALUE:
                pair.data = self._get_value(token)
                pair.data_type = "fuzz"
                pairs.append(pair)
                pair = Pair()

            elif token.token_type == token_types.S_VALUE:
                pair.data = self._get_s_value(token)
                pair.data_type = "re"
                pairs.append(pair)
                pair = Pair()

            elif token.token_type == token_types.OP:
                pair.data = self.operator_keywords[token.value.strip()]
                pair.data_type = "operator"
                pairs.append(pair)
                pair = Pair()
            self.index += 1

        return pairs
        

    def parse(self, tokens: Tokens):
        self.tokens = tokens

        self.results = Pair()
        self.scope_stack = []
        self.index = 0

        self._fix_tokens()
        self.index = 0
        self.results = Pair(self.defulats[token_types.TYPE], "scope", self._get_pair())
        return self.results

if __name__ == "__main__":
    type_keywords = {
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

    operator_keywords = {
            "and": "and",
            "or": "or",
            "|": "or",
            "&": "and"
            }

    seperators= {
            " ": basic_types.WS,
            "\n": basic_types.WS,
            "\t": basic_types.WS,
            "\\": basic_types.ESC,
            '"': basic_types.D_QUOTES,
            "'": basic_types.S_QUOTES,
            ":": basic_types.SEP,
            "(": basic_types.L_OP,
            ")": basic_types.R_OP
            }
    string = 'playlists: artist: "*iron*" (title: king | title: "Left*")'
    print(f"{string=}")

    parser = Parser(type_keywords, operator_keywords)
    tk = Lexer(type_keywords, operator_keywords, seperators)
    tokens: Tokens = tk.lex(string)
    parser.tokens = tokens
    parser._fix_tokens()
    secound = parser.tokens
    print("string='", end="")
    for i in secound:
        print(i, end="")
    print("'")
    parser.index = 0
    results = parser.parse(tokens)
    print(f"{results=}")
