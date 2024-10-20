from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QScrollArea, QGroupBox, QTextEdit
)
from PyQt5.QtCore import Qt
from .bet_entry_widget import BetEntryWidget
from models import Bet, BettingStrategy, Combination
from utils import generate_combinations, allocate_stakes
import json

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rafinioo's Betting Strategy Simulator")
        self.bets_widgets = []
        self.strategy = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Betting Strategy Configuration
        config_group = QGroupBox("Betting Strategy Configuration")
        config_layout = QHBoxLayout()

        # Total Budget
        config_layout.addWidget(QLabel("Total Budget ($):"))
        self.budget_input = QLineEdit("100.00")
        config_layout.addWidget(self.budget_input)

        # Strategy Type
        config_layout.addWidget(QLabel("Strategy Type:"))
        self.strategy_type_combo = QComboBox()
        self.strategy_type_combo.addItems(["Accumulator", "Parlay", "System"])
        self.strategy_type_combo.currentTextChanged.connect(self.on_strategy_type_change)
        config_layout.addWidget(self.strategy_type_combo)

        # Number of Folds
        config_layout.addWidget(QLabel("Number of Folds (Legs per Combination):"))
        self.folds_input = QLineEdit("4")
        config_layout.addWidget(self.folds_input)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Bets Entry
        bets_group = QGroupBox("Bets")
        bets_layout = QVBoxLayout()

        # Scroll Area for Bets
        self.bets_scroll = QScrollArea()
        self.bets_scroll.setWidgetResizable(True)
        self.bets_container = QWidget()
        self.bets_vbox = QVBoxLayout()
        self.bets_container.setLayout(self.bets_vbox)
        self.bets_scroll.setWidget(self.bets_container)
        bets_layout.addWidget(self.bets_scroll)

        # Add default bets
        default_bets = [
            {"name": "Bet 1", "odds": "1.60", "confidence": "60"},
            {"name": "Bet 2", "odds": "1.70", "confidence": "55"},
            {"name": "Bet 3", "odds": "1.47", "confidence": "50"},
            {"name": "Bet 4", "odds": "1.30", "confidence": "65"},
            {"name": "Bet 5", "odds": "1.08", "confidence": "70"},
            {"name": "Bet 6", "odds": "1.13", "confidence": "60"},
        ]

        for bet in default_bets:
            self.add_bet_entry(bet["name"], bet["odds"], bet["confidence"])

        bets_group.setLayout(bets_layout)
        main_layout.addWidget(bets_group)

        # Add/Remove Bet Buttons
        buttons_layout = QHBoxLayout()
        self.add_bet_btn = QPushButton("Add Bet")
        self.add_bet_btn.clicked.connect(lambda: self.add_bet_entry())
        self.remove_bet_btn = QPushButton("Remove Bet")
        self.remove_bet_btn.clicked.connect(lambda: self.remove_bet_entry())
        buttons_layout.addWidget(self.add_bet_btn)
        buttons_layout.addWidget(self.remove_bet_btn)
        main_layout.addLayout(buttons_layout)

        # Action Buttons
        action_layout = QHBoxLayout()
        self.process_btn = QPushButton("Process Betting Strategy")
        self.process_btn.clicked.connect(self.process_strategy)
        self.save_btn = QPushButton("Save Strategy")
        self.save_btn.clicked.connect(self.save_strategy)
        self.load_btn = QPushButton("Load Strategy")
        self.load_btn.clicked.connect(self.load_strategy)
        action_layout.addWidget(self.process_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.load_btn)
        main_layout.addLayout(action_layout)

        # Results Table
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)  # Added Total Stake column
        self.results_table.setHorizontalHeaderLabels([
            "Combination", "Combined Odds", "Stake Allocation ($)", "Total Stake ($)", "Potential Payout ($)"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Explanations Section
        explanations_group = QGroupBox("Strategy Explanations")
        explanations_layout = QVBoxLayout()
        self.explanations_text = QTextEdit()
        self.explanations_text.setReadOnly(True)
        explanations_layout.addWidget(self.explanations_text)
        explanations_group.setLayout(explanations_layout)
        main_layout.addWidget(explanations_group)

        self.setLayout(main_layout)

    def add_bet_entry(self, name="Bet", odds="1.50", confidence="50"):
        bet_widget = BetEntryWidget(name=name, odds=odds, confidence=confidence)
        self.bets_vbox.addWidget(bet_widget)
        self.bets_widgets.append(bet_widget)

    def remove_bet_entry(self):
        if self.bets_widgets:
            bet_widget = self.bets_widgets.pop()
            self.bets_vbox.removeWidget(bet_widget)
            bet_widget.deleteLater()
        else:
            QMessageBox.warning(self, "Warning", "No more bets to remove.")

    def on_strategy_type_change(self, strategy_type):
        if strategy_type in ["Accumulator", "Parlay"]:
            num_bets = len(self.bets_widgets)
            self.folds_input.setText(str(num_bets))
            self.folds_input.setEnabled(False)
        elif strategy_type == "System":
            self.folds_input.setEnabled(True)

    def process_strategy(self):
        try:
            total_budget = float(self.budget_input.text().strip())
            if total_budget <= 0:
                raise ValueError("Total budget must be greater than zero.")
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid Total Budget: {e}")
            return

        strategy_type = self.strategy_type_combo.currentText()
        try:
            folds = int(self.folds_input.text().strip())
            if folds <= 0:
                raise ValueError("Number of folds must be greater than zero.")
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid Number of Folds: {e}")
            return

        bets = []
        for idx, bet_widget in enumerate(self.bets_widgets, start=1):
            bet_data = bet_widget.get_bet_data()
            try:
                name = bet_data["name"]
                odds = float(bet_data["odds"])
                confidence = float(bet_data["confidence"])
                if odds <= 1.0:
                    raise ValueError("Odds must be greater than 1.0.")
                if not (0 <= confidence <= 100):
                    raise ValueError("Confidence must be between 0 and 100.")
                bets.append(Bet(name, odds, confidence))
            except ValueError as e:
                QMessageBox.critical(self, "Input Error", f"Bet {idx} ({bet_data['name']}): {e}")
                return

        if strategy_type in ["Accumulator", "Parlay"]:
            folds = len(bets)
            self.folds_input.setText(str(folds))

        if folds > len(bets):
            QMessageBox.critical(self, "Input Error", f"Number of folds ({folds}) cannot exceed the number of bets ({len(bets)}).")
            return

        self.strategy = BettingStrategy(total_budget, strategy_type, folds)
        self.strategy.combinations = generate_combinations(bets, folds, strategy_type)
        allocate_stakes(self.strategy)

        self.display_results()

    def display_results(self):
        self.results_table.setRowCount(0)
        self.explanations_text.clear()

        if not self.strategy:
            return

        combinations = self.strategy.combinations
        total_payout = 0
        total_stake = 0
        explanations = []

        for combo in combinations:
            bet_names = ", ".join([bet.name for bet in combo.bets])
            combined_odds = round(combo.combined_odds, 2)
            index = self.strategy.combinations.index(combo)
            stake_allocation = round(self.strategy.stake_allocation[index], 2)
            total_stake += stake_allocation
            potential_payout = round(combined_odds * stake_allocation, 2)
            total_payout += potential_payout

            explanation = f"Combination: {bet_names}\n" \
                          f"Combined Odds: {combined_odds}\n" \
                          f"Stake Allocation: ${stake_allocation}\n" \
                          f"Potential Payout: ${potential_payout}\n"
            explanations.append(explanation)

            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            self.results_table.setItem(row_position, 0, QTableWidgetItem(bet_names))
            self.results_table.setItem(row_position, 1, QTableWidgetItem(f"{combined_odds:.2f}"))
            self.results_table.setItem(row_position, 2, QTableWidgetItem(f"{stake_allocation:.2f}"))
            self.results_table.setItem(row_position, 3, QTableWidgetItem(f"{total_stake:.2f}"))
            self.results_table.setItem(row_position, 4, QTableWidgetItem(f"{potential_payout:.2f}"))

        # Add total row
        row_position = self.results_table.rowCount()
        self.results_table.insertRow(row_position)
        total_item = QTableWidgetItem("Total")
        total_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(row_position, 0, total_item)
        self.results_table.setItem(row_position, 3, QTableWidgetItem(f"{total_stake:.2f}"))
        self.results_table.setItem(row_position, 4, QTableWidgetItem(f"{total_payout:.2f}"))

        for explanation in explanations:
            self.explanations_text.append(explanation)
            self.explanations_text.append("<hr>")

    def save_strategy(self):
        if not self.strategy:
            QMessageBox.warning(self, "Warning", "No strategy to save. Please process a strategy first.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Strategy", "", "JSON Files (*.json);;All Files (*)", options=options)
        if not file_path:
            return

        data = {
            "total_budget": self.strategy.total_budget,
            "strategy_type": self.strategy.strategy_type,
            "folds": self.strategy.folds,
            "combinations": [
                {"bets": [{"name": bet.name, "odds": bet.odds, "confidence": bet.confidence} for bet in combo.bets]}
                for combo in self.strategy.combinations
            ],
            "stake_allocation": self.strategy.stake_allocation
        }

        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Success", f"Strategy saved successfully to {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save strategy: {e}")

    def load_strategy(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Strategy", "", "JSON Files (*.json);;All Files (*)", options=options)
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            required_fields = ["total_budget", "strategy_type", "folds", "combinations", "stake_allocation"]
            if not all(field in data for field in required_fields):
                raise ValueError("Invalid strategy file format.")

            combinations = []
            for combo in data["combinations"]:
                bets = [Bet(bet["name"], bet["odds"], bet["confidence"]) for bet in combo["bets"]]
                combinations.append(Combination(bets))

            self.strategy = BettingStrategy(
                total_budget=data["total_budget"],
                strategy_type=data["strategy_type"],
                folds=data["folds"],
                combinations=combinations,
                stake_allocation=data["stake_allocation"]
            )

            self.budget_input.setText(str(self.strategy.total_budget))
            index = self.strategy_type_combo.findText(self.strategy.strategy_type)
            if index >= 0:
                self.strategy_type_combo.setCurrentIndex(index)
            self.folds_input.setText(str(self.strategy.folds))

            while self.bets_widgets:
                self.remove_bet_entry()

            unique_bets = {}
            for combo in self.strategy.combinations:
                for bet in combo.bets:
                    unique_bets[bet.name] = bet
            for bet in unique_bets.values():
                self.add_bet_entry(bet.name, str(bet.odds), str(bet.confidence))

            self.display_results()
            QMessageBox.information(self, "Success", f"Strategy loaded successfully from {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load strategy: {e}")
