from logging import root
from pathlib import Path
from typing import List, Optional
from rapidfuzz import fuzz
from parser import Pair, Parser
from random import shuffle
from lexer import Lexer
import time
import json

class Song:
    def __init__(self, song_path: str, score_list: List, root: 'Query', query: List[dict]) -> None:
        self.root = root
        self.query = query
        self.path = song_path
        self.score_list = score_list
        self.score = 0

        for score in self.score_list:
            self.score += score[1]

    def get(self, key: str):
        return self.root.data[self.path][key]

class Playable:
    def __init__(self, playable: List, playable_type: str) -> None:
        self.playable_type: str = playable_type
        self.playable: List = playable
        self.type: str = "playlist" if len(playable) > 0 and isinstance(playable[0], Playlist) else "song"
        self.sort()

    def sort(self):
        if self.type == "playlist":
            self.playable.sort(key=lambda x: (x.score, len(x.songs)), reverse=True)
        else:
            self.playable.sort(key=lambda x: x.score, reverse=True)

    def get_playable(self, index: int):
        if self.type == "playlist":
            return [i.path for i in self.playable[index]]
        if self.type == "song":
            return [self.playable[index].path]

    def get_playable_type(self):
        return self.playable_type

    def __iter__(self):
        for i in self.playable:
            yield i

class Playlist:
    def __init__(self, songs: List[Song], playlist_name: str, root_song: Optional[Song]) -> None:
        self.name = playlist_name
        self.root_song = root_song
        self.songs: List[Song] = songs
        self.artist = self._get_artist()
        self._sort_song()
        self.score = self._get_score()

    def _sort_song(self):
        if self.name != "":
            self.songs.sort(key=lambda x: x.get("playlists")[self.name] if x.get("playlists").get(self.name) is not None else float("inf"))

    def _get_score(self):
        score = 0
        for song in self.songs:
            score += song.score
        return score / max(len(self.songs), 1)

    def _get_artist(self):
        unformated = {}
        results = {}
        first_seen_order = {}
        order_counter = 0
        for song in self.songs:
            artists = set()
            for a in song.get("artist"):
                none_formated = a
                a = a.strip().lower()
                if a not in artists:
                    artists.add(a)
                    if a not in first_seen_order:
                        first_seen_order[a] = order_counter
                        order_counter += 1
                    unformated[a] = none_formated
                    results[a] = results.get(a, 0) + 1
        most_appearances = max(results.values(), default=0)
        top_artists = [a for a, c in results.items() if c == most_appearances]
        top_artists.sort(key=lambda a: first_seen_order[a])
        if top_artists:
            return unformated[top_artists[0]]
        return ""

    def __iter__(self):
        for i in self.songs:
            yield i


class Query:
    def __init__(self, db_path) -> None:
        self.db_path: Path = db_path if isinstance(db_path, Path) else Path(db_path)
        self.data = self._load_file()
        self.generator = None
        self.query_playlist_gen = None
        self.stop_time = None
        self.last_query = None
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
        p_weight = 0.60
        s_weight = 1 - p_weight
        p_ratio = fuzz.partial_token_set_ratio(value, query)
        min_p_ratio = (min_score - (100 * s_weight)) / p_weight
        if p_ratio < min_p_ratio:
            self._fuzz_cache[(value, query)] = 0
            return 0
        s_ratio = fuzz.token_set_ratio(value, query)
        score = ((p_ratio * p_weight) + (s_ratio * s_weight))
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
                if isinstance(value, (dict, list)):
                    query_result = 0.0
                    for val in value:
                        tmp = self.funcs[query["func"]](val.lower().strip(), query["value"])
                        if tmp > query_result:
                            query_result = tmp
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
        total = 0
        for song in self.data:
            if total % 100 == 0:
                if time.perf_counter() >= self.stop_time:
                    yield (results, False)
            result = self._score_song(song, querys)
            if result[0]:
                results.append(Song(song, result[1], self, querys))
            total += 1
        yield (results, True)

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

    def _query_playlists(self, playlists_names):
        total_iters = 0
        for song in self.data:
            if total_iters % 100 == 0:
                if time.perf_counter() >= self.stop_time:
                    yield (playlists_names, False)
            for playlist in self.data[song].get("playlists", []):
                if playlist in playlists_names:
                    playlists_names[playlist]["songs"].append(Song(song, self._score_song(song, playlists_names[playlist]["root_song"].query)[1], self, playlists_names[playlist]["root_song"].query))
            total_iters += 1
        yield (playlists_names, True)

    def get_playlsits(self, songs: List[Song]):
        if self.query_playlist_gen is None:
            playlists_names = {}
            for root_song in songs:
                if len(root_song.get("playlists")) == 0:
                    playlists_names[root_song.get("title")] = {"songs": [], "root_song": root_song}
                    playlists_names[root_song.get("title")]["songs"] = [root_song]
                for playlist in root_song.get("playlists"):
                    playlists_names[playlist] = {"songs": [], "root_song": root_song}
            self.query_playlist_gen = self._query_playlists(playlists_names)
        playlists_names, done = next(self.query_playlist_gen)
        if done:
            self.query_playlist_gen = None
        results = []
        for playlist in playlists_names:
            if len(playlists_names[playlist]["songs"]) > 0:
                results.append(Playlist(playlists_names[playlist]["songs"], playlist, playlists_names[playlist]["root_song"]))
        return (results, done)


    def query(self, ast: Pair, stop_time, restart = False):
        asm = self._compile_ast(ast)
        self.stop_time = stop_time
        if self.generator is None or restart:
            self.last_query = None
            self.generator = self._query_db(asm)
        if not self.last_query is not None:
            results, done = next(self.generator)
            self.query_playlist_gen = None
            if done:
                self.last_query = results
        else:
            done = True
            results = self.last_query
        if asm[0]["key"] == "songs":
            return (Playable(results, "songs"), done)

        if asm[0]["key"] == "append":
            return (Playable(results, "append"), done)

        if asm[0]["key"] == "insert-next":
            return (Playable(results, "insert-next"), done)

        if asm[0]["key"] == "append-playlist":
            playlists, p_done = self.get_playlsits(results)
            return (Playable(playlists, "append"), done and p_done)

        if asm[0]["key"] == "all-matches":
            return (Playable([Playlist(results, "", None)], "all-matches"), done)

        if asm[0]["key"] == "shuffled-playlists":
            playlists, p_done = self.get_playlsits(results)
            for playlist in playlists:
                shuffle(playlist.songs)
            return (Playable(playlists, "shuffled-playlists"), done and p_done)

        playlists, p_done = self.get_playlsits(results)
        return (Playable(playlists, "playlists"), done and p_done)

if __name__ == "__main__":
    def print_playable(results):
        for i in results:
            if results.type == "playlist":
                print(f"{i.name:<150}{i.score}")
            else:
                print(f"{i.get('title'):<150}{i.score}")
    lexer  = Lexer()
    parser = Parser()
    query = Query("data/tmp_db.json")
    string = "add: artist: ironmouse and title: left right"
    string = "playlists: artist: ironmouse"
    tokens = lexer.lex(string)
    ast = parser.parse(tokens)
    start = time.time()
    running = True
    loops = 0
    while running:
        results, done = query.query(ast, time.perf_counter() + 0.01) 
        if done:
            running = False
        loops += 1;
    print(f"Total loops took {loops}")
    print(f"Took {time.time() - start} secounds to run")
    print(f"Total data {len(query.data)}")
    print(f"query string '{string}'")
    print_playable(results)

