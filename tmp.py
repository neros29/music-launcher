from pathlib import Path
import hashlib
files = ['/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/LEFT RIGHT.mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/Devil.mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang：Attack of the Magic Cloud/[Not] A Devil.mp3', '/home/neros/Music/Soren/Pop/Album - We Are So Back/LEFT RIGHT (feat. Noguchii).mp3', '/home/neros/Music/Soren/Play_Lists/IRONMOUSE MUSIC/(Not) A Devil - Ironmouse.mp3', '/home/neros/Music/Soren/Play_Lists/IRONMOUSE MUSIC/Devil - Ironmouse & Bubi.mp3', '/home/neros/Music/Soren/Play_Lists/IRONMOUSE MUSIC/Devil - Ironmouse & Bubi (Official Music Video).mp3', '/home/neros/Music/Soren/Play_Lists/IRONMOUSE MUSIC/Devil - Ironmouse & Bubi (MMD Dance Data Distribution).mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/LEFT RIGHT.mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/Devil.mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/[Not] A Devil.mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/[Not] A Devil.mp3', '/home/neros/Music/Soren/Pop/Album - Sayton Gang： Attack of the Magic Cloud/Devil.mp3', '/home/neros/Music/Soren/Pop/Album - We Are So Back/LEFT RIGHT (feat. Noguchii).mp3']

def hash_file(image: Path):
    if not  image.is_file():
        return None
    hash = hashlib.sha256()
    with open(image, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            hash.update(byte_block)
    return hash.hexdigest()
for file in files:
    print(file)
    print(hash_file(Path(file)))


