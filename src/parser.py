from typing import Optional
from lexer import Token, Tokens, Lexer
from langdef import basic_types, token_types
import langdef

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
    def __init__(self) -> None:
        self.type_keywords = langdef.type_keywords
        self.operator_keywords = langdef.operator_keywords
        self.defualts = langdef.defulats
        self.valid_output_paths = langdef.valid_output_paths
        self.tokens = Tokens()
        self.results = Pair()
        self.scope_stack = []
        self.index = 0
    def _get_valid_paths(self):
        token = self.tokens[self.index -1]
        if token.token_type is not None:
            return self.valid_output_paths[token.token_type]
        raise SyntaxError(f"Token '{token}' has no token_type")

    def _insert_token(self, token_type: token_types):
        self.tokens.insert(self.index, Token((self.tokens[self.index - 1].start_idx[0], self.tokens[self.index - 1].start_idx[1] + 1), self.defualts[token_type], token_type=token_type, virtual=True))
        self._manage_scope()
        # self.index += 1

    def _manage_scope(self):
        token = self.tokens[self.index]
        if token.token_type == token_types.R_OP:
            if len(self.scope_stack) > 0:
                self.scope_stack.pop()

        if token.token_type == token_types.L_OP and token.start_idx not in self.scope_stack:
            self.scope_stack.append(token.start_idx)

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
                self.index += 1
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
        self.pairs = self._get_pair()
        self.results = Pair(self.defualts[token_types.TYPE].replace(" ", "").replace(":", ""), "scope", self._get_pair()) if len(self.pairs) > 1 else self.pairs[0]
        return self.results

if __name__ == "__main__":
    string = 'playlists: artist: "*iron*" (title: king | title: "Left*")'
    string = "playlists: (artist: ironmouse and songs: (title: 'king*' or title: 'left*') and artist: shiro beats)"
    print(f"{string=}")

    parser = Parser()
    tk = Lexer()
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
