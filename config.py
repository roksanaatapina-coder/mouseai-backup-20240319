class Config:
    def __init__(self):
        self.game_detection_methods = ['process_name', 'active_window_title']
        self.data_collection_methods = [
            'timestamp',
            'mouse_dx_dy',
            'left_right_click_events',
            'wheel_events',
            'session_start_end',
            'selected_game_genre'
        ]
