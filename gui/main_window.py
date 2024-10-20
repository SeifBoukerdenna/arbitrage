# gui/main_window.py

import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QScrollArea, QGroupBox, QTextEdit, QSplitter, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QColor
from .bet_entry_widget import BetEntryWidget
from models.models import Bet, BettingStrategy, Combination
from utils.utils import generate_combinations, allocate_stakes
from data.bets_data import default_bets

class MainWindow(QWidget):
    """Main window for Rafinioo's Betting Strategy Simulator."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rafinioo's Betting Strategy Simulator")
        self.setMinimumSize(900, 700)  # Set a larger minimum size for better layout
        self.bets_widgets = []
        self.strategy = None
        self.init_ui()
        self.apply_stylesheet()

    def apply_stylesheet(self):
        """Apply a stylesheet to the application for enhanced aesthetics."""
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                border: none;
                border-radius: 4px;
                color: white;
                background-color: #4CAF50;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QLabel {
                font-weight: bold;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Set margins for the main layout
        main_layout.setSpacing(10)  # Set spacing between widgets

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

        # Scroll Area to make the entire layout scrollable if needed
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.central_widget_with_layout(main_layout))

        # Final Layout
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(scroll_area)

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
        bets_splitter.setHandleWidth(1)  # Make the splitter handle less prominent

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
        self.add_bet_btn.clicked.connect(self.add_bet_entry)
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
        """Create action buttons for processing, saving, and loading strategies."""
        buttons_widget = QWidget()
        action_layout = QHBoxLayout(buttons_widget)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(20)

        self.process_btn = QPushButton("Process Betting Strategy")
        self.process_btn.clicked.connect(self.process_strategy)
        self.process_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.process_btn.setToolTip("Process the betting strategy based on entered bets.")

        self.save_btn = QPushButton("Save Strategy")
        self.save_btn.clicked.connect(self.save_strategy)
        self.save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.save_btn.setToolTip("Save the current betting strategy to a file.")

        self.load_btn = QPushButton("Load Strategy")
        self.load_btn.clicked.connect(self.load_strategy)
        self.load_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.load_btn.setToolTip("Load a previously saved betting strategy from a file.")

        action_layout.addWidget(self.process_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.load_btn)

        buttons_widget.setLayout(action_layout)
        buttons_widget.setFixedHeight(70)

        return buttons_widget

    def create_results_explanations_section(self) -> QSplitter:
        """Create the results and explanations section."""
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)  # Make the splitter handle less prominent

        # Results Table Group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(10, 10, 10, 10)
        results_layout.setSpacing(10)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Combination", "Combined Odds", "Stake Allocation ($)", "Potential Payout ($)"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #f9f9f9;
                gridline-color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #b3d7ff;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #cccccc;
            }
            /* Alternate row colors */
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:nth-child(even) {
                background-color: #ffffff;
            }
            QTableWidget::item:nth-child(odd) {
                background-color: #f2f2f2;
            }
        """)

        # Enable user to resize columns
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # Allow automatic row height based on content
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        results_group.setMinimumHeight(250)
        splitter.addWidget(results_group)

        # Totals Display Group
        totals_group = QGroupBox("Totals")
        totals_layout = QHBoxLayout()
        totals_layout.setContentsMargins(10, 10, 10, 10)
        totals_layout.setSpacing(20)

        self.total_stake_label = QLabel("Total Stake Allocation ($): 0.00")
        self.total_payout_label = QLabel("Total Potential Payout ($): 0.00")

        # Styling for totals
        totals_font = QFont()
        totals_font.setPointSize(12)
        totals_font.setBold(True)
        self.total_stake_label.setFont(totals_font)
        self.total_payout_label.setFont(totals_font)

        totals_layout.addWidget(self.total_stake_label)
        totals_layout.addWidget(self.total_payout_label)
        totals_group.setLayout(totals_layout)
        totals_group.setMinimumHeight(50)
        splitter.addWidget(totals_group)

        # Explanations Section Group
        explanations_group = QGroupBox("Strategy Explanations")
        explanations_layout = QVBoxLayout()
        explanations_layout.setContentsMargins(10, 10, 10, 10)
        explanations_layout.setSpacing(10)

        self.explanations_text = QTextEdit()
        self.explanations_text.setReadOnly(True)
        self.explanations_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }
        """)
        explanations_layout.addWidget(self.explanations_text)
        explanations_group.setLayout(explanations_layout)
        explanations_group.setMinimumHeight(150)
        splitter.addWidget(explanations_group)

        # Set initial sizes for splitter
        splitter.setSizes([300, 60, 200])

        return splitter

    def central_widget_with_layout(self, layout: QVBoxLayout) -> QWidget:
        """Wrap the given layout in a central widget."""
        central_widget = QWidget()
        central_widget.setLayout(layout)
        return central_widget

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
        """
        Handle changes in the strategy type selection.

        :param strategy_type: Newly selected strategy type.
        """
        if strategy_type in ["Accumulator", "Parlay"]:
            num_bets = len(self.bets_widgets)
            self.folds_input.setText(str(num_bets))
            self.folds_input.setEnabled(False)
        elif strategy_type == "System":
            self.folds_input.setEnabled(True)

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

        if strategy_type in ["Accumulator", "Parlay"]:
            folds = len(bets)
            self.folds_input.setText(str(folds))

        if folds > len(bets):
            QMessageBox.critical(
                self, "Input Error",
                f"Number of folds ({folds}) cannot exceed the number of bets ({len(bets)})."
            )
            return

        # Generate combinations and allocate stakes
        self.strategy = BettingStrategy(total_budget, strategy_type, folds)
        self.strategy.combinations = generate_combinations(bets, folds, strategy_type)
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
        combo_rows = []

        # Collect all combination data first
        for index, combo in enumerate(combinations):
            bet_names = ", ".join([bet.name for bet in combo.bets])
            combined_odds = round(combo.combined_odds, 2)
            stake_allocation = round(self.strategy.stake_allocation[index], 2)
            potential_payout = round(combined_odds * stake_allocation, 2)

            total_stake += stake_allocation
            total_payout += potential_payout

            explanation = (
                f"<b>Combination:</b> {bet_names}<br>"
                f"<b>Combined Odds:</b> {combined_odds}<br>"
                f"<b>Stake Allocation:</b> ${stake_allocation}<br>"
                f"<b>Potential Payout:</b> ${potential_payout}<br><br>"
            )
            explanations.append(explanation)

            combo_rows.append({
                "Combination": bet_names,
                "Combined Odds": combined_odds,
                "Stake Allocation ($)": stake_allocation,
                "Potential Payout ($)": potential_payout
            })

        # Sort the combo_rows based on "Stake Allocation ($)" in descending order
        sorted_combo_rows = sorted(combo_rows, key=lambda x: x["Stake Allocation ($)"], reverse=True)

        # Populate the results table with sorted rows
        for row_data in sorted_combo_rows:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)

            combination_item = QTableWidgetItem(row_data["Combination"])
            combination_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.results_table.setItem(row_position, 0, combination_item)

            odds_item = QTableWidgetItem(f"{row_data['Combined Odds']:.2f}")
            odds_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.results_table.setItem(row_position, 1, odds_item)

            stake_item = QTableWidgetItem(f"${row_data['Stake Allocation ($)']:.2f}")
            stake_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.results_table.setItem(row_position, 2, stake_item)

            payout_item = QTableWidgetItem(f"${row_data['Potential Payout ($)']:.2f}")
            payout_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.results_table.setItem(row_position, 3, payout_item)

        # Update Totals Display
        self.total_stake_label.setText(f"Total Stake Allocation ($): {total_stake:.2f}")
        self.total_payout_label.setText(f"Total Potential Payout ($): {total_payout:.2f}")

        # Enable sorting (user can sort by clicking column headers)
        self.results_table.setSortingEnabled(True)
        # Initially sort by "Stake Allocation ($)" descending
        self.results_table.sortItems(2, Qt.DescendingOrder)

        # Populate explanations
        for explanation in explanations:
            self.explanations_text.append(explanation)

    def save_strategy(self):
        """Save the current betting strategy to a JSON file."""
        if not self.strategy:
            QMessageBox.warning(self, "Warning", "No strategy to save. Please process a strategy first.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Strategy", "", "JSON Files (*.json);;All Files (*)", options=options
        )
        if not file_path:
            return

        data = {
            "total_budget": self.strategy.total_budget,
            "strategy_type": self.strategy.strategy_type,
            "folds": self.strategy.folds,
            "combinations": [
                {
                    "bets": [
                        {"name": bet.name, "odds": bet.odds, "confidence": bet.confidence}
                        for bet in combo.bets
                    ]
                }
                for combo in self.strategy.combinations
            ],
            "stake_allocation": self.strategy.stake_allocation
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
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Strategy", "", "JSON Files (*.json);;All Files (*)", options=options
        )
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                data = json.load(file)

            required_fields = {"total_budget", "strategy_type", "folds", "combinations", "stake_allocation"}
            if not required_fields.issubset(data.keys()):
                raise ValueError("Invalid strategy file format.")

            combinations = [
                Combination(
                    bets=[Bet(bet["name"], bet["odds"], bet["confidence"]) for bet in combo["bets"]]
                )
                for combo in data["combinations"]
            ]

            self.strategy = BettingStrategy(
                total_budget=data["total_budget"],
                strategy_type=data["strategy_type"],
                folds=data["folds"],
                combinations=combinations,
                stake_allocation=data["stake_allocation"]
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
