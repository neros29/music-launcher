import os
import json
from mutagen._file import File as MutagenFile

class Load:
    def __init__(self, path):
        self.musicPath = path
        self.musicExtentions = (".mp3", ".m4a")
        self.dbPath = "/home/neros/Documents/projects/music/data/db.json"
        self.data = {}
        self.loadFile()

    def extract_metadata(self, filepath):
        """Extract metadata from an audio file using mutagen."""
        metadata = self.data["music"][filepath]
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
                    metadata['artist'] = audio['artist'][0]
                else:
                    metadata['artist']  = None
                if 'album' in audio:
                    if audio['album'][0] is not None and audio["album"][0] != 'NA':
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

    def loadData(self):
        music = self.data["music"]
        for directory in os.walk(self.musicPath):
            for file in directory[2]:
                path = os.path.join(directory[0], file)   # Safer path construction
                if file.lower().endswith(self.musicExtentions):
                    if music.get(path) is None:
                        music[path] = {
                                "playlists": {
                                },
                        }
                        self.extract_metadata(path)
        self.saveData()

    def loadFile(self):
        if not os.path.isfile(self.dbPath):
            with open(self.dbPath, "w") as f:
                json.dump({"music": {}}, f)
        with open(self.dbPath, "r") as f:
            self.data = json.load(f)
            if self.data.get("music") is None:
                self.data["music"] = {}

    def saveData(self):
        with open(self.dbPath, "w") as f:
            json.dump(self.data, f, indent=4)

if __name__ == "__main__":
    load = Load("/home/neros/Music/Soren/")
    load.loadData()

