from typing import Dict, List, Optional
from thefuzz import fuzz, process
from pathlib import Path
import json
import re

class Song:
    def __init__(self, name: str = "", data: Optional[Dict]= None) -> None:
        self.data: Dict = data if data is not None else {}
        self.name: str = name;
        self._iterable_types = (dict, list)

    def has_property(self, key: str, value: str):
        return value in str(self.get_values(key))

    def get_values(self, key: str):
        values = []
        value = self.data.get(key)
        if isinstance(value, self._iterable_types):
            for value in self.data.get(key, [None]):
                if value is not None:
                    values.append(str(value))
        else:
            values.append(str(value))
        return values

    def __repr__(self):
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Song):
            return NotImplemented 
        return self.name == other.name

class Data:
    def __init__(self, data = None) -> None:
        self.data: List[Song] = data if data is not None else []
        self._min_score = 75
        self._limit = None

    def regex(self, key: str, pattern: str):
        values = self.get_values(key)
        results = []
        for value in values:
            try:
                if re.search(pattern.lower(), value.lower()):
                    results.append(value)
            except Exception as e:
                print(f"Error \"{e}\" with {value=}, and {pattern=}")
        return results

    def fuzz(self, key: str, pattern: str):
        values = self.get_values(key)
        matches = process.extract(pattern, values, scorer=fuzz.WRatio, limit=self._limit)
        results = []
        for match, score in matches:
            if score > self._min_score:
                results.append(match)
        return results
    
    def get_songs(self, key: str, value: str):
        results = []
        for song in self.data:
            if song.has_property(key, value):
                results.append(song)
        return Data(results)

    def get_songs_batch(self, key: str, values: List):
        results = []
        for value in values:
            results += self.get_songs(key, value).data
        return Data(results)

    def get_playable(self):
        return [i.name for i in self.data]

    def get_values(self, key: str, all_values=False) -> List:
        values = []
        for song in self.data:
            if all_values:
                values += song.get_values(key)
                continue
            value = song.get_values(key)
            for v in value:
                if v not in values:
                    values.append(v)
        return values
    
    def concat_and(self, other: 'Data'):
        matches = []
        for value in self.data:
            if value in other.data:
                matches.append(value)
        return Data(matches)

    def concat_or(self, other: 'Data'):
        results = []
        for i in self.data + other.data:
            if i not in results:
                results.append(i)
        return Data(results)

    def __iter__(self):
        for i in self.data:
            yield i

    def __repr__(self):
        return self.get_playable().__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Data):
            return NotImplemented # Better than False for __eq__
        return self.data == other.data

class Playlist(Data):
    def __init__(self, playlist: Data, playlist_name: str = "") -> None:
        super().__init__(playlist.data)
        self.playlist_name: str = playlist_name
        self.score = 0
        self.artist: str = self._get_artist()
        self._sort()

    def _sort(self):
        if self.playlist_name != "":
            self.data.sort(key = lambda x: x.data["playlists"].get(self.playlist_name) or float("inf"))

    def _get_artist(self):
        artists = self.get_values("artist", all_values=True)
        count = {
        }
        for artist in artists:
            if artist is not None:
                split_artist = []
                for i in artist.split(","):
                    formated_artist = i.strip()
                    if formated_artist not in split_artist:
                        split_artist.append(formated_artist)
                        if formated_artist in count:
                            count[formated_artist] += 1
                        else:
                            count[formated_artist] = 1
        most = 0
        most_artist = ""
        for artist in count:
            if count[artist] > most:
                most_artist = artist
                most = count[artist]
        self.score = most / len(self.data)
        return most_artist


class Query(Data):
    def __init__(self, db_path: Path) -> None:
        self.db_path: Path = db_path
        super().__init__(self._load_file())

    def _load_file(self):
        if not self.db_path.is_file():
            raise FileNotFoundError(f"File {self.db_path} dose not exst.")
        with open(self.db_path, "r") as f:
            data = json.load(f)
        songs = []
        for song in data["music"]:
            songs.append(Song(song, data["music"][song]))
        return songs

    def get_playlists(self, root_songs: Data):
        results = []
        playlist_names = []
        for song in root_songs:
            playlists = song.get_values("playlists")
            for playlist in playlists:  
                if playlist not in playlist_names:
                    playlist_names.append(playlist)
        for playlist in playlist_names:
            result = Playlist(self.get_songs("playlists", playlist), playlist)
            results.append(result)
        return results


