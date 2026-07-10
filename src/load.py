import os
import json
from typing import Dict, Optional
from mutagen._file import File as MutagenFile
from queue import Queue
from threading import Thread
import re

class Load:
    def __init__(self, path, dbPath):
        self.musicPath = path
        self.musicExtentions = (".mp3", ".m4a")
        self.dbPath = dbPath
        self.data = {}
        self._load_file()
        self.work_queue = Queue() 
        self.return_queue = Queue()
        self.paths = set()
        self.deleted = self.data["cache"]["duplicates"]
        self.thread_count = 8
        for _ in range(self.thread_count):
            t = Thread(target=self.worker, daemon=True)
            t.start()

    def _load_file(self):
        if not os.path.isfile(self.dbPath):
            with open(self.dbPath, "w") as f:
                json.dump({"music": {}}, f)
        with open(self.dbPath, "r") as f:
            self.data = json.load(f)
            if self.data.get("music") is None:
                self.data["music"] = {}
            if self.data.get("cache") is None:
                self.data["cache"] = {}
                self.data["cache"]["duplicates"] = {}

    def _save_data(self):
        with open(self.dbPath, "w") as f:
            json.dump(self.data, f, indent=4)

    def _extract_metadata(self, filepath):
        """Extract metadata from an audio file using mutagen."""
        metadata: Dict[str, Optional[dict]] = {
                "playlists": {},
            }
        try:
            # Use easy mode for consistent tag access across formats
            audio = MutagenFile(filepath, easy=True)
            if audio is not None:
                # Populate metadata from available tags
                if 'title' in audio:
                    metadata['title'] = audio['title'][0]
                else:
                    metadata['title']  = None
                if 'artist' in audio:
                    metadata['artist'] = [i.strip() for i in audio['artist'][0].split(",")]
                else:
                    metadata['artist']  = None
                if 'album' in audio:
                    if audio['album'][0] is not None and audio["album"][0] != 'NA':
                        assert metadata["playlists"] is not None
                        metadata["playlists"][audio['album'][0]] = None
                if 'date' in audio:
                    metadata['date'] = audio['date'][0]
                else:
                    metadata['date']  = None
                if 'genre' in audio:
                    metadata['genre'] = audio['genre'][0]
                else:
                    metadata['genre']  = None
                # Duration is stored in the audio info object
                if audio.info and hasattr(audio.info, 'length'):
                    metadata['duration'] = audio.info.length
            else:
                print(f"Warning: Could not read metadata from {filepath}")
        except Exception as e:
            print(f"Error reading metadata from {filepath}: {e}")
        return metadata

    def worker(self):
        while True:
            path = self.work_queue.get()
            data = self._extract_metadata(path)
            self.return_queue.put((path, data))

    def get_music(self):
        procesed = 0
        receved = 0
        music = self.data["music"]
        for directory in os.walk(self.musicPath):
            for file in directory[2]:
                path = os.path.join(directory[0], file)
                if file.lower().endswith(self.musicExtentions):
                    self.paths.add(path)
                    if music.get(path) is None and path not in self.deleted:
                        procesed += 1
                        self.work_queue.put(path)
        while procesed > receved:
            path, data = self.return_queue.get()
            music[path] = data
            receved += 1
        print(f"proccesed {procesed} music files")

    def parse_m3u(self, data, path):
        results = []
        name = None
        lines = data.split("\n")
        for line in lines:
            if line.strip().startswith("#"):
                match = re.match(r"^#\s*NAME\s*:(.*)$", line)
                if match:
                    name = match.group(1).strip()
            elif len(line.strip()) > 0:
                results.append(os.path.abspath(os.path.join("/".join(path.split("/")[:-1]), line)))
        if name is None:
            match = re.match(r"^Album\s-\s(.*).m3u$", path.split("/")[-1])
            if match:
                name = match.group(1).strip()
            else:
                name = path.split("/")[-1].strip()
        return (results, name)

    def get_m3u(self):
        procesed = 0
        music = self.data["music"]
        cache = self.data["cache"]
        if not cache.get("m3u"):
            cache["m3u"] = {}
        for directory in os.walk(self.musicPath):
            for file in directory[2]:
                path = os.path.join(directory[0], file)
                if file.lower().endswith((".m3u")):
                    if path in cache["m3u"]:
                        continue
                    with open(path, "r") as f:
                        data = f.read()
                        playlist, name = self.parse_m3u(data, path)
                        procesed += 1
                        for index, song in enumerate(playlist):
                            orig_path = cache["duplicates"].get(song)
                            if music.get(song):
                                music[song]["playlists"][name] = index
                                cache["m3u"][path] = True
                            elif orig_path:
                                self.data[orig_path]["playlists"][name] = index
                                cache["m3u"][path] = True
                            else:
                                print(f"faild to find {song} form in {path}")
        print(f"proccesed {procesed} m3u files")

    def _clean_db(self):
        songs = {}
        dups = []
        for song in self.data["music"]:
            if not song in self.paths:
                print(f"song {song}")
                dups.append(song)
                continue
            song_data = self.data["music"][song]
            song_hash = f"{song_data['title']},{song_data['artist']},{song_data['date']}" 
            if song_hash not in songs:
                songs[song_hash] = song
            else:
                dups.append(song)
        for song in dups:
            song_data = self.data["music"][song]
            song_hash = f"{song_data['title']},{song_data['artist']},{song_data['date']}" 
            # if song_hash in songs:
            orig = songs[song_hash]
            orig_data = self.data["music"][orig]["playlists"]
            for playlist in song_data["playlists"]:
                if playlist not in orig_data or orig_data[playlist] == None:
                    orig_data[playlist] = song_data["playlists"][playlist]
            self.data["cache"]["duplicates"][song] = orig
            del self.data["music"][song]
        print(f"deleted {len(dups)}")
    
    def fill_db(self):
        self.get_music()
        self.get_m3u()
        self._clean_db()
        self._save_data()

if __name__ == "__main__":
    load = Load("/home/neros/Music/", "/home/neros/Documents/projects/music/data/db.json")
    load.fill_db()
