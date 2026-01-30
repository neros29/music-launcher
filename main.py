import os
import json

class Load:
    def __init__(self, path):
        self.musicPath = path
        self.musicExtentions = (".mp3", ".m4a", ".mp4")
        self.dbPath = "/home/neros/Documents/projects/music/data/db.json"
        self.data = {}


    def loadData(self):
        music = {}
        for directory in os.walk(self.musicPath):
            for file in directory[2]:
                if file.endswith(self.musicExtentions):
                    music[file[:-4]] = directory[0] + "/" + file
        self.data["music"] = music
    def saveData(self):
        with open(self.dbPath, "w") as f:
            json.dump(self.data, f, indent=4)


if __name__ == "__main__":
    load = Load("/home/neros/Music/")
    load.loadData()
    load.saveData()


                    
