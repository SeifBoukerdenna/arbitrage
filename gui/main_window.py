import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QScrollArea, QGroupBox, QTextEdit, QSplitter, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QPalette, QColor
from .bet_entry_widget import BetEntryWidget
from models.models import Bet, BettingStrategy, Combination
from utils.utils import generate_combinations, allocate_stakes
from data.bets_data import default_bets


class MainWindow(QWidget):
    """Main window for the Betting Strategy Simulator."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Betting Strategy Simulator")
        self.setMinimumSize(900, 700)
        self.bets_widgets = []
        self.strategy = None
        self.init_ui()
        self.apply_light_mode()

    def apply_light_mode(self):
        """Ensure the application uses light mode colors."""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        palette.setColor(QPalette.Base, QColor("#ffffff"))
        palette.setColor(QPalette.AlternateBase, QColor("#f6f6f6"))
        palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ToolTipText, QColor("#000000"))
        palette.setColor(QPalette.Text, QColor("#000000"))
        palette.setColor(QPalette.Button, QColor("#f0f0f0"))
        palette.setColor(QPalette.ButtonText, QColor("#000000"))
        palette.setColor(QPalette.BrightText, QColor("#ff0000"))
        self.setPalette(palette)

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Main Splitter to divide the window vertically
        main_splitter = QSplitter(Qt.Vertical)

        # Strategy Configuration Section
        config_group = self.create_strategy_configuration()
        main_splitter.addWidget(config_group)

        # Bets Entry Section
        bets_splitter = self.create_bets_section()
        main_splitter.addWidget(bets_splitter)

        # Action Buttons Section
        action_widget = self.create_action_buttons()
        main_splitter.addWidget(action_widget)

        # Results and Explanations Section
        results_explanations_splitter = self.create_results_explanations_section()
        main_splitter.addWidget(results_explanations_splitter)

        # Add the splitter to the main layout
        main_layout.addWidget(main_splitter)

        # Set the main layout
        self.setLayout(main_layout)

    def create_strategy_configuration(self) -> QGroupBox:
        """Create the strategy configuration group."""
        config_group = QGroupBox("Betting Strategy Configuration")
        config_layout = QHBoxLayout()
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(20)

        # Total Budget
        budget_label = QLabel("Total Budget ($):")
        self.budget_input = QLineEdit("100.00")
        self.budget_input.setFixedWidth(100)
        self.budget_input.setValidator(QDoubleValidator(0.01, 1000000.00, 2))
        self.budget_input.setToolTip("Enter your total budget for betting.")
        config_layout.addWidget(budget_label)
        config_layout.addWidget(self.budget_input)

        # Strategy Type
        strategy_label = QLabel("Strategy Type:")
        self.strategy_type_combo = QComboBox()
        self.strategy_type_combo.addItems(["Accumulator", "Parlay", "System"])
        self.strategy_type_combo.currentTextChanged.connect(self.on_strategy_type_change)
        self.strategy_type_combo.setToolTip("Select your betting strategy type.")
        config_layout.addWidget(strategy_label)
        config_layout.addWidget(self.strategy_type_combo)

        # Risk Preference
        risk_label = QLabel("Risk Preference:")
        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["Conservative", "Moderate", "Aggressive"])
        self.risk_combo.setToolTip("Select your risk preference.")
        config_layout.addWidget(risk_label)
        config_layout.addWidget(self.risk_combo)

        # Number of Folds
        folds_label = QLabel("Number of Folds (Legs per Combination):")
        self.folds_input = QLineEdit("4")
        self.folds_input.setFixedWidth(50)
        self.folds_input.setValidator(QIntValidator(1, 100))
        self.folds_input.setToolTip("Enter the number of folds (legs) per combination.")
        config_layout.addWidget(folds_label)
        config_layout.addWidget(self.folds_input)

        config_group.setLayout(config_layout)
        return config_group

    def create_bets_section(self) -> QSplitter:
        """Create the bets entry section with add/remove functionality."""
        bets_splitter = QSplitter(Qt.Vertical)
        bets_splitter.setHandleWidth(1)

        # Bets Entry Group
        bets_group = QGroupBox("Bets")
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

        for bet in default_bets:
            self.add_bet_entry(bet["name"], bet["odds"], bet["confidence"])

        bets_group.setLayout(bets_layout)
        bets_splitter.addWidget(bets_group)

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

        bets_splitter.addWidget(buttons_widget)
        return bets_splitter

    def create_action_buttons(self) -> QWidget:
        """Create action buttons for processing, saving, loading, and resetting strategies."""
        buttons_widget = QWidget()
        action_layout = QHBoxLayout(buttons_widget)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(20)

        self.process_btn = QPushButton("Process Betting Strategy")
        self.process_btn.clicked.connect(self.process_strategy)
        self.process_btn.setToolTip("Process the betting strategy based on entered bets.")

        self.save_btn = QPushButton("Save Strategy")
        self.save_btn.clicked.connect(self.save_strategy)
        self.save_btn.setToolTip("Save the current betting strategy to a file.")

        self.load_btn = QPushButton("Load Strategy")
        self.load_btn.clicked.connect(self.load_strategy)
        self.load_btn.setToolTip("Load a previously saved betting strategy from a file.")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_app)
        self.reset_btn.setToolTip("Reset the application to its initial state.")

        action_layout.addWidget(self.process_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.load_btn)
        action_layout.addWidget(self.reset_btn)

        buttons_widget.setLayout(action_layout)
        buttons_widget.setFixedHeight(70)

        return buttons_widget

    def create_results_explanations_section(self) -> QSplitter:
        """Create the results and explanations section."""
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)

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
        splitter.addWidget(results_group)

        # Totals Display Group
        totals_group = QGroupBox("Totals")
        totals_layout = QHBoxLayout()
        totals_layout.setContentsMargins(10, 10, 10, 10)
        totals_layout.setSpacing(20)

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
        splitter.addWidget(totals_group)

        # Explanations Section Group
        explanations_group = QGroupBox("Strategy Explanations")
        explanations_layout = QVBoxLayout()
        explanations_layout.setContentsMargins(10, 10, 10, 10)
        explanations_layout.setSpacing(10)

        self.explanations_text = QTextEdit()
        self.explanations_text.setReadOnly(True)
        explanations_layout.addWidget(self.explanations_text)
        explanations_group.setLayout(explanations_layout)
        splitter.addWidget(explanations_group)

        return splitter

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

    def on_strategy_type_change(self, strategy_type: str):
        """Handle changes in the strategy type selection."""
        if strategy_type in ["Accumulator", "Parlay"]:
            num_bets = len(self.bets_widgets)
            self.folds_input.setText(str(num_bets))
            self.folds_input.setEnabled(False)
        elif strategy_type == "System":
            self.folds_input.setEnabled(False)
            self.folds_input.setText("Varies")

    def process_strategy(self):
        """Process the betting strategy based on user input."""
        try:
            total_budget = float(self.budget_input.text().strip())
            if total_budget <= 0:
                raise ValueError("Total budget must be greater than zero.")
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid Total Budget: {e}")
            return

        strategy_type = self.strategy_type_combo.currentText()
        risk_preference = self.risk_combo.currentText()

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
                return

        folds = len(bets)
        self.folds_input.setText(str(folds))

        if strategy_type == "System":
            folds = None  # For System strategy, folds vary
        else:
            if folds > len(bets):
                QMessageBox.critical(
                    self, "Input Error",
                    f"Number of folds ({folds}) cannot exceed the number of bets ({len(bets)})."
                )
                return

        # Generate combinations
        self.strategy = BettingStrategy(total_budget, strategy_type, folds, risk_preference)
        self.strategy.combinations = generate_combinations(bets, strategy_type, max_combination_size=len(bets))

        # Filter and sort combinations based on risk preference
        self.strategy.filter_and_sort_combinations()

        if not self.strategy.combinations:
            QMessageBox.warning(self, "Warning", "No suitable combinations found based on your risk preference.")
            return

        # Allocate stakes
        allocate_stakes(self.strategy)

        # Display results
        self.display_results()

    def display_results(self):
        """Display the results and explanations based on the processed strategy."""
        self.results_table.setRowCount(0)
        self.explanations_text.clear()

        if not self.strategy:
            return

        combinations = self.strategy.combinations
        total_payout = 0.0
        total_stake = 0.0
        explanations = []

        for index, combo in enumerate(combinations):
            stake_allocation = round(self.strategy.stake_allocation[index], 2)
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

    def save_strategy(self):
        """Save the current betting strategy to a JSON file."""
        if not self.strategy:
            QMessageBox.warning(self, "Warning", "No strategy to save. Please process a strategy first.")
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
        for combo, stake in zip(self.strategy.combinations, self.strategy.stake_allocation):
            if stake > 0:
                filtered_combinations.append((combo, stake))

        if not filtered_combinations:
            QMessageBox.warning(self, "Warning", "No combinations with stake allocation greater than zero to save.")
            return

        data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_budget": self.strategy.total_budget,
            "total_stake": sum(stake for combo, stake in filtered_combinations),
            "total_potential_payout": sum(
                combo.combined_odds * stake for combo, stake in filtered_combinations
            ),
            "strategy_type": self.strategy.strategy_type,
            "risk_preference": self.strategy.risk_preference,
            "folds": self.strategy.folds,
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
            return

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

            self.strategy = BettingStrategy(
                total_budget=data["total_budget"],
                strategy_type=data["strategy_type"],
                folds=data["folds"],
                risk_preference=data["risk_preference"],
                combinations=combinations,
                stake_allocation=stake_allocations
            )

            # Update UI with loaded data
            self.update_ui_with_loaded_strategy()

            QMessageBox.information(self, "Success", f"Strategy loaded successfully from {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load strategy: {e}")

    def update_ui_with_loaded_strategy(self):
        """Update the UI elements based on the loaded strategy."""
        self.budget_input.setText(f"{self.strategy.total_budget:.2f}")
        strategy_index = self.strategy_type_combo.findText(self.strategy.strategy_type)
        if strategy_index >= 0:
            self.strategy_type_combo.setCurrentIndex(strategy_index)
        risk_index = self.risk_combo.findText(self.strategy.risk_preference)
        if risk_index >= 0:
            self.risk_combo.setCurrentIndex(risk_index)
        self.folds_input.setText(str(self.strategy.folds))

        # Clear existing bets
        while self.bets_widgets:
            self.remove_bet_entry()

        # Collect unique bets to prevent duplicates
        unique_bets = {}
        for combo in self.strategy.combinations:
            for bet in combo.bets:
                unique_bets[bet.name] = bet

        # Add bets to the UI
        for bet in unique_bets.values():
            self.add_bet_entry(bet.name, f"{bet.odds:.2f}", f"{bet.confidence:.1f}")

        # Display results
        self.display_results()

    def reset_app(self):
        """Reset the application to its initial state."""
        self.budget_input.setText("100.00")
        self.strategy_type_combo.setCurrentIndex(0)
        self.risk_combo.setCurrentIndex(1)  # Set to "Moderate" by default
        self.folds_input.setText("4")
        self.folds_input.setEnabled(False)

        # Clear bets
        while self.bets_widgets:
            self.remove_bet_entry()

        # Add default bets
        for bet in default_bets:
            self.add_bet_entry(bet["name"], bet["odds"], bet["confidence"])

        # Clear results and explanations
        self.results_table.setRowCount(0)
        self.explanations_text.clear()
        self.total_stake_label.setText("Total Stake Allocation ($): 0.00")
        self.total_payout_label.setText("Total Potential Payout ($): 0.00")
        self.strategy = None

        QMessageBox.information(self, "Reset", "Application has been reset to its initial state.")
