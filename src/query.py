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

class Songs:
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
        return Songs(results)

    def get_songs_batch(self, key: str, values: List):
        results = []
        for value in values:
            results += self.get_songs(key, value).data
        return Songs(results)

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
    
    def _concat_and(self, other: 'Songs'):
        matches = []
        for value in self.data:
            if value in other.data and value not in matches:
                matches.append(value)
        return Songs(matches)

    def concat_and(self, other):
        if isinstance(other, Songs):
            return self._concat_and(other)
        elif isinstance(other, Playlists):
            results = []
            for songs in other:
                results.append(self._concat_and(songs))
            return results
        else:
            raise NotImplemented

    def concat_or(self, other):
        if isinstance(other, Songs):
            return self._concat_or(other)
        elif isinstance(other, Playlists):
            results = []
            for songs in other:
                results.append(self._concat_or(songs))
            return results
        else:
            raise NotImplemented

    def _concat_or(self, other: 'Songs'):
        results = []
        for i in self.data + other.data:
            if i not in results:
                results.append(i)
        return Songs(results)

    def __iter__(self):
        for i in self.data:
            yield i

    def __repr__(self):
        return self.get_playable().__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Songs):
            return NotImplemented # Better than False for __eq__
        return self.data == other.data

    def __add__(self, other: 'Songs'):
        self.data = self.data + other.data
        results = []
        for song in self.data:
            if song not in results:
                self.data.append(song)
        return Songs(results)

class Playlist(Songs):
    def __init__(self, playlist, playlist_name: str = "") -> None:

        if isinstance(playlist, Playlists):
            new: Optional[Songs] = None
            for i in playlist:
                if new is None:
                    new = i
                else:
                    new = new + i
            assert new is not None, "this should not happend" 
            super().__init__(new.data)
        else:
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

class Playlists:
    def __init__(self, data: List[Playlist]) -> None:
        self.data = data

    def _concat_and(self, other: 'Songs'):
        results = []
        for songs in self.data:
            matches = []
            for song in songs:
                if song not in matches and song in other.data:
                    matches.append(song)
            results.append(matches)
        return Playlists(results)

    def concat_and(self, other):
        if isinstance(other, Songs):
            return self._concat_and(other)
        elif isinstance(other, Playlists):
            results = []
            for songs in other:
                results.append(self._concat_and(songs))
            return results
        else:
            raise NotImplemented

    def concat_or(self, other):
        if isinstance(other, Songs):
            return self._concat_or(other)
        elif isinstance(other, Playlists):
            results = []
            for songs in other:
                results.append(self._concat_or(songs))
            return results
        else:
            raise NotImplemented

    def _concat_or(self, other: 'Songs'):
        results = []
        for songs in self.data:
            matches = songs + other
            results.append(matches)
        return Playlists(results)

    def __iter__(self):
        for i in self.data:
            yield i
    def __getitem__(self, index: int):
        return self.data[index]

class Query(Songs):
    def __init__(self, db_path) -> None:
        self.db_path: Path = db_path if isinstance(db_path, Path) else Path(db_path)
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

    def get_playlists(self, root_songs) -> Playlists:
        if isinstance(root_songs, Playlists):
            return root_songs
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
        return Playlists(results)

