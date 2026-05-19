from sys import path
path.append("src/")
from query import Song

def test_Song():
    song = Song("/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Hell Again (Live Version).mp3", DATA["/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Hell Again (Live Version).mp3"])
    song1 = Song("/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Hell Again (Live Version).mp3", DATA["/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Hell Again (Live Version).mp3"])

    assert song == song1, "song.__eq__ test faild"
    assert song.__repr__() == "/home/neros/Music/Soren/Pop/Album - Club Ironmouse/Hell Again (Live Version).mp3", f"song.__repr__ failed with return {song.__repr__()=}"

    assert song.get_values("playlists") == ["Club Ironmouse"], f"song.get_values('playlists) failed with return {song.get_values('playlists')}"
    assert song.get_values("artist") == ["Ironmouse, shirobeats, HalaCG"], f"song.get_values('artist) failed with return {song.get_values('artist')}"

    assert song.has_property("artist", "Ironmouse, shirobeats, HalaCG"), f"song.has_property('artist', 'Ironmouse, shirobeats, HalaCG') faild with return {song.has_property('artist', 'Ironmouse, shirobeats, HalaCG')}"
    assert not song.has_property("artist", "none existent artist"), f"song.has_property('artist', 'none existent artist') faild with return {song.has_property('artist', 'none existent artist')}"

DATA = {
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
    }
