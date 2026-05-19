from pathlib import Path
from typing import Dict
import query
import re

class Parser:
    def __init__(self, db_path: Path) -> None:
        self.query = query.Query(db_path)
        self._min_score = 75
        self._limit = None

    def _glob_to_regex(self, glob_pattern):
        regex_pattern = re.escape(glob_pattern)
        regex_pattern = regex_pattern.replace(r'\*', '.*')
        regex_pattern = regex_pattern.replace(r'\?', '.')
        regex_pattern = f"^{regex_pattern}$"
        return regex_pattern

        
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
                values = self.query.regex(key, self._glob_to_regex(token["re"]))
            else:
                values = self.query.fuzz(key, token["fuzz"])
            if op == "and":
                results = results.concat_and(self.query.get_songs_batch(key, values))
            else:
                results = results.concat_or(self.query.get_songs_batch(key, values))
        return results

