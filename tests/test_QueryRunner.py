from sys import path
path.append("src/")

from typing import List
from queryRunner import QueryRunner
from pathlib import Path
import json

from query import Data, Playlist, Query
def test_QueryRunner():
    tmp_db = Path("tmp/db.json")
    tmp_db.write_text(json.dumps({"music": DATA}))
    query = Query(Path("tmp/db.json").expanduser())
    parser = QueryRunner(query)

    values = parser.run({r"results": r"songs", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}]})
    assert isinstance(values, Data), "Parser.run test faild do to values not being of type Data"
    assert "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Aren't We All The Worst (Live Version).mp3" == values.data[0].name, "Parser.prase test failed"

    values = parser.run({r"results": r"songs", r"query": [{r"key": r"title", r"re": r"reand"}]})
    assert isinstance(values, Data), "Parser.run test faild do to values not being of type Data"
    assert len(values.data) == 0, "Parser.prase test failed"
    
    values = parser.run({r"results": r"playlists", r"query": [{r"key": r"playlists", r"re": r"Club Ironmouse"}]})
    assert isinstance(values, List), "Parser.run test faild do to values not being of type Playlist"
    assert len(values[0].data) == 13, f"Parser.run test faild with results {len(values[0].data)}"

    values = parser.run({r"results": r"all", r"query": [{r"key": r"duration", r"re": r"250.152"}, r"or", {r"key": r"duration", r"re": r"160.68"}]})
    assert isinstance(values, Playlist), "Parser.run test faild do to values not being of type Playlist"
    assert len(values.data) == 2, f"Parser.run test faild with results {len(values.data)}"

    assert parser._glob_to_regex("*iron*") == "^.*iron.*$", f"Parser._glob_to_regex test failed returning {parser._glob_to_regex('*iron*')}"
    assert parser._glob_to_regex("*iron?ouse.*") == r"^.*iron.ouse\..*$", f"Parser._glob_to_regex test failed returning {parser._glob_to_regex('*iron?ous.*')}"


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
