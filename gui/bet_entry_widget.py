# gui/bet_entry_widget.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt5.QtCore import Qt

class BetEntryWidget(QWidget):
    def __init__(self, parent=None, name="Bet 1", odds="1.50", confidence="50"):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Bet Name")
        self.odds_input = QLineEdit(odds)
        self.odds_input.setPlaceholderText("Odds (e.g., 1.50)")
        self.confidence_input = QLineEdit(confidence)
        self.confidence_input.setPlaceholderText("Confidence (%)")

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Odds:"))
        layout.addWidget(self.odds_input)
        layout.addWidget(QLabel("Confidence (%):"))
        layout.addWidget(self.confidence_input)

        self.setLayout(layout)

    def get_bet_data(self):
        return {
            "name": self.name_input.text().strip(),
            "odds": self.odds_input.text().strip(),
            "confidence": self.confidence_input.text().strip()
        }

    def set_bet_data(self, name, odds, confidence):
        self.name_input.setText(name)
        self.odds_input.setText(str(odds))
        self.confidence_input.setText(str(confidence))
