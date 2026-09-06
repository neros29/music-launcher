from pytui import Surface
from string import printable
from enum import Enum, auto
from logging import getLogger

logger = getLogger(__name__)
class Event(Enum):
    ENTER = auto()
    BACKSPACE = auto()
    PRINTABLE = auto()
    DOWN = auto()
    UP = auto()
    LEFT = auto()
    RIGHT = auto()
    TAB = auto()


class Events:
    def __init__(self, event_surface: Surface) -> None:
        self.event_surface = event_surface
        self.special_keys = {
                chr(127): Event.BACKSPACE,
                chr(10): Event.ENTER,
                "Left": Event.LEFT,
                "Right": Event.RIGHT,
                "Up": Event.UP,
                "Down": Event.DOWN,
                chr(0x09): Event.TAB,
                }
        self.keys = self._register_keys()
        logger.info("Events has been initialized")

    def _register_keys(self):
        keys = list(printable)
        s_chs = []
        for s_ch in self.special_keys:
            s_chs.append(s_ch)
        self.event_surface.register_keys(s_chs + keys)
        return keys

    def get_events(self):
        events = []
        for key, value in self.special_keys.items():
            if self.event_surface.get_event(key):
                logger.debug("key, '%s' pressed.", value)
                events.append((value, None))
        for key in self.keys:
            if self.event_surface.get_event(key):
                logger.debug("key, '%s' pressed.", key)
                events.append((Event.PRINTABLE, key))
        return events
