from pathlib import Path
import subprocess
import hashlib
import socket
import json
import time
from typing import Optional

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
            stderr=open("logs/mpv.err", "a"),
            stdout=open("logs/mpv.out", "a"),
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True
        )

    def send(self, cmd_dict: dict):
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
    def __init__(self, ipc_file: str, mpv_cmd: str, cache_dir: str = f"~/.cache/music-launcher") -> None:
        self.cache_dir = cache_dir
        self._cmd_runner = SendCmd(ipc_file, mpv_cmd)

    def _hash_playlist(self, songs: list[str]):
        hash = hashlib.sha256()
        for song in songs:
            hash.update(song.encode())
        return hash.hexdigest()

    def _get_playlist(self, songs: list[str]) -> str:
        path = Path(self.cache_dir).expanduser()
        path.mkdir(exist_ok=True)
        file = path / f"{self._hash_playlist(songs)}.m3u"
        if not file.is_file():
            with open(file, "w") as f:
                for song in songs:
                    if Path(song).is_file():
                        f.write(song + "\n")
        return str(file)

    def play_song(self, songs: list[str], command: str, setup_commands: Optional[list[list]]=None) -> list:
        if setup_commands is None:
            setup_commands = []
        responses = []
        to_play = None
        if len(songs) > 1:
            to_play = self._get_playlist(songs)
        elif len(songs) == 1:
            to_play = songs[0]

        if to_play is not None and Path(to_play).is_file():
            cmds = []
            for c in setup_commands:
                cmds.append({"command": c})
            cmds.append({"command": ["loadfile", to_play, command]})
            for cmd in cmds:
                responses.append(self._cmd_runner.send(cmd))
        else:
            responses.append(f"File {to_play} not found")
        return responses

    def exit(self):
            self._cmd_runner.exit()
