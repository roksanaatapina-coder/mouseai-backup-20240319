import win32api
import time
from typing import Optional, Tuple

class Collector:
    def __init__(self) -> None:
        self.mouse_position: Optional[Tuple[int, int]] = None
        self.left_click: bool = False
        self.right_click: bool = False
        self.wheel_delta: int = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start_session(self) -> None:
        self.start_time = time.time()

    def stop_session(self) -> None:
        self.end_time = time.time()

    def get_mouse_position(self) -> Tuple[int, int]:
        return win32api.GetCursorPos()

    def set_left_click(self, left_click: bool) -> None:
        self.left_click = left_click

    def set_right_click(self, right_click: bool) -> None:
        self.right_click = right_click

    def set_wheel_delta(self, wheel_delta: int) -> None:
        self.wheel_delta = wheel_delta
