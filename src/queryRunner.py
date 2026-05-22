from sys import path
path.append("src/")
from query import Playlist, Query, Song
from parser import Pair, Operator
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
            return self.root.get_songs_batch(ast.key, self.root.fuzz(ast.key, ast.data))
        elif ast.data_type == "re":
            return self.root.get_songs_batch(ast.key, self.root.regex(ast.key, self._glob_to_regex(ast.data)))
        elif ast.data_type == "scope":
            op = None
            results = None
            for pair in ast.data:
                if isinstance(pair, Operator):
                    op = pair.data
                    continue
                elif isinstance(pair, Pair):
                    if results is None:
                        assert op is None, "Something bad happened"
                        results = self.run(pair)
                    elif op == "and":
                        results = results.concat_and(self.run(pair))
                    elif op == "or":
                        results = results.concat_or(self.run(pair))
                    else:
                        raise SyntaxError(f"operator {op} dose not exist.")
            if ast.key == "playlists":
                return self.root.get_playlists(results)
            elif ast.key == "songs":
                return results
            elif ast.key == "all":
                return Playlist(results)
        else:
            raise SyntaxError(f"data_type {ast.data_type} dose not exist.")



        

if __name__ == "__main__":
    q = Query("data/db.json")
    qr = QueryRunner(q)

    tokens = Pair("songs", "scope", [Pair("artist", "fuzz", "ironmouse"), Operator("and"), Pair("songs", "scope", [Pair("title", "re", "left right*"), Operator("or"), Pair("title", "re", "devil")])])
    # songs: artist: this means artist is in side the songs: scope. it is functionaly equivlent to songs: (artist: ...)
    # a scope is denoted as a list with the pair operater pair pattern all scopes must have an odd number length and must have an operatorer on every even number with in the list.
    # playlists: duration: <3 & playlists: artist: ironmouse | artist: shirobeats
    # type: eval((type: name = get(type, name) & type: eval((type: name = get(type, name) | type: name = get(type, name)))))
    # I need a way to hold three diffrent values in a single type: name pair, the first is the type this is what we are searching in, then we have the function this is what function we want to call and last is the data. 
    # eval runs on scopes, get runs on type: name 

    values = qr.run(tokens)
    assert values != None;
    for i in values:
        if isinstance(i, Playlist):
            print(i.playlist_name)
        elif isinstance(i, Song):
            print(i.name)
