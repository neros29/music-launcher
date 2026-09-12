from pytui import Surface
from playBackController import PlayBackController
from typing import Optional
from logging import getLogger
from threading import Thread, Lock

logger = getLogger(__name__)

class PlayBackControllerException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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
        self.pbc: tuple[Optional[PlayBackController], str] = (None, "")
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
                self.pbc = (PlayBackController(self.socket_file, self.playback_cmd), "success")
            except Exception as e:
                self.pbc = (None, str(e))

    def _handle_enter(self):
        if self.selected is not None:
            self.play(self.selected)
            return True
        else:
            logger.info("Tried to hit enter when nothing was selected")

    def play(self, songs):
        defualt_setup_comands = [
                ["set_property", "loop-file", "no"]
                ]
        loop_cmd = [["set_property", "loop-file", "inf"]]
        logger.info("Playing songs %s", songs)
        with self.pbc_lock:
            if self.pbc[1] != "success" or self.pbc[0] is None: 
                logger.error("Playback controller object failed to launch, with Error (%s)", self.pbc[1])
                raise PlayBackControllerException(f"Playback controller object failed to launch, with Error ({self.pbc[1]})")
            pbc = self.pbc[0]
            if self.play_type == "append":
                self.append = False
                responses = pbc.play_song(songs, "append", defualt_setup_comands)
                for response in responses:
                    if response[1] != 'success':
                        logger.warning("Append command failed with response '%s' ", response[0])
            elif self.play_type == "insert-next":
                self.next_song = False
                responses = pbc.play_song(songs, "insert-next", defualt_setup_comands)
                for response in responses:
                    if response[1] != 'success':
                        logger.warning("Insert-next command failed with response '%s' ", response[0])
            elif self.play_type == "loop":
                responses = pbc.play_song(songs, "replace", defualt_setup_comands + loop_cmd)
                for response in responses:
                    if response[1] != 'success':
                        logger.warning("Loop command failed with response '%s' ", response[0])
            else:
                responses = pbc.play_song(songs, "replace", defualt_setup_comands)
                for response in responses:
                    if response[1] != 'success':
                        logger.warning("Replace command failed with response '%s' ", response[0])


    def events(self):
        for key in self.special_keys:
            if self.surface.get_event(key):
                logger.debug("Received special key '%s' calling Editor.'%s'", key, self.special_keys[key].__name__)
                return self.special_keys[key]()

    def update(self, selected):
        self.selected = selected
        return self.events()
