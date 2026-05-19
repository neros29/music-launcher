from query import Query, Data, Song
from pathlib import Path
import json

def test_Query():
    data = Data([Song(i, DATA[i]) for i in DATA])
    tmp_db = Path("tmp/db.json")
    tmp_db.write_text(json.dumps({"music": DATA}))

    query = Query(tmp_db)
    assert len(query.data) == len(data.data), "Query._load_file test faild"

    playlists = query.get_playlists(Data([Song(i, DATA[i]) for i in DATA][:1]))
    assert playlists[0].playlist_name == "Club Ironmouse", f"Query.get_playlists test faild with value {playlists[0].playlist_name=}"
    assert playlists[0] == data, f"Query.get_playlists test faild with value {playlists[0].playlist_name=}"
    tmp_db.unlink()

DATA = {
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Cry for Me WA WA WA (Live Version).mp3": {
            "id": 1357,
            "playlists": {
                "Club Ironmouse": None
                },
            "title": "Cry for Me WA WA WA (Live Version)",
            "artist": "Ironmouse, shirobeats, HalaCG, Bubi",
            "date": "2026",
            "genre": "Music",
            "duration": 160.68
            },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Aishite Aishite Aishite.mp3": {
            "id": 1358,
            "playlists": {
                "Club Ironmouse": None
                },
            "title": "Aishite Aishite Aishite",
            "artist": "Ironmouse, shirobeats, ThunderScott",
            "date": "2026",
            "genre": "Music",
            "duration": 250.152
            },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Hell Again (Live Version).mp3": {
            "id": 1359,
            "playlists": {
                "Club Ironmouse": None
                },
            "title": "Hell Again (Live Version)",
            "artist": "Ironmouse, shirobeats, HalaCG",
            "date": "2026",
            "genre": "Music",
            "duration": 149.4
            },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Time to Feast (Live Version).mp3": {
            "id": 1360,
            "playlists": {
                "Club Ironmouse": None
                },
            "title": "Time to Feast (Live Version)",
            "artist": "Ironmouse, shirobeats, HalaCG",
            "date": "2026",
            "genre": "Music",
            "duration": 168.096
            },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Otonoke (\u30aa\u30c8\u30ce\u30b1) (Live Version).mp3": {
            "id": 1361,
            "playlists": {
                "Club Ironmouse": None
                },
            "title": "Otonoke (\u30aa\u30c8\u30ce\u30b1) (Live Version)",
            "artist": "Ironmouse, shirobeats, ThunderScott",
            "date": "2026",
            "genre": "Music",
            "duration": 183.744
            },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Abracadabra.mp3": {
                "id": 1362,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Abracadabra",
                "artist": "Ironmouse, shirobeats, ThunderScott",
                "date": "2026",
                "genre": "Music",
                "duration": 225.048
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Daidaidaidaidaikirai.mp3": {
                "id": 1363,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Daidaidaidaidaikirai",
                "artist": "Ironmouse, shirobeats, Michi Mochievee",
                "date": "2026",
                "genre": "Music",
                "duration": 155.688
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Gnarly.mp3": {
                "id": 1364,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Gnarly",
                "artist": "Ironmouse, shirobeats, Michi Mochievee, K9KURO",
                "date": "2026",
                "genre": "Music",
                "duration": 137.256
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/AI\u2661SCREAM!.mp3": {
                "id": 1365,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "AI\u2661SCREAM!",
                "artist": "Ironmouse, shirobeats, ThunderScott, Henya the Genius, Michi Mochievee",
                "date": "2026",
                "genre": "Music",
                "duration": 258.672
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Meow.mp3": {
                "id": 1366,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Meow",
                "artist": "Ironmouse, Sleeping Forest, HalaCG",
                "date": "2026",
                "genre": "Music",
                "duration": 160.224
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Play.mp3": {
                "id": 1367,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Play",
                "artist": "Ironmouse, shirobeats",
                "date": "2026",
                "genre": "Music",
                "duration": 158.832
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Music Box of Fate (Live Version).mp3": {
                "id": 1368,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Music Box of Fate (Live Version)",
                "artist": "Ironmouse, WUNDER RiKU, StarlightDaryl",
                "date": "2026",
                "genre": "Music",
                "duration": 286.272
                },
        "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Aren't We All The Worst (Live Version).mp3": {
                "id": 1369,
                "playlists": {
                    "Club Ironmouse": None
                    },
                "title": "Aren't We All The Worst (Live Version)",
                "artist": "Ironmouse, shirobeats, HalaCG, Bubi, Kiwwi",
                "date": "2026",
                "genre": "Music",
                "duration": 173.616
                },

    }

