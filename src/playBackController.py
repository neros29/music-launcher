from pathlib import Path
import subprocess
import hashlib
import socket
import json
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SendCmd:
    def __init__(self, ipc_file: str, mpv_cmd) -> None:
        self.ipc_file = ipc_file
        self._mpv_cmd = mpv_cmd
        self._start_client()
        self.events = []
        self.id = 0

    def _init_socket(self):
        logger.debug("Starting client connection")
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(self.ipc_file)
        client.settimeout(5.0)
        return client

    def _start_client(self):
        wait_time = 0.5
        retrys = 2
        try:
            self.client = self._init_socket()
            logger.debug("Successfully connected to socket.")
        except (FileNotFoundError, ConnectionRefusedError) as e:
            logger.warning("Failed to connect to socket (%s). Trying to start mpv.", e)
            self._start_mpv()
            for i in range(retrys):
                if not Path(self.ipc_file).exists():
                    time.sleep(wait_time)
                    if i >= retrys:
                        raise FileNotFoundError("Ipc file was never created. Are you sure your ipc file in your mpv command matches the socket_file in your config")
                    continue
                try:
                    self.client = self._init_socket()
                    logger.info("After starting mpv connected to socket after %s/%s trys.", i, retrys)
                    return
                except (FileNotFoundError, ConnectionRefusedError):
                    logger.debug("Failed to connect to socket after starting mpv %s/%s times. Will try again in %s seconds.", i, retrys, wait_time)
                    time.sleep(wait_time)
                    continue
            raise ConnectionError("Failed to start client. Possible causes, mpv not running, incorrect ipc file.")
        except Exception:
            logger.exception("Socket connection failed during initialization")
            raise

    def _start_mpv(self):
        use_shell = isinstance(self._mpv_cmd, str)
        subprocess.Popen(
            self._mpv_cmd,
            shell=use_shell,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True
        )

    def recv(self, cmd_id):
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
                        response = (data, data.get("error"))
                        logger.debug("request id %s response received with error value '%s'", cmd_id, response[1])
                        return response
                    else:
                        self.events.append(data)
                        continue
                except json.JSONDecodeError as e:
                    bad_line = line[:100] + "..." if len(line) > 100 else line
                    logger.error("Error Decoding response (%s) on response id %s : Data: '%s'", e, cmd_id, bad_line)
                    continue

    def send(self, cmd_dict: dict):
        cmd_id = self.id
        self.id += 1
        cmd_dict["request_id"] = cmd_id
        cmd = json.dumps(cmd_dict)
        cmd += "\n"
        retrys = 2
        wait_time = 0.5
        try:
            logger.debug("Sending cmd '%s' to mpv", cmd.replace("\n", ""))
            self.client.send(cmd.encode())
            logger.debug("Successfully sent cmd")
        except BrokenPipeError as e:
            logger.warning("Failed to send cmd to mpv (%s) Trying to restart client", e)
            self._start_client()
            for i in range(retrys):
                try:
                    self.client.send(cmd.encode())
                    logger.info("Successfully sent cmd after restarting client")
                    break
                except BrokenPipeError:
                    if i >= retrys - 1:
                        logger.warning("Failed to send cmd after restarting client %s/%s times. Will try again in %s seconds.", i, retrys, wait_time)
                        raise 
                    logger.warning("Failed to send cmd after restarting client %s/%s times. Will try again in %s seconds.", i, retrys, wait_time)
                    time.sleep(wait_time)
                    continue
        return self.recv(cmd_id)

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
            logger.debug("Generating m3u file for playlist at %s", file)
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
            logging.warning("Unable to play song as file %s not found.", to_play)
            responses.append(f"File {to_play} not found")
        return responses

    def exit(self):
            self._cmd_runner.exit()
