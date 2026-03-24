import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self, mode):
        super().__init__()
        self.setWindowTitle("Aim/Mouse Behavior Analysis")
        self.setGeometry(100, 100, 400, 300)

        self.status_label = QLabel(self)
        self.status_label.setText("Idle")

        self.start_button = QPushButton("Start Session", self)
        self.start_button.clicked.connect(self.start_session)

        self.stop_button = QPushButton("Stop Session", self)
        self.stop_button.clicked.connect(self.stop_session)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_session(self):
        self.status_label.setText("Recording")
        # Placeholder logic for starting session

    def stop_session(self):
        self.status_label.setText("Analyzing")
        # Placeholder logic for stopping session
