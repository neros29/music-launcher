from sys import path
path.append("src/")
from typing import Dict
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

        
    def run(self, tokens: Dict):
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
                values = self.root.regex(key, self._glob_to_regex(token["re"]))
            else:
                values = self.root.fuzz(key, token["fuzz"])
            if op == "and":
                results = results.concat_and(self.root.get_songs_batch(key, values))
            else:
                results = results.concat_or(self.root.get_songs_batch(key, values))
        if tokens["results"] == "all":
            return query.Playlist(results)
        elif tokens["results"] == "songs":
            return results
        else:
            return self.root.get_playlists(results)

