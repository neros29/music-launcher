from sys import path
path.append("src/")
from query import Playlist, Query, Song
from parser import Pair, Parser
from lexer import Lexer, basic_types
import query
import re


class QueryRunner:
    def __init__(self, root: query.Query) -> None:
        self.root = root

    def _glob_to_regex(self, glob_pattern):
        regex_pattern = re.escape(glob_pattern)
        regex_pattern = regex_pattern.replace(r'\*', '.*')
        regex_pattern = regex_pattern.replace(r'\?', '.')
        regex_pattern = f"^{regex_pattern}$"
        return regex_pattern

    def run(self, ast: Pair): 
        return self._interpert(ast, self.root)

    def _interpert(self, ast: Pair, search_space):
        if ast.data_type == "fuzz":
            results = search_space.get_songs_batch(ast.key, search_space.fuzz(ast.key, ast.data))
            if results == NotImplemented:
                return query.Songs()
            return results
        elif ast.data_type == "re":
            results = search_space.get_songs_batch(ast.key, search_space.regex(ast.key, self._glob_to_regex(ast.data)))
            if results == NotImplemented:
                return query.Songs()
            return results
        elif ast.data_type == "scope":
            op = None
            results = None
            for pair in ast.data:
                if pair.data_type == "operator":
                    op = pair.data
                    continue
                elif isinstance(pair, Pair):
                    if results is None:
                        assert op is None, "Something bad happened"
                        results = self._interpert(pair, search_space)
                    elif op == "and":
                        results = self._interpert(pair, results)
                        if results == NotImplemented:
                            results = query.Songs()
                    elif op == "or":
                        results = results.concat_or(self._interpert(pair, search_space))
                        if results == NotImplemented:
                            results = query.Songs()
                    else:
                        raise SyntaxError(f"operator {op} dose not exist.")
            if ast.key == "playlists":
                return self.root.get_playlists(results)
            elif ast.key == "songs":
                return results
            elif ast.key == "all":
                return Playlist(results)
            else:
                return results
        else:
            raise SyntaxError(f"data_type {ast.data_type} dose not exist.")
        

if __name__ == "__main__":
    q = Query("data/db.json")
    qr = QueryRunner(q)
    lexer = Lexer()
    parser = Parser()

    string = 'all: artist: ironmouse (title: "king*" or title: "left*")'

    import time
    tokens = lexer.lex(string)
    ast = parser.parse(tokens)
    start = time.time()
    values = qr.run(ast)
    print(f"{time.time() - start=}")
    print(f"{ast=}")
    assert values != None;
    for i in values:
        if isinstance(i, Playlist):
            print(i.playlist_name)
        elif isinstance(i, Song):
            print(f"{i.name} artist: {i.get_values('artist')}")
