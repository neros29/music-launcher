from query import Data, Song, Playlist

def test_Playlists():
    data = Data([Song(i, OUTHER_DATA[i]) for i in OUTHER_DATA])
    playlist = Playlist(data, "Appetite For Destruction")
    assert playlist.score == 0.6, f"Playlists._get_artist faild with return {playlist.score=}"
    assert playlist.artist == "Guns N' Roses", f"Playlists._get_artist faild with return {playlist.artist=}"
    assert playlist.get_playable()[:2] == ["/home/neros/Music/Soren/Play_Lists/programing/Sweet Child O' Mine.mp3", '/home/neros/Music/Soren/Play_Lists/programing/Welcome To The Jungle.mp3'], "Playlist._sort failed."


OUTHER_DATA = {
        "/home/neros/Music/Soren/Play_Lists/programing/Sweet Child O' Mine.mp3": {
            "playlists": {
                "Appetite For Destruction": 5
            },
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "date": "2018",
            "genre": None,
            "duration": 356.112
        },
        "/home/neros/Music/Soren/Play_Lists/programing/Anouther song.mp3": {
            "playlists": {
                "Appetite For Destruction": None
            },
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "date": "2018",
            "genre": None,
            "duration": 356.112
        },
        "/home/neros/Music/Soren/Play_Lists/programing/Welcome To The Jungle.mp3": {
            "playlists": {
                "Appetite For Destruction": 6
            },
            "title": "Welcome To The Jungle",
            "artist": "Guns N' Roses",
            "date": "2018",
            "genre": None,
            "duration": 273.504
        },
        "/home/neros/Music/Soren/Play_Lists/programing/What Do You Do for Money Honey.mp3": {
            "playlists": {
                "Back In Black": None
            },
            "title": "What Do You Do for Money Honey",
            "artist": "AC/DC",
            "date": "2018",
            "genre": None,
            "duration": 215.568
        },
        "/home/neros/Music/Soren/Play_Lists/programing/Without Me.mp3": {
            "playlists": {
                "The Eminem Show": None
            },
            "title": "Without Me",
            "artist": "Eminem",
            "date": "2018",
            "genre": None,
            "duration": 290.352
        },
    }
