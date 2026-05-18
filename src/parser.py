from pathlib import Path
from thefuzz import fuzz, process
from typing import Dict, List
import query
import time
import re

class Parser:
    def __init__(self, db_path: Path) -> None:
        self.root = query.Music(db_path)
        self._min_score = 75
        self._limit = None

    def _regex(self, key: str, pattern: str):
        pattern = self._glob_to_regex(pattern)
        values = self.root.get_values(key)
        results = []
        for value in values:
            if re.search(pattern.lower(), value.lower()):
                results.append(value)
        return results

    def _glob_to_regex(self, glob_pattern):
        regex_pattern = re.escape(glob_pattern)
        regex_pattern = regex_pattern.replace(r'\*', '.*')
        regex_pattern = regex_pattern.replace(r'\?', '.')
        regex_pattern = f"^{regex_pattern}$"
        return regex_pattern

    def _fuzz(self, key: str, pattern: str):
        values = self.root.get_values(key)
        matches = process.extract(pattern, values, scorer=fuzz.WRatio, limit=self._limit)
        results = []
        for match, score in matches:
            if score > self._min_score:
                results.append(match)
        return results
        
    def _get_songs(self, key: str, values: List):
        results = query.Data()
        for value in values:
            tmp = self.root.get_songs(key, value)
            results = results.concat_or(tmp)
        return results
    
    def parse(self, tokens: Dict):
        results = query.Data();
        op = None
        for num, token in enumerate(tokens.get("query", []), start=0):
            isop = 0 != num % 2
            if isop:
                op = token
                continue
            key = token["key"]
            values = []

            if "re" in token:
                values = self._regex(key, token["re"])
            else:
                values = self._fuzz(key, token["fuzz"])
            if op == "and":
                results = results.concat_and(self._get_songs(key, values))
            else:
                results = results.concat_or(self._get_songs(key, values))
        return (tokens["results"], results)

if __name__ == "__main__":

    parser = Parser(Path("~/Documents/projects/music/data/db.json").expanduser())
    start = time.time()
    values = parser.parse({r"results": r"playlists", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"left right"}]})
    # playlists: artist: "*iron*" title: left right
    print(time.time() - start)
    print(*(i.name for i in values[1]), sep="\n")

