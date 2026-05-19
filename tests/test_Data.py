from query import Data, Song

def test_Data():
    data = Data([Song(i, DATA[i]) for i in DATA])

    values = data.fuzz("title", "arent we all teh worst")
    assert values[0] == "Aren't We All The Worst (Live Version)", "data.fuzz test failed"
    
    values = data.regex("title", "^.*We All The.*$")
    assert values == ["Aren't We All The Worst (Live Version)"], "data.regex test failed"

    values = data.get_songs("duration", "250.152")
    assert values.data[0].name == "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Aishite Aishite Aishite.mp3", f"data.get_songs test failed returning {values.data[0].name=}"

    values = data.get_songs("playlists", "Club Ironmouse")
    assert len(values.data) == 13, f"data.get_songs test failed returning {values.data[0].name=}"

    values = data.get_values("playlists")
    assert values == ["Club Ironmouse"], f"data.get_values test failed returning {values=}"

    other_data = Data([Song(i, DATA) for i in DATA][0:5])
    values = data.concat_and(other_data)
    assert values.data == data.data[0:5], f"data.concat_and test failed returning {values.data=}"

    values = data.concat_or(other_data)
    assert values.data == data.data, f"data.concat_or test failed returning {values.data=}"

    other_data = Data([Song(i, DATA) for i in DATA][5:])
    data1 = Data([Song(i, DATA) for i in DATA][:5])
    values = data1.concat_and(other_data)
    assert len(values.data) == 0, f"data.concat_and test failed returning {values.data=}"

    values = data1.concat_or(other_data)
    assert values.data == data.data, f"data.concat_or test failed returning {values.data=}"

    values = data1.concat_or(other_data)
    assert values.data == data.data, f"data.concat_or test failed returning {values.data=}"

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

