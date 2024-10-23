from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QLabel, QGroupBox, QVBoxLayout,
    QScrollArea, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtCore import Qt
from .bet_entry_widget import BetEntryWidget
from data.bets_data import default_bets
from models.bet import Bet

class BetsEntryWidget(QGroupBox):
    """Widget for entering bets."""

    def __init__(self):
        super().__init__("Bets")
        self.bets_widgets = []
        self.init_ui()

    def init_ui(self):
        bets_layout = QVBoxLayout()
        bets_layout.setContentsMargins(10, 10, 10, 10)
        bets_layout.setSpacing(10)

        # Scroll Area for Bets
        self.bets_scroll = QScrollArea()
        self.bets_scroll.setWidgetResizable(True)
        self.bets_container = QWidget()
        self.bets_vbox = QVBoxLayout()
        self.bets_vbox.setAlignment(Qt.AlignTop)
        self.bets_container.setLayout(self.bets_vbox)
        self.bets_scroll.setWidget(self.bets_container)
        bets_layout.addWidget(self.bets_scroll)

        # Add default bets
        for bet in default_bets:
            self.add_bet_entry(bet["name"], bet["odds"], bet["confidence"])

        # Add/Remove Bet Buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(10, 0, 10, 0)
        buttons_layout.setSpacing(20)

        self.add_bet_btn = QPushButton("Add Bet")
        self.add_bet_btn.clicked.connect(lambda: self.add_bet_entry())
        self.add_bet_btn.setToolTip("Add a new bet entry.")
        self.remove_bet_btn = QPushButton("Remove Bet")
        self.remove_bet_btn.clicked.connect(self.remove_bet_entry)
        self.remove_bet_btn.setToolTip("Remove the last bet entry.")

        buttons_layout.addWidget(self.add_bet_btn)
        buttons_layout.addWidget(self.remove_bet_btn)
        buttons_widget.setLayout(buttons_layout)
        buttons_widget.setFixedHeight(60)

        bets_layout.addWidget(buttons_widget)
        self.setLayout(bets_layout)

    def add_bet_entry(self, name: str = "Bet", odds: str = "1.50", confidence: str = "50"):
        """Add a new bet entry widget."""
        bet_widget = BetEntryWidget(name=name, odds=odds, confidence=confidence)
        self.bets_vbox.addWidget(bet_widget)
        self.bets_widgets.append(bet_widget)

    def remove_bet_entry(self):
        """Remove the last bet entry widget."""
        if self.bets_widgets:
            bet_widget = self.bets_widgets.pop()
            self.bets_vbox.removeWidget(bet_widget)
            bet_widget.deleteLater()
        else:
            QMessageBox.warning(self, "Warning", "No more bets to remove.")

    def get_bets(self):
        bets = []
        for idx, bet_widget in enumerate(self.bets_widgets, start=1):
            bet_data = bet_widget.get_bet_data()
            try:
                name = bet_data["name"]
                odds = float(bet_data["odds"])
                confidence = float(bet_data["confidence"])
                if not name:
                    raise ValueError("Bet name cannot be empty.")
                if odds <= 1.0:
                    raise ValueError("Odds must be greater than 1.0.")
                if not (0 <= confidence <= 100):
                    raise ValueError("Confidence must be between 0 and 100.")
                bets.append(Bet(name, odds, confidence))
            except ValueError as e:
                QMessageBox.critical(self, "Input Error", f"Bet {idx} ({bet_data.get('name', 'Unnamed')}): {e}")
                raise
        return bets

    def set_bets(self, bets):
        # Clear existing bets
        while self.bets_widgets:
            self.remove_bet_entry()

        # Add bets to the UI
        for bet in bets:
            self.add_bet_entry(bet.name, f"{bet.odds:.2f}", f"{bet.confidence:.1f}")

    def reset(self):
        # Clear bets
        while self.bets_widgets:
            self.remove_bet_entry()

        # Add default bets
        for bet in default_bets:
            self.add_bet_entry(bet["name"], bet["odds"], bet["confidence"])
