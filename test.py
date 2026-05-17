import json
import time
from thefuzz import fuzz, process

start = time.time()
with open("data/db.json", "r") as f:
    DATA = json.load(f)["music"]
print(f"time to load: {time.time() - start}")

def query(key: str):
    artists = []
    start = time.time()
    for i in DATA:
        artist = DATA[i]["metadata"].get(key)
        if artist is not None and artist not in artists:
            artists.append(artist)
    print(f"time to find: {time.time() - start}, amount found: {len(artists)} of {len(DATA)}")
    return artists

def fuzzy_find(candidates, query, limit=10):
    start = time.time()
    matches = process.extract(query, candidates, scorer=fuzz.WRatio, limit=limit)
    print(f"fuzzing took: {time.time()-start}")
    print(f"\nResults for '{query}':\n")
    return matches

def get_songs(key: str, value: str):
    songs = []
    for song in DATA:
        for metadata in DATA[song]["metadata"]:
            if metadata == key and DATA[song]["metadata"][metadata] == value:
                songs.append(DATA[song])
    return songs

def print_results(matches, key):
    for match, score in matches:
        songs = get_songs(key, match)
        print(f"score: {score}{' ' * (50 - len(str(score))) }match: {match}{' ' * (50 - len(match)) }len of songs:{len(songs)}")
        
if __name__ == "__main__":
    key = input("A key to search through: ")
    value = input("The value to find: ")
    result = query(key) 
    matches = fuzzy_find(result, value, 20)
    print_results(matches, key)

