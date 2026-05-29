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
        if ast.data_type == "fuzz":
            results = self.root.get_songs_batch(ast.key, self.root.fuzz(ast.key, ast.data))
            if results == NotImplemented:
                return query.Songs()
            return results
        elif ast.data_type == "re":
            results = self.root.get_songs_batch(ast.key, self.root.regex(ast.key, self._glob_to_regex(ast.data)))
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
                        results = self.run(pair)
                    elif op == "and":
                        results = results.concat_and(self.run(pair))
                        if results == NotImplemented:
                            results = query.Songs()
                    elif op == "or":
                        results = results.concat_or(self.run(pair))
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
    q = Query("data/db.json")
    qr = QueryRunner(q)
    lexer = Lexer(type_keywords, operator_keywords, seperators)
    parser = Parser(type_keywords, operator_keywords)
    string = 'songs: artist: ironmouse (title: "left right*" or title: "devil")'
    tokens = lexer.lex(string)
    ast = parser.parse(tokens)
    tokens = Pair("songs", "scope", [Pair("artist", "fuzz", "ironmouse"), Pair(None, "operator", "and"), Pair("songs", "scope", [Pair("title", "re", "left right*"), Pair(None, "operator", "or"), Pair("title", "re", "devil")])])
    print(f"{ast=}")
    values = qr.run(ast)
    assert values != None;
    for i in values:
        if isinstance(i, Playlist):
            print(i.playlist_name)
        elif isinstance(i, Song):
            print(i.name)
