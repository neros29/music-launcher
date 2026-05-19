from typing import Dict


class Lexer:
    def __init__(self) -> None:
        pass

    def lex(self, string: str) -> Dict:
        return {}


if __name__ == "__main__":
    string = 'songs: artist: "*iron*" & title: Arent we all teh worst'
    value = {r"results": r"songs", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}]}
    lexer = Lexer()
    print(lexer.lex(string))
    print(lexer.lex(string) == value)
