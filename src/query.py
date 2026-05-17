from typing import List
from pathlib import Path
import json

class Playlist:
    def __init__(self, name: str) -> None:
        self.name = name
        self.songs = []


class Query:
    def __init__(self, db_path: Path) -> None:
        self.db_path: Path = db_path
        self.data = self._load_file()

    def _load_file(self):
        if not self.db_path.is_file:
            raise FileNotFoundError(f"File {self.db_path} dose not exst.")
        with open(self.db_path, "r") as f:
            data = json.load(f)
        return data

    def _get_song(self, key: str, value: str):
        songs = []
        music = self.data["music"]
        for song in music:
            for metadata in music[song]:
                if metadata == key and music[song][metadata] == value:
                    songs.append(song)
        return songs

    def _get_playlist(self, key: str, value: str):
        songs = []
        root_songs = self._get_song(key, value)
        playlists = []
        for i in root_songs:
            playlists += self.data["music"][i]["playlists"]

        for song in self.data["music"]:
            for playlist in self.data[song]["playlists"]:
                if playlist in playlists:
                    songs.append(song)
        return songs

            

    def get_songs(self, result: str, key: str, value: str) -> List:
        result_types = {
                "playlist": "playlist",
                "album": "playlist",
                "song": "song"
        }
        result_type = result_types.get(result, "song")
        if result_type == "song":
            return self._get_song(key, value)
        else:
            return []
            # return self._get_playlist(key, value)

    def get_values(self, key: str) -> List:
        values = []
        for i in self.data["music"]:
            value = self.data["music"][i].get(key)
            if value is not None and value not in values:
                values.append(value)
        return values


if __name__ == "__main__":
    from thefuzz import fuzz, process
    from playBackController import PlayBackController
    pbc = PlayBackController("/tmp/mpv")
    query = Query(Path("~/Documents/projects/music/data/db.json").expanduser())
    result = input("Input the type you want to return: ")
    key = input("Input the key search in: ")
    value = input("Input the value of the key you want to use: ")
    candidates = query.get_values(key)
    matches = process.extract(value, candidates, scorer=fuzz.WRatio, limit=5)
    songs = []
    num = 0
    for match, score in matches:
        results = query.get_songs(result, key, match)
        for song in results:
            songs.append(song)
            print(f"id: {num}{song}")
            num += 1
    index = int(input("Index of the song you want to play: "))
    print(songs[index])
    print(pbc.replace_playlist([songs[index]]))
        
