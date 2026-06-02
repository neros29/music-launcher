from pathlib import Path
from typing import List
from thefuzz import fuzz
from parser import Pair, Parser
from lexer import Lexer
import json

class Song:
    def __init__(self, song_path: str, score_list: List, root: 'Query') -> None:
        self.root = root
        self.path = song_path
        self.score_list = score_list

        self.score = 0
        for score in self.score_list:
            self.score += score[1]
    def get(self, key: str):
        return self.root.data[self.path][key]

class Playlist:
    def __init__(self, songs: List[Song], playlist_name: str, root_song: Song) -> None:
        self.name = playlist_name
        self.root_song = root_song
        self.songs = songs
        self.artist = self._get_artist()

    def _get_artist(self):
        results = {}
        for song in self.songs:
            artists = [i.strip() for i in song.get("artist").split(",")]
            for artist in artists:
                if artist not in results:
                    results[artist] = 1
                else:
                    results[artist] += 1
        most_aperences = 0
        most_aperences_name = ""
        for artist in results:
            if results[artist] > most_aperences:
                most_aperences_name = artist
                most_aperences = results[artist]
        return most_aperences_name

    def __iter__(self):
        for i in self.songs:
            yield i


class Query:
    def __init__(self, db_path) -> None:
        self.db_path: Path = db_path if isinstance(db_path, Path) else Path(db_path)
        self.data = self._load_file()
        self.funcs = {
                "fuzz": self._fuzz,
                "re": self._glob,
                "eq": self._eq,
                }
        self.op_funcs = {
                "and": self._and,
                "or": self._or,
                None: self._or,
                }
        self._fuzz_cache = {}
        self._playlist_cache = {}

    def _load_file(self):
        if not self.db_path.is_file():
            raise FileNotFoundError(f"File {self.db_path} dose not exst.")
        with open(self.db_path, "r") as f:
            data = json.load(f)
        return data["music"]

    def _and(self, b1: bool, b2: bool):
        return b1 and b2

    def _or(self, b1: bool, b2: bool):
        return b1 or b2

    def _eq(self, v1: str, v2: str):
        return float(v1 == v2)

    def _fuzz(self, value: str, query: str):
        cached =  self._fuzz_cache.get((value, query))
        if cached:
            return cached
        min_score = 60
        p_ratio = fuzz.partial_token_sort_ratio(value, query)
        if p_ratio < min_score - 5:
            self._fuzz_cache[(value, query)] = 0
            return 0
        s_ratio = fuzz.token_sort_ratio(value, query)
        score = ((p_ratio * 0.80) + (s_ratio * 0.20))
        result = max((score - min_score) / (100 - min_score), 0)
        self._fuzz_cache[(value, query)] = result
        return result

    def _glob(self, string: str, pattern: str):
        pattern_idx, string_idx = 0, 0
        pattern_star_idx = -1
        string_backtrack_idx = -1

        p_len = len(pattern)
        s_len = len(string)
        while string_idx < s_len:
            if pattern_idx < p_len and (pattern[pattern_idx] == string[string_idx] or pattern[pattern_idx] == '?'):
                pattern_idx += 1
                string_idx += 1
                
            elif pattern_idx < p_len and pattern[pattern_idx] == '*':
                pattern_star_idx = pattern_idx
                string_backtrack_idx = string_idx
                pattern_idx += 1 

            elif pattern_star_idx != -1:
                pattern_idx = pattern_star_idx + 1
                string_backtrack_idx += 1
                string_idx = string_backtrack_idx

            else:
                return 0
        while pattern_idx < p_len and pattern[pattern_idx] == '*':
            pattern_idx += 1

        return float(pattern_idx == p_len)

    def _score_song(self, song: str, querys: List[dict]):
        result = False
        score = []
        song_data = self.data[song]
        for query in querys:
            if query["op"] == "and" and not result:
                return (False, [])
            elif query["op"] == "or" and result:
                continue
            elif query["func"] == "self":
                query_result, s = self._score_song(song, query["value"])
                score = s + score
            elif query["func"] in self.funcs:
                value = song_data.get(query["key"])
                if value is None:
                    return (False, [])
                if isinstance(value, dict):
                    query_result = 0.0
                    for val in value:
                        query_result = self.funcs[query["func"]](val.lower().strip(), query["value"])
                        if query_result > 0:
                            break
                else:
                    query_result = self.funcs[query["func"]](value.lower().strip(), query["value"])
                if query_result > 0:
                    score.append([query["key"], query_result])
            else:
                print("function not found")
                continue
            result = self.op_funcs[query["op"]](result, query_result > 0)
        return (result, score)

    def _query_db(self, querys):
        results = []
        for song in self.data:
            result = self._score_song(song, querys)
            if result[0]:
                results.append(Song(song, result[1], self))
        return results

    def _compile_ast(self, ast: Pair, i_op = None):
        if ast.data_type != "scope":
            return [{"func": ast.data_type, "key": ast.key, "value": ast.data, "op": i_op}]
        op = None
        results = []
        for pair in ast.data:
            if pair.data_type == "operator":
                op = pair.data
            else:
                results += self._compile_ast(pair, op)
        return [{"func": "self", "key": ast.key.strip().lower() if isinstance(ast.key, str) else ast.key, "value": results.strip().lower() if isinstance(results, str) else results, "op": i_op}]

    def get_playlsits(self, songs: List[Song]):
        playlists_names = {}
        for root_song in songs:
            for playlist in root_song.get("playlists"):
                playlists_names[playlist] = {"songs": [], "root_song": root_song}
        for song in self.data:
            for playlist in self.data[song].get("playlists", []):
                if playlist in playlists_names:
                    playlists_names[playlist]["songs"].append(Song(song, [], self))
        results = []
        for playlist in playlists_names:
            results.append(Playlist(playlists_names[playlist]["songs"], playlist, playlists_names[playlist]["root_song"]))
        return results


    def query(self, ast: Pair):
        asm = self._compile_ast(ast)
        results = self._query_db(asm)
        results.sort(key=lambda x: x.score, reverse=True)
        if asm[0]["key"] == "playlists":
            playlists = self.get_playlsits(results)
            return playlists
        return results
        

if __name__ == "__main__":
    query = Query("data/db.json")
    parser = Parser()
    lexer = Lexer()

    string = "songs: artist: ironmouse (title: 'king*' or title: 'l"
    string = "playlists: a"
    string = "songs: songs:(artist: ironmouse or artist: shirobeats) and (title: 'king*' or title: 'show off*')"
    tokens = lexer.lex(string)
    ast = parser.parse(tokens)
    import time
    print(string)
    print(ast)
    start = time.time()
    results = query.query(ast)
    print(f"query.query took {time.time() - start}")
    # for song in results:
    #     print(f"songs: {song.get('title')}: {song.score_list}")
    # for playlist in results:
    #     print(f"{playlist.name}")
