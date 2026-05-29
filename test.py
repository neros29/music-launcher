from re import escape
from sys import path
path.append("src/")
from pathlib import Path
from query import Query, Playlist, Songs, Song
from queryRunner import QueryRunner
from lexer import Lexer, basic_types
from parser import Parser
from playBackController import PlayBackController
type_keywords = {
        "artist": "artist",
        "title": "title",
        "playlists": "playlists",
        "playlist": "playlists",
        "album": "playlists",
        "albums": "playlists",
        "date": "date",
        "genre": "genre",
        "duration": "duration",
        "songs": "songs",
        "song": "songs"
        }

operator_keywords = {
        "and": "and",
        "or": "or",
        "|": "or",
        "&": "and"
        }

seperators= {
        " ": basic_types.WS,
        "\n": basic_types.WS,
        "\t": basic_types.WS,
        "\\": basic_types.ESC,
        '"': basic_types.D_QUOTES,
        "'": basic_types.S_QUOTES,
        ":": basic_types.SEP,
        "(": basic_types.L_OP,
        ")": basic_types.R_OP
        }

query = Query(Path("~/Documents/projects/music/data/db.json").expanduser())
qr = QueryRunner(query)
file = "/tmp/mpv"
try:
    pbc = PlayBackController(file)
except FileNotFoundError:
    print(f"File {file} dose not exist. Please make sure that mpv is running in ipc server mode with the correct socket path.")
    exit()
parser = Parser(type_keywords, operator_keywords)
lexer = Lexer(type_keywords, operator_keywords, seperators)

while True:
    try:
        q = input("Your query> ")
    except KeyboardInterrupt:
        break
    if q == "/exit":
        break
    tokens = lexer.lex(q) 
    ast = parser.parse(tokens)
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
    try:
        i = int(input("Index you want to hear: "))
    except KeyboardInterrupt:
        print()
        continue
    except ValueError:
        print("Not a valid index")
        continue

    if type(songs[0]) == Playlist:
        print(f"playing: {songs[i].playlist_name}")
        pbc.replace_playlist(songs[i].get_playable())
        continue
    print(f"playing: {songs[i]}")
    pbc.replace_playlist([songs[i]])
pbc.exit() 
