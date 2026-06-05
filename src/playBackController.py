from pathlib import Path
import subprocess
import hashlib
import socket
import json
import time
from typing import Dict, List

class SendCmd:
    def __init__(self, ipc_file: str, mpv_cmd) -> None:
        self.ipc_file = ipc_file
        self._mpv_cmd = mpv_cmd
        self._start_client()
        self.events = []
        self.id = 0

    def _init_socket(self):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(self.ipc_file)
        client.settimeout(5.0)
        return client

    def _start_client(self):
        try:
            self.client = self._init_socket()
        except (FileNotFoundError, ConnectionRefusedError):
            self._start_mpv()
            for _ in range(10):
                try:
                    self.client = self._init_socket()
                    return
                except (FileNotFoundError, ConnectionRefusedError):
                    time.sleep(0.5)
                    continue
            raise ConnectionError("Failed to start client")

    def _start_mpv(self):
        use_shell = isinstance(self._mpv_cmd, str)
        subprocess.Popen(
            self._mpv_cmd,
            shell=use_shell,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True
        )

    def send(self, cmd_dict: Dict):
        cmd_id = self.id
        self.id += 1
        cmd_dict["request_id"] = cmd_id
        cmd = json.dumps(cmd_dict)
        cmd += "\n"
        try:
            self.client.send(cmd.encode())
        except BrokenPipeError:
            self._start_client()
            for i in range(10):
                try:
                    self.client.send(cmd.encode())
                    break
                except BrokenPipeError:
                    if i >= 9:
                        raise BrokenPipeError("Reached max retries")
                    time.sleep(0.5)
                    continue
        while True:
            response = b''
            while True:
                self.client.settimeout(2.0)
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

    def exit(self):
        self.client.close()

class PlayBackController:
    def __init__(self, ipc_file: str, mpv_cmd: str) -> None:
        self._cmd_runner = SendCmd(ipc_file, mpv_cmd)

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
                    if Path(song).is_file():
                        f.write(song + "\n")
        return str(file)

    def _replace_large(self, songs: List[str]):
        path = self._write_m3u(songs)
        cmd = {
                "command": ["loadfile", path, "replace"]
        }
        response = self._cmd_runner.send(cmd)
        return [response]
        

    def _replace(self, songs: List[str]):
        responses = []
        first = True
        for song in songs: 
            if Path(song).is_file():
                if first:
                    cmd = {
                            "command": ["loadfile", song, "replace"]
                    }
                    first = False
                else:
                    cmd = {
                            "command": ["loadfile", song, "append"]
                    }
                response = self._cmd_runner.send(cmd)
                responses.append(response)
        return responses

    def _append(self, songs: List[str]):
        responses = []
        for song in songs: 
            if Path(song).is_file():
                cmd = {
                        "command": ["loadfile", song, "append"]
                }
                response = self._cmd_runner.send(cmd)
                responses.append(response)
        return responses

    def exit(self):
        self._cmd_runner.exit()

    def replace_playlist(self, songs: List[str]):
        if not isinstance(songs, list):
            raise ValueError("Songs must be a list")
        large: int = 30
        if len(songs) > large:
            return self._replace_large(songs)
        else:
            return self._replace(songs)

    def add_to_playlists(self, songs: List[str]):
        if not isinstance(songs, list):
            raise ValueError("Songs must be a list")
        return self._append(songs)

