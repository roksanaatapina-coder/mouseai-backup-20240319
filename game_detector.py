import win32gui
import time

class GameDetector:
    def __init__(self, config):
        self.config = config
        self.active_window_title = None

    def detect_active_game(self):
        while True:
            self.active_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if any(method in self.config.game_detection_methods for method in ['process_name', 'active_window_title']):
                break
            time.sleep(0.1)
