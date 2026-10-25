from typing import Optional, Generator, Any, Callable
import time

class Worker:
    def __init__(self, func: Optional[Callable[..., Generator[None, None, Any]]] = None) -> None:
        self.to_use: Callable[..., Generator[None, None, Any]] = func if func else self.work
        self.worker: Optional[Generator] = None

    def work(self, *args, **kwargs) -> Generator[None, None, Any]:
        raise NotImplementedError("You must implement work, when inheriting from Worker")

    def do_work(self, work_time: float, restart = False, *args, **kwargs):
        if work_time < 0:
            raise ValueError("Work time must not negative")
        start = time.perf_counter()
        if self.worker is None or restart:
            self.worker = self.to_use(*args, **kwargs)
        while True:
            if work_time > time.perf_counter() - start:
                try:
                    next(self.worker)
                except StopIteration as e:
                    return e.value
            else:
                return None

