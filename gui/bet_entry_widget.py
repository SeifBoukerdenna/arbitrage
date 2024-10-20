# gui/bet_entry_widget.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator

class BetEntryWidget(QWidget):
    """Widget for entering individual bet details."""

    def __init__(self, parent=None, name: str = "Bet 1", odds: str = "1.50", confidence: str = "50"):
        super().__init__(parent)
        self.init_ui(name, odds, confidence)

    def init_ui(self, name: str, odds: str, confidence: str):
        """Initialize the UI components."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)

        # Name Input
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Bet Name")
        self.name_input.setFixedWidth(150)
        self.name_input.setToolTip("Enter the name of the bet.")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        # Odds Input
        self.odds_input = QLineEdit(odds)
        self.odds_input.setPlaceholderText("Odds (e.g., 1.50)")
        self.odds_input.setFixedWidth(120)
        self.odds_input.setValidator(QDoubleValidator(1.01, 1000.00, 2))
        self.odds_input.setToolTip("Enter the odds for the bet (greater than 1.00).")
        layout.addWidget(QLabel("Odds:"))
        layout.addWidget(self.odds_input)

        # Confidence Input
        self.confidence_input = QLineEdit(confidence)
        self.confidence_input.setPlaceholderText("Confidence (%)")
        self.confidence_input.setFixedWidth(120)
        self.confidence_input.setValidator(QIntValidator(0, 100))
        self.confidence_input.setToolTip("Enter your confidence percentage in the bet.")
        layout.addWidget(QLabel("Confidence (%):"))
        layout.addWidget(self.confidence_input)

        self.setLayout(layout)

    def get_bet_data(self) -> dict:
        """
        Retrieve the entered bet data.

        :return: Dictionary containing bet name, odds, and confidence.
        """
        return {
            "name": self.name_input.text().strip(),
            "odds": self.odds_input.text().strip(),
            "confidence": self.confidence_input.text().strip()
        }

    def set_bet_data(self, name: str, odds: float, confidence: float):
        """
        Set the bet data programmatically.

        :param name: Bet name.
        :param odds: Bet odds.
        :param confidence: Bet confidence percentage.
        """
        self.name_input.setText(name)
        self.odds_input.setText(f"{odds:.2f}")
        self.confidence_input.setText(f"{confidence:.1f}")
