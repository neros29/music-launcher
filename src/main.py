import logging
from logging.handlers import RotatingFileHandler
from config import Config
import logging.config
from app import Main
from load import Load
import json
from pathlib import Path
import os
import sys
logger = logging.getLogger(__name__)

def setup_logging(conf_paths: list[str]):
    # 1. Create a root logger
    conf_path = None
    for path in conf_paths:
        conf_path = Path(path)
        if conf_path.is_file():
            conf_path = conf_path.absolute()
            with open(str(conf_path), "r") as f:
                data = json.load(f)
            logging.config.dictConfig(data)
            break

    logger.info("============================== Application logging started. ==============================")
    logger.info("Using logging file %s", str(conf_path))

def run():
    config = Config("music-launcher")
    args = sys.argv
    if len(args) > 1 and args[1] == "load":
        logger.info("Starting data base loading")
        print(f"Loading music into db...")
        load = Load(config.config["music_paths"], config.db_path())
        load.fill_db()
    elif len(args) > 1 and args[1] == "test":
        config.config["socket_file"] = "/tmp/mpv-test"
        config.config["player_cmd"] = "hyprctl dispatch \"hl.dsp.exec_cmd('mpv --input-ipc-server=\"/tmp/mpv-test\" --idle=yes --player-operation-mode=pseudo-gui', { workspace = '9 silent' })\""
        print("\x1b[?1h")
        logger.info("Starting app in debug mode")
        main = Main(config)
        main.run()
        print("\x1b[?25h")
    else:
        logger.info("Starting app in production mode")
        print("\x1b[?1h")
        main = Main(config)
        main.run()
        print("\x1b[?25h")
    logger.info("App closed")

if __name__ == "__main__":
    setup_logging([
        "logs/config.json",
        "conf/config.json"
        ])
    run()
