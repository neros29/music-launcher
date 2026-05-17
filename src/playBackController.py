from pathlib import Path
import hashlib
import socket
import json
from typing import Dict, List

class SendCmd:
    def __init__(self, ipc_file: str) -> None:
        self.client = self._init_socket(ipc_file)
        self.events = []
        self.id = 0

    def _init_socket(self, ipc_file):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(ipc_file)
        return client

    def send(self, cmd_dict: Dict):
        cmd_id = self.id
        self.id += 1
        cmd_dict["request_id"] = cmd_id
        cmd = json.dumps(cmd_dict)
        cmd += "\n"
        self.client.send(cmd.encode())
        while True:
            response = b''
            while True:
                chunk = self.client.recv(1024)
                if not chunk:
                    break
                response += chunk
                if b'\n' in chunk:
                    break
            for line in response.decode().split("\n"):
                if line.strip() == "":
                    continue
                try:
                    data = json.loads(line)
                    if data.get("request_id") == cmd_id:
                        return data
                    else:
                        self.events.append(data)
                        continue
                except json.JSONDecodeError:
                    print("[SendCmd] Error Decoding value: " + line)
                    continue

class PlayBackController:
    def __init__(self, ipc_file: str) -> None:
        self._cmd_runner = SendCmd(ipc_file)

    def _hash_playlist(self, songs: List[str]):
        hash = hashlib.sha256()
        for song in songs:
            hash.update(song.encode())
        return hash.hexdigest()

    def _write_m3u(self, songs: List[str]) -> str:
        path = Path("~/.cache/music-control/").expanduser()
        path.mkdir(exist_ok=True)
        file = path / f"{self._hash_playlist(songs)}.m3u"
        if not file.is_file():
            with open(file, "w") as f:
                for song in songs:
                    f.write(song + "\n")
        if file.is_file():
            print("Cache hit")
        return str(file)

    def _replace_large(self, songs: List[str]):
        path = self._write_m3u(songs)
        cmd = {
                "command": ["loadfile", path, "replace"]
        }
        self._send(json.dumps(cmd))
        return self._recv()
        

    def _replace(self, songs: List[str]):
        responses = []
        first = True
        for song in songs: 
            if first:
                cmd = {
                        "command": ["loadfile", song, "replace"]
                }
                first = False
            else:
                cmd = {
                        "command": ["loadfile", song, "append"]
                }
            self._send(json.dumps(cmd))
            responses.append(self._recv())
        return responses


    def replace_playlist(self, songs: List[str]):
        large: int = 6
        if len(songs) > large:
            return self._replace_large(songs)
        else:
            return self._replace(songs)
             

if __name__ == "__main__":
    pbc = PlayBackController("/tmp/mpv")
    songs = [str(i) for i in Path("/home/neros/Music/Soren/Pop/Album - Mouse Birthday Concert").iterdir()]
    print("sending songs")
    print(pbc.replace_playlist(songs))


