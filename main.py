import os
import json
from mutagen._file import File as MutagenFile

class Load:
    def __init__(self, path):
        self.musicPath = path
        self.musicExtentions = (".mp3", ".m4a", ".mp4")
        self.dbPath = "/home/neros/Documents/projects/music/data/db.json"
        self.data = {}

    def extract_metadata(self, filepath):
        """Extract metadata from an audio file using mutagen."""
        metadata = {
            "title": None,
            "artist": None,
            "album": None,
            "tracknumber": None,
            "discnumber": None,
            "date": None,
            "genre": None,
            "duration": None
        }
        try:
            # Use easy mode for consistent tag access across formats
            audio = MutagenFile(filepath, easy=True)
            if audio is not None:
                # Populate metadata from available tags
                if 'title' in audio:
                    metadata['title'] = audio['title'][0]
                if 'artist' in audio:
                    metadata['artist'] = audio['artist'][0]
                if 'album' in audio:
                    metadata['album'] = audio['album'][0]
                if 'tracknumber' in audio:
                    metadata['tracknumber'] = audio['tracknumber'][0]
                if 'discnumber' in audio:
                    metadata['discnumber'] = audio['discnumber'][0]
                if 'date' in audio:
                    metadata['date'] = audio['date'][0]
                if 'genre' in audio:
                    metadata['genre'] = audio['genre'][0]
                # Duration is stored in the audio info object
                if audio.info and hasattr(audio.info, 'length'):
                    metadata['duration'] = audio.info.length
            else:
                print(f"Warning: Could not read metadata from {filepath}")
        except Exception as e:
            print(f"Error reading metadata from {filepath}: {e}")
        return metadata

    def loadData(self):
        music = {}
        for directory in os.walk(self.musicPath):
            for file in directory[2]:
                path = os.path.join(directory[0], file)   # Safer path construction
                if file.lower().endswith(self.musicExtentions):
                    metadata = self.extract_metadata(path)
                    music[path] = {
                        "name": os.path.splitext(file)[0],   # Removes extension cleanly
                        "playList": directory[0],
                        "metadata": metadata
                    }
        self.data["music"] = music
        self.saveData()

    def saveData(self):
        with open(self.dbPath, "w") as f:
            json.dump(self.data, f, indent=4)

if __name__ == "__main__":
    load = Load("/home/neros/Music/")
    load.loadData()
