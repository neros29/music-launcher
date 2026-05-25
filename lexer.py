from typing import List, Optional
from parser import Parser

class Token:
    def __init__(self, end_idx: int, value: str) -> None:
        self.type = None
        self.start_idx = end_idx - len(value)
        self.end_idx = end_idx
        self.value = value

    def set_type(self, token_type):
        self.type = token_type
    
    def __repr__(self) -> str:
        return self.value

    def __add__(self, other):
        if isinstance(other, Token):
            return Token(other.end_idx, self.value + other.value)

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
        self.tokens: List[Token] = []

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
        results += "]"

        return results

class Lexer:
    def __init__(self, type_keywords, operator_keywords, seperators) -> None:
        self.type_keywords = type_keywords
        self.operator_keywords = operator_keywords
        self.seperators = seperators

        self.tokens: Optional[Tokens] = None

        self.value: Optional[Token] = None

        self.string = None
        self.escape = False
        self.operator = None
        self.key = None

    def _value_add(self, token: Token): 
        if self.value is None:
            self.value = token
        else:
            self.value += token

    def _push_value(self):
        if self.value is not None and  self.tokens is not None:
            if self.value.value.strip() == "":
                self.value.set_type("ws")
            else:
                self.value.set_type("value")
            self.tokens.append(self.value)
            self.value = None

    def _undo_op_guess(self):
        if self.operator is not None:
            self._value_add(self.operator)
            self.operator = None

    def _undo_guess(self):
        if self.key is not None:
            self._undo_op_guess()
            self._value_add(self.key)
            self.key = None
    
    def _append_op(self):
        if self.operator is not None and self.tokens is not None:
            if self.operator.value.strip() in self.operator_keywords:
                self.operator.set_type("operator")
            elif self.operator.value.strip() in self.seperators:
                self.operator.set_type(self.seperators[self.operator.value.strip()])
            self.tokens.append(self.operator)
            self.operator = None

    def _get_tokens(self, string: str):
        buffer = ""
        for index, char in enumerate(string):
            if char in self.seperators:
                if len(buffer) > 0:
                    yield Token(index, buffer)
                yield Token(index + 1, char)
                buffer = ""
            else:
                buffer += char
        if len(buffer) > 0:
            yield Token(len(string), buffer)
        yield Token(len(string) + 1, "EOF")

    def lex(self, string: str):
        self.tokens = Tokens()
        for token in self._get_tokens(string):
            if self.escape:
                self._value_add(token)
                self.escape = False

            elif token.value == "EOF":
                if self.operator:
                    if self.operator.value.strip() in self.seperators:
                        self.operator.set_type(self.seperators[self.operator.value.strip()])
                        self.tokens.append(self.operator)
                    else:
                        self._value_add(self.operator)
                elif self.key:
                    self._value_add(self.key)
                self._push_value()

            elif self.string:
                if token in self.seperators:
                    sep_type = self.seperators[token.value]
                    if sep_type == "string" and token == self.string:
                        if self.value is not None:
                            self._value_add(token)
                            self.value.set_type("string")
                            self.tokens.append(self.value)
                            self.value = None
                            self.string = None
                    elif sep_type == "esc":
                        self.escape = True
                        self._value_add(token)
                    else:
                        self._value_add(token)
                else:
                    self._value_add(token)

            elif self.key:
                if token in self.seperators:
                    if self.seperators[token.value] == "ws":
                        self.key += token
                    elif self.seperators[token.value] == "sep":
                        self.key += token
                        self._push_value()
                        self._append_op()
                        if self.key:
                            self.key.set_type("type")
                            self.tokens.append(self.key)
                            self.key = None
                    else:
                        self._undo_guess()
                        self._value_add(token)
                else:
                    self._undo_guess()
                    self._value_add(token)

            elif self.operator:
                if token in self.seperators and self.seperators[token.value] == "ws":
                    self.operator += token
                elif token in self.type_keywords:
                    self.key = token
                elif token not in self.seperators:
                    self._undo_op_guess()
                    self._value_add(token)
            else:
                if token in self.seperators:
                    sep_type = self.seperators[token.value]
                    if sep_type == "string":
                        if self.value is None or self.value.value.strip() == "":
                            self.string = token
                        self._value_add(token)
                    elif sep_type == "esc":
                        self.escape = True
                    elif sep_type == "scopein" or sep_type == "scopeout":
                        self.operator = token
                    else:
                        self._value_add(token)
                elif token in self.type_keywords:
                    self.key = token
                elif token in self.operator_keywords:
                    self.operator = token
                else:
                    self._value_add(token)

        self.tokens.tokens.sort(key=lambda x: x.start_idx)
        return self.tokens


if __name__ == "__main__":
    string = 'artist: "*iron*" (title: title or artist i : & | and outher or or or title : "Left*")'
    print(f"{string=}")
    parser = Parser()
    tk = Lexer(parser.type_keywords, parser.operator_keywords, parser.seperators)
    tokens: Tokens = tk.lex(string)
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
