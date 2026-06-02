from pathlib import Path
from typing import List
from thefuzz import fuzz
import json

class Song:
    def __init__(self, song_path: str, matched_keys: List[str], root: 'Query') -> None:
        self.root = root
        self.path = song_path
        self.matched_keys= matched_keys

    def get(self, key: str):
        return self.root.data[self.path][key]

class Playlist:
    def __init__(self, root_song: Song, playlist_name: str, root: 'Query') -> None:
        self.root = root
        self.root_song = root_song
        self.name = playlist_name
        self.songs = self._get_song()
        self.artist = self._get_artist()

    def _get_song(self):
        return self.root.query_db([{"func": "eq", "key": "playlists", "value": self.name, "op": None}])

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

class Query:
    def __init__(self, db_path) -> None:
        self.db_path: Path = db_path if isinstance(db_path, Path) else Path(db_path)
        self.data = self._load_file()
        self.funcs = {
                "fuzz": self._fuzz,
                "glob": self._glob,
                "eq": self._eq,
                }
        self.op_funcs = {
                "and": self._and,
                "or": self._or,
                None: self._or,
                }

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
        return v1 == v2 

    def _fuzz(self, real_value: str, value: str):
        min_score = 75
        score = fuzz.partial_token_sort_ratio(real_value, value)
        return score > min_score

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
                return False
        while pattern_idx < p_len and pattern[pattern_idx] == '*':
            pattern_idx += 1
        return pattern_idx == p_len

    def query_db(self, querys: List[dict]):
        results = []
        for song in self.data:
            result = False
            op = None
            key_matches = []
            for query in querys:
                if not result and op == "and":
                    break
                if isinstance(query, str):
                    op = query

                elif query["func"] in self.funcs:
                    value = self.data[song][query["key"]]
                    if isinstance(value, dict):
                        query_result = False
                        for val in value:
                            query_result =  self.funcs[query["func"]](val.lower().strip(), query["value"].lower().strip()) or query_result
                    else:
                        query_result = self.funcs[query["func"]](value.lower().strip(), query["value"].lower().strip())
                    if query_result:
                        key_matches.append(query["key"])
                    result = self.op_funcs[query["op"]](result, query_result)
                else:
                    print("function not found")
            if result:
                results.append(Song(song, key_matches, self))
        return results

if __name__ == "__main__":
    query = Query("data/db.json")
    query_data = [{"func": "glob", "key": "title", "value": "*right", "op": None}, {"func": "glob", "key": "title", "value": "king*", "op": "or"}, {"func": "fuzz", "key": "artist", "value": "ironmouse", "op": "and"} ]
    results: List[Song] = query.query_db(query_data)
    for song in results:
        for playlist in song.get('playlists'):
            import time
            start = time.time()
            p = Playlist(song, playlist, query)
            print(time.time() - start)
            print(f"{p.name}, {p.artist}, {len(p.songs)}")
        print(f"{song.get('title')}: {song.matched_keys}")
