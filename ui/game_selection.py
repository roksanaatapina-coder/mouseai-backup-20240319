import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class GameSelection(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Selection")
        self.setGeometry(100, 100, 400, 300)

        self.status_label = QLabel(self)
        self.status_label.setText("Idle")

        self.tactical_fps_button = QPushButton("Tactical FPS", self)
        self.tactical_fps_button.clicked.connect(lambda: self.select_game('tactical_fps'))

        self.hero_arena_fps_button = QPushButton("Hero / Arena FPS", self)
        self.hero_arena_fps_button.clicked.connect(lambda: self.select_game('hero_arena_fps'))

        self.battle_royale_button = QPushButton("Battle Royale", self)
        self.battle_royale_button.clicked.connect(lambda: self.select_game('battle_royale'))

        self.universal_button = QPushButton("Universal", self)
        self.universal_button.clicked.connect(lambda: self.select_game('universal'))

        self.cs2_button = QPushButton("CS2", self)
        self.cs2_button.clicked.connect(lambda: self.select_game('cs2'))

        self.valorant_button = QPushButton("Valorant", self)
        self.valorant_button.clicked.connect(lambda: self.select_game('valorant'))

        self.apex_legends_button = QPushButton("Apex Legends", self)
        self.apex_legends_button.clicked.connect(lambda: self.select_game('apex_legends'))

        self.overwatch_2_button = QPushButton("Overwatch 2", self)
        self.overwatch_2_button.clicked.connect(lambda: self.select_game('overwatch_2'))

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.tactical_fps_button)
        layout.addWidget(self.hero_arena_fps_button)
        layout.addWidget(self.battle_royale_button)
        layout.addWidget(self.universal_button)
        layout.addWidget(self.cs2_button)
        layout.addWidget(self.valorant_button)
        layout.addWidget(self.apex_legends_button)
        layout.addWidget(self.overwatch_2_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def select_game(self, game):
        # Placeholder logic for selecting game
        print(f"Selected: {game}")
