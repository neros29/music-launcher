from pathlib import Path
from copy import deepcopy
import json
import os
from typing import Optional


class Config:
    def __init__(self, app_name: str = "music-launcher") -> None:
        self.app_name = app_name
        self.file_name = "config.json"
        self.config = {
                "music_paths": [
                    "~/Music/"
                    ],
                "theme": {
                    "background": "#121316",
                    "foreground": "#e3e2e6",
                    "surface_bg": "#40495b",
                    "syntax": {
                        "TYPE": "#d28c89",
                        "STRING_VALUE": "#3e87a3",
                        "VALUE": "#e2b370",
                        "OP": "#81a8e6",
                        "SCOPE": "#81a8e6",
                        "AUTO_COMPLETE": "#9188a8"
                        }
                    },
                "socket_file": "/tmp/mpv",
                "player_cmd": "mpv --input-ipc-server={socket_file} --idle=yes --player-operation-mode=pseudo-gui"
                }
        self.config_path = self._get_config_path()
        self.default_config = False
        self._load_config()
        

    def _get_config_path(self) -> Path:
        base = os.getenv("XDG_CONFIG_HOME")
        path = Path(base) / self.app_name if base else Path.home() / ".config" / self.app_name
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if not (path / self.file_name).exists():
            self._generate_default_config(path / self.file_name)
        return path

    def _load_config(self):
        if self.default_config:
            return
        with open(str(self.config_path / self.file_name), "r") as f:
            try:
                data = json.load(f)
                user_conf = deepcopy(self.config)
                for k, v in data.items():
                    if k in user_conf and isinstance(user_conf[k], type(v)):
                        user_conf[k] = v
                    elif k == "theme":
                        if isinstance(v, str):
                            user_conf[k] = v
            except json.JSONDecodeError:
                return
            self._parse_config(user_conf)

    def _parse_config(self, user_conf):
        self._parse_theme(user_conf["theme"])
        user_conf["music_paths"] = [file for file in user_conf["music_paths"] if Path(file).expanduser().is_dir()]
        if len(user_conf["music_paths"]) > 0:
            self.config["music_paths"] = user_conf["music_paths"]
        self.config["music_paths"] = [str(Path(file).expanduser()) for file in self.config["music_paths"]]

        if Path(user_conf["socket_file"]).parent.is_dir():
            self.config["socket_file"] = user_conf["socket_file"]

        if len(user_conf["player_cmd"]) > 0:
            self.config["player_cmd"] = user_conf["player_cmd"]

    def _hex_to_rgb(self, hex_str: str) -> Optional[list[int]]:
            """Safely converts #RRGGBB or #RGB to [R, G, B]."""
            try:
                hex_str = hex_str.lstrip('#')
                if len(hex_str) == 3:
                    hex_str = ''.join([c*2 for c in hex_str])
                return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]
            except (ValueError, IndexError):
                return None

    def _parse_theme(self, theme):
        data = theme
        if isinstance(theme, str):
            theme_file = Path(theme).expanduser()
            if theme_file.is_file() and theme_file.suffix == ".json":
                with open(theme_file, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        return
        for k, v in self.config["theme"].items():
            if isinstance(data[k], type(v)):
                if isinstance(v, dict):
                    for s_k, s_v in v.items():
                        color = False
                        if data.get(k) and data.get(s_k):
                            color = self._hex_to_rgb(data[k][s_k])
                        self.config["theme"][k][s_k] =  color if color else self._hex_to_rgb(s_v)
                else:
                    color = False
                    if data.get(k):
                        color = self._hex_to_rgb(data[k])
                    self.config["theme"][k] =  color if color else self._hex_to_rgb(self.config["theme"][k])

    def _generate_default_config(self, path):
        with open(str(path), "w") as f:
            json.dump(self.config, f, indent=4)
        self.default_config = True

    def db_path(self):
        base = os.getenv("XDG_STATE_HOME")
        path = Path(base) / self.app_name if base else Path.home() / ".local" / "state" / self.app_name
        path.mkdir(parents=True, exist_ok=True)
        return str(path / "db.json")

if __name__ == "__main__":
    config = Config()
    print(config.config)
