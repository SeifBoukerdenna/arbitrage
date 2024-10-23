from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton


class ActionButtonsWidget(QWidget):
    """Widget containing action buttons."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        action_layout = QHBoxLayout(self)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(20)

        self.process_btn = QPushButton("Process Betting Strategy")
        self.process_btn.setToolTip("Process the betting strategy based on entered bets.")

        self.save_btn = QPushButton("Save Strategy")
        self.save_btn.setToolTip("Save the current betting strategy to a file.")

        self.load_btn = QPushButton("Load Strategy")
        self.load_btn.setToolTip("Load a previously saved betting strategy from a file.")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setToolTip("Reset the application to its initial state.")

        action_layout.addWidget(self.process_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.load_btn)
        action_layout.addWidget(self.reset_btn)

        self.setLayout(action_layout)
        self.setFixedHeight(70)
