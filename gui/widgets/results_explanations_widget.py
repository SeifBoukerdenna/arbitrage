import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QSplitter, QGroupBox, QVBoxLayout, QTableWidget, QLabel, QTextEdit,
    QMessageBox, QFileDialog, QTableWidgetItem, QHeaderView  # Corrected import
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont  # QFont remains in QtGui
from models.bet import Bet
from models.combination import Combination
from models.betting_strategy import BettingStrategy


class ResultsExplanationsWidget(QSplitter):
    """Widget for displaying results and explanations."""

    def __init__(self):
        super().__init__(Qt.Vertical)
        self.init_ui()

    def init_ui(self):
        self.setHandleWidth(1)

        # Results Table Group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(10, 10, 10, 10)
        results_layout.setSpacing(10)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Combination", "Combined Odds", "Stake Allocation ($)", "Potential Payout ($)", "EV per $"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        self.addWidget(results_group)

        # Totals Display Group
        totals_group = QGroupBox("Totals")
        totals_layout = QVBoxLayout()
        totals_layout.setContentsMargins(10, 10, 10, 10)
        totals_layout.setSpacing(10)

        self.total_stake_label = QLabel("Total Stake Allocation ($): 0.00")
        self.total_payout_label = QLabel("Total Potential Payout ($): 0.00")

        totals_font = QFont()
        totals_font.setPointSize(12)
        totals_font.setBold(True)
        self.total_stake_label.setFont(totals_font)
        self.total_payout_label.setFont(totals_font)

        totals_layout.addWidget(self.total_stake_label)
        totals_layout.addWidget(self.total_payout_label)
        totals_group.setLayout(totals_layout)
        self.addWidget(totals_group)

        # Explanations Section Group
        explanations_group = QGroupBox("Strategy Explanations")
        explanations_layout = QVBoxLayout()
        explanations_layout.setContentsMargins(10, 10, 10, 10)
        explanations_layout.setSpacing(10)

        self.explanations_text = QTextEdit()
        self.explanations_text.setReadOnly(True)
        explanations_layout.addWidget(self.explanations_text)
        explanations_group.setLayout(explanations_layout)
        self.addWidget(explanations_group)

    def display_results(self, strategy):
        """Display the results and explanations based on the processed strategy."""
        self.results_table.setRowCount(0)
        self.explanations_text.clear()

        if not strategy:
            return

        combinations = strategy.combinations
        total_payout = 0.0
        total_stake = 0.0
        explanations = []

        for index, combo in enumerate(combinations):
            stake_allocation = round(strategy.stake_allocation[index], 2)
            if stake_allocation <= 0:
                continue  # Skip combinations with zero stake allocation

            bet_names = ", ".join([bet.name for bet in combo.bets])
            combined_odds = round(combo.combined_odds, 2)
            potential_payout = round(combined_odds * stake_allocation, 2)
            ev_per_dollar = round(combo.ev_per_dollar, 2)

            total_stake += stake_allocation
            total_payout += potential_payout

            explanation = (
                f"<b>Combination:</b> {bet_names}<br>"
                f"<b>Combined Odds:</b> {combined_odds}<br>"
                f"<b>Stake Allocation:</b> ${stake_allocation}<br>"
                f"<b>Potential Payout:</b> ${potential_payout}<br>"
                f"<b>Expected Value per $:</b> {ev_per_dollar}<br><br>"
            )
            explanations.append(explanation)

            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)

            self.results_table.setItem(row_position, 0, QTableWidgetItem(bet_names))
            self.results_table.setItem(row_position, 1, QTableWidgetItem(f"{combined_odds:.2f}"))
            self.results_table.setItem(row_position, 2, QTableWidgetItem(f"${stake_allocation:.2f}"))
            self.results_table.setItem(row_position, 3, QTableWidgetItem(f"${potential_payout:.2f}"))
            self.results_table.setItem(row_position, 4, QTableWidgetItem(f"{ev_per_dollar:.2f}"))

        # Update Totals Display
        self.total_stake_label.setText(f"Total Stake Allocation ($): {total_stake:.2f}")
        self.total_payout_label.setText(f"Total Potential Payout ($): {total_payout:.2f}")

        # Enable sorting
        self.results_table.setSortingEnabled(True)
        # Initially sort by "EV per $"
        self.results_table.sortItems(4, Qt.DescendingOrder)

        # Populate explanations
        for explanation in explanations:
            self.explanations_text.append(explanation)

        # Add total stake and payout to explanations
        self.explanations_text.append(f"<b>Total Stake Allocation ($):</b> {total_stake:.2f}")
        self.explanations_text.append(f"<b>Total Potential Payout ($):</b> {total_payout:.2f}")

    def save_strategy(self, strategy):
        """Save the current betting strategy to a JSON file."""
        if not strategy:
            self.show_warning("No strategy to save. Please process a strategy first.")
            return

        options = QFileDialog.Options()
        # Set default directory to "results" folder
        default_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(default_dir, exist_ok=True)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Strategy", default_dir, "JSON Files (*.json);;All Files (*)", options=options
        )
        if not file_path:
            return

        # Filter combinations with stake allocation > 0
        filtered_combinations = []
        for combo, stake in zip(strategy.combinations, strategy.stake_allocation):
            if stake > 0:
                filtered_combinations.append((combo, stake))

        if not filtered_combinations:
            self.show_warning("No combinations with stake allocation greater than zero to save.")
            return

        data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_budget": strategy.total_budget,
            "total_stake": sum(stake for combo, stake in filtered_combinations),
            "total_potential_payout": sum(
                combo.combined_odds * stake for combo, stake in filtered_combinations
            ),
            "strategy_type": strategy.strategy_type,
            "risk_preference": strategy.risk_preference,
            "folds": strategy.folds,
            "combinations": [
                {
                    "bets": [
                        {"name": bet.name, "odds": bet.odds, "confidence": bet.confidence}
                        for bet in combo.bets
                    ],
                    "combined_odds": combo.combined_odds,
                    "combined_prob": combo.combined_prob,
                    "ev_per_dollar": combo.ev_per_dollar,
                    "stake_allocation": stake,
                    "potential_payout": combo.combined_odds * stake,
                }
                for combo, stake in filtered_combinations
            ],
        }

        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            QMessageBox.information(self, "Success", f"Strategy saved successfully to {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save strategy: {e}")

    def load_strategy(self):
        """Load a betting strategy from a JSON file."""
        options = QFileDialog.Options()
        # Set default directory to "results" folder
        default_dir = os.path.join(os.getcwd(), "results")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Strategy", default_dir, "JSON Files (*.json);;All Files (*)", options=options
        )
        if not file_path:
            return None

        try:
            with open(file_path, "r") as file:
                data = json.load(file)

            required_fields = {"total_budget", "strategy_type", "folds", "combinations", "risk_preference"}
            if not required_fields.issubset(data.keys()):
                raise ValueError("Invalid strategy file format.")

            combinations = []
            stake_allocations = []
            for combo_data in data["combinations"]:
                bets = [Bet(bet["name"], bet["odds"], bet["confidence"]) for bet in combo_data["bets"]]
                combo = Combination(bets)
                combinations.append(combo)
                stake_allocations.append(combo_data.get("stake_allocation", 0.0))

            strategy = BettingStrategy(
                total_budget=data["total_budget"],
                strategy_type=data["strategy_type"],
                folds=data["folds"],
                risk_preference=data["risk_preference"],
                combinations=combinations,
                stake_allocation=stake_allocations
            )

            return strategy
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load strategy: {e}")
            return None

    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)

    def reset(self):
        self.results_table.setRowCount(0)
        self.explanations_text.clear()
        self.total_stake_label.setText("Total Stake Allocation ($): 0.00")
        self.total_payout_label.setText("Total Potential Payout ($): 0.00")
