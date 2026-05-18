from typing import Dict, List, Optional
from pathlib import Path
import json


class Song:
    def __init__(self, name: str = "", data: Optional[Dict]= None) -> None:
        self.data: Dict = data if data is not None else {}
        self.name: str = name;
        self._iterable_types = (dict, list)

    def has_property(self, key: str, value: str):
        return value in self.get_values(key)

    def get_values(self, key: str):
        values = []
        value = self.data.get(key)
        if isinstance(value, self._iterable_types):
            for value in self.data.get(key, [None]):
                if value is not None:
                    values.append(value)
        else:
            values.append(value)
        return values

class Data:
    def __init__(self, data = None) -> None:
        self.data: List[Song] = data if data is not None else []

    def get_songs(self, key: str, value: str):
        results = []
        for song in self.data:
            if song.has_property(key, value):
                results.append(song)
        return Data(results)

    def get_playable(self):
        return [i.name for i in self.data]

    def get_values(self, key: str) -> List:
        values = []
        for song in self.data:
            values += song.get_values(key)
        return values
    
    def concat_and(self, other: 'Data'):
        matches = []
        for value in self.data:
            if value in other.data:
                matches.append(value)
        return Data(matches)

    def concat_or(self, other: 'Data'):
        new = self.data + other.data
        return Data(new)

    def __iter__(self):
        for i in self.data:
            yield i


class Music(Data):
    def __init__(self, db_path: Path) -> None:
        self.db_path: Path = db_path
        music = self._load_file()
        super().__init__([Song(i, music[i]) for i in music])

    def _load_file(self):
        if not self.db_path.is_file():
            raise FileNotFoundError(f"File {self.db_path} dose not exst.")
        with open(self.db_path, "r") as f:
            data = json.load(f)
        return data["music"]

if __name__ == "__main__":
    from thefuzz import fuzz, process
    from playBackController import PlayBackController
    pbc = PlayBackController("/tmp/mpv")
    root = Music(Path("~/Documents/projects/music/data/db.json").expanduser())
    matches = process.extract("gnarly", root.get_values("title"), scorer=fuzz.WRatio, limit=None)
    matches2 = process.extract("ironmouse", root.get_values("artist"), scorer=fuzz.WRatio, limit=None)
    songs = Data()
    for match, score in matches:
        if score > 75:
            songs = songs.concat_or(root.get_songs("title", match))

    songs2 = Data()
    for match, score in matches2:
        if score > 75:
            songs2 = songs2.concat_or(root.get_songs("artist", match))

    for song in songs.concat_and(songs2):
        print(f"Song {song.get_values('title')} playlists: ", end="")
        print(song.get_values("playlists"))
    pbc.replace_playlist(songs.concat_and(songs2).get_playable())

