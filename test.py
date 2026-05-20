from sys import path
path.append("src/")
from pathlib import Path
from query import Query, Playlist, Data, Song
from queryRunner import QueryRunner
from parser import Parser
from playBackController import PlayBackController


query = Query(Path("~/Documents/projects/music/data/db.json").expanduser())
qr = QueryRunner(query)
pbc = PlayBackController("/tmp/mpv")
parser = Parser()

while True:
    q = input("Your query> ")
    if q == "/exit":
        break
    ast = parser.parse(q)
    if ast == None:
        print("Invalid search query")
        continue
    results = qr.run(ast)
    if type(results) == Playlist:
        print(f"playing custom playlist from query")
        pbc.replace_playlist(results.get_playable())
        continue
    index = 0
    songs = []
    for result in results:
        if type(result) == Playlist:
            print(f"{index}: {result.playlist_name}")
            songs.append(result)
            index += 1
        elif type(result) == Song:
            print(f"{index}: {result}")
            songs.append(result.name)
            index += 1
    i = int(input("Index you want to hear: "))
    if type(songs[0]) == Playlist:
        print(f"playing: {songs[i].playlist_name}")
        pbc.replace_playlist(songs[i].get_playable())
        continue
    print(f"playing: {songs[i]}")
    pbc.replace_playlist([songs[i]])
pbc.exit() 
