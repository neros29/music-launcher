from pytui import Surface
from playBackController import PlayBackController
from typing import Optional
from logging import getLogger
from threading import Thread, Lock

logger = getLogger(__name__)

class Player:
    def __init__(self, root_surf: Surface, socket_file, playback_cmd) -> None:
        self.surface = root_surf
        self.socket_file = socket_file
        self.playback_cmd = playback_cmd

        self.special_keys = {
                chr(10): self._handle_enter
            }
        self._register_keys()
        self.selected = None
        self.pbc_lock = Lock()
        self.pbc: tuple[Optional[PlayBackController], Optional[Exception]] = (None, None)
        self.t = Thread(target=self._start_pbc, daemon=True)
        self.t.start()
        self.play_type = "song"

    def _register_keys(self):
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.surface.register_keys(s_chs)

    def _start_pbc(self):
        with self.pbc_lock:
            try:
                self.pbc = (PlayBackController(self.socket_file, self.playback_cmd), None)
            except Exception as e:
                self.pbc = (None, e)

    def _handle_enter(self):
        if self.selected is not None:
            self.play(self.selected)
            return True
        else:
            logger.info("Tried to hit enter when nothing was selected")
            return False

    def play(self, songs):
        defualt_setup_comands = [
                ["set_property", "loop-file", "no"]
                ]
        loop_cmd = [["set_property", "loop-file", "inf"]]
        commands = {
                "append": ("append", defualt_setup_comands),
                "insert-next": ("insert-next", defualt_setup_comands),
                "loop": ("replace", defualt_setup_comands + loop_cmd),
                "defualt": ("replace", defualt_setup_comands),
                }
        logger.info("Playing songs %s", songs)
        with self.pbc_lock:
            if self.pbc[1] is not None: 
                logger.error("Playback controller object failed to launch, with Error (%s)", self.pbc[1])
                raise self.pbc[1]
            assert self.pbc[0] is not None, "This should not be None"
            pbc = self.pbc[0]
            if commands.get(self.play_type):
                command = commands[self.play_type]
            else:
                command = commands["defualt"]
            cmd_results = pbc.play_song(songs, command[0], command[1])
            for cmd in cmd_results:
                if cmd[1] != "success":
                    logger.warning("Mpv command failed with '%s'", cmd[0])
                


    def events(self):
        for key in self.special_keys:
            if self.surface.get_event(key):
                logger.debug("Received special key calling Editor.'%s'", key, self.special_keys[key].__name__)
                return self.special_keys[key]()

    def update(self, selected):
        self.selected = selected
        return self.events()

    def exit(self):
        if self.pbc[1] is None and self.pbc[0] is not None:
            self.pbc[0].exit()
