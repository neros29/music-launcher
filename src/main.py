import logging
from logging.handlers import RotatingFileHandler
from config import Config
from app import Main
from load import Load
from pathlib import Path
import os
import sys
logger = logging.getLogger(__name__)

def setup_logging(log_file_path = "logs/debug.log"):
    # 1. Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
        
    # 2. Create the Rotating File Handler
    # This keeps up to 5 backup files, each max 5MB
    log_file_path = Path(log_file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        str(log_file_path),
        maxBytes=5*1024*1024,
        backupCount=5
    )

    # 3. Create a Format for the file (include timestamps!)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # 4. Add the handler to the root logger
    root_logger.addHandler(file_handler)
    root_logger.info("============================== Application logging started. ==============================")

def set_logging_levels():
    lex_level = os.getenv("LOG_LEVEL_LEX", "WARNING")
    logging.getLogger("lexer").setLevel(lex_level)

    pbc_level = os.getenv("LOG_LEVEL_PBC", "WARNING")
    logging.getLogger("playBackController").setLevel(pbc_level)

    app_level = os.getenv("LOG_LEVEL_APP", "INFO")
    logging.getLogger("app").setLevel(app_level)

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
    setup_logging("logs/debug.log")
    set_logging_levels()
    run()
