from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QScrollArea, QGroupBox, QTextEdit, QHeaderView
)
from PyQt5.QtCore import Qt

class BettingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rafinioo's Betting Strategy Simulator")
        self.bets = []
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
        headers_layout = QHBoxLayout()
        headers = ["Name", "Odds", "Min Confidence (%)", "Max Confidence (%)"]
        for header in headers:
            lbl = QLabel(f"<b>{header}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(lbl)
        bets_layout.addLayout(headers_layout)

        # Scroll Area for Bets
        self.bets_scroll = QScrollArea()
        self.bets_scroll.setWidgetResizable(True)
        self.bets_container = QWidget()
        self.bets_vbox = QVBoxLayout()
        self.bets_container.setLayout(self.bets_vbox)
        self.bets_scroll.setWidget(self.bets_container)
        bets_layout.addWidget(self.bets_scroll)

        # Default Bets
        default_bets = [
            {"name": "Bet 1", "odds": "1.60", "min_conf": "60", "max_conf": "80"},
            {"name": "Bet 2", "odds": "1.70", "min_conf": "55", "max_conf": "75"},
            {"name": "Bet 3", "odds": "1.47", "min_conf": "50", "max_conf": "70"},
            {"name": "Bet 4", "odds": "1.30", "min_conf": "65", "max_conf": "85"},
            {"name": "Bet 5", "odds": "1.08", "min_conf": "70", "max_conf": "90"},
            {"name": "Bet 6", "odds": "1.13", "min_conf": "60", "max_conf": "80"},
        ]

        self.bet_widgets = []
        for i, bet in enumerate(default_bets):
            self.add_bet_entry(bet["name"], bet["odds"], bet["min_conf"], bet["max_conf"])

        bets_group.setLayout(bets_layout)
        main_layout.addWidget(bets_group)

        # Add/Remove Bet Buttons
        buttons_layout = QHBoxLayout()
        self.add_bet_btn = QPushButton("Add Bet")
        self.add_bet_btn.clicked.connect(self.add_bet)
        self.remove_bet_btn = QPushButton("Remove Bet")
        self.remove_bet_btn.clicked.connect(self.remove_bet)
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
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Combination", "Combined Odds", "Stake Allocation ($)", "Potential Payout ($)"])

        # Enable sorting before populating the table
        self.results_table.setSortingEnabled(True)

        # Set equal column widths
        header = self.results_table.horizontalHeader()
        for col in range(self.results_table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

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

    def add_bet_entry(self, name="Bet", odds="1.50", min_conf="50", max_conf="80"):
        """
        Adds a new bet entry to the bets section.
        """
        bet_layout = QHBoxLayout()

        name_input = QLineEdit(name)
        name_input.setPlaceholderText("Bet Name")
        odds_input = QLineEdit(odds)
        odds_input.setPlaceholderText("Odds (e.g., 1.50)")
        min_conf_input = QLineEdit(min_conf)
        min_conf_input.setPlaceholderText("Min Confidence (%)")
        max_conf_input = QLineEdit(max_conf)
        max_conf_input.setPlaceholderText("Max Confidence (%)")

        bet_layout.addWidget(name_input)
        bet_layout.addWidget(odds_input)
        bet_layout.addWidget(min_conf_input)
        bet_layout.addWidget(max_conf_input)

        self.bets_vbox.addLayout(bet_layout)
        self.bet_widgets.append((name_input, odds_input, min_conf_input, max_conf_input))

    def add_bet(self):
        """
        Slot to handle adding a new bet.
        """
        index = len(self.bet_widgets) + 1
        self.add_bet_entry(f"Bet {index}", "1.50", "50", "80")

    def remove_bet(self):
        """
        Slot to handle removing the last bet.
        """
        if self.bet_widgets:
            widgets = self.bet_widgets.pop()
            for widget in widgets:
                widget.deleteLater()
        else:
            QMessageBox.warning(self, "Warning", "No more bets to remove.")

    def on_strategy_type_change(self, text):
        """
        Adjust UI or behavior based on the selected strategy type.
        For example:
        - If "Accumulator" or "Parlay" is selected, disable the folds input and set folds to number of bets.
        - If "System" is selected, enable the folds input.
        """
        if text in ["Accumulator", "Parlay"]:
            num_bets = len(self.bet_widgets)
            self.folds_input.setText(str(num_bets))
            self.folds_input.setEnabled(False)
        elif text == "System":
            self.folds_input.setEnabled(True)
        else:
            self.folds_input.setEnabled(True)

    def process_strategy(self):
        """
        Processes the betting strategy based on user inputs.
        """
        try:
            # Validate and parse total budget
            total_budget_str = self.budget_input.text().strip()
            total_budget = float(total_budget_str)
            if total_budget <= 0:
                raise ValueError("Total budget must be greater than zero.")
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid Total Budget: {e}")
            return

        strategy_type = self.strategy_type_combo.currentText()

        try:
            folds_str = self.folds_input.text().strip()
            folds = int(folds_str)
            if folds <= 0:
                raise ValueError("Number of folds must be greater than zero.")
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid Number of Folds: {e}")
            return

        # Gather bets
        bets = []
        for idx, widgets in enumerate(self.bet_widgets, start=1):
            name = widgets[0].text().strip()
            odds_str = widgets[1].text().strip()
            min_conf_str = widgets[2].text().strip()
            max_conf_str = widgets[3].text().strip()

            if not name:
                QMessageBox.critical(self, "Input Error", f"Bet {idx}: Name cannot be empty.")
                return

            try:
                odds = float(odds_str)
                if odds <= 1.0:
                    raise ValueError("Odds must be greater than 1.0.")
            except ValueError as e:
                QMessageBox.critical(self, "Input Error", f"Bet {idx} ({name}): Invalid Odds: {e}")
                return

            try:
                min_conf = float(min_conf_str)
                max_conf = float(max_conf_str)
                if not (0 <= min_conf <= 100) or not (0 <= max_conf <= 100):
                    raise ValueError("Confidence percentages must be between 0 and 100.")
                if min_conf > max_conf:
                    raise ValueError("Minimum confidence cannot exceed maximum confidence.")
            except ValueError as e:
                QMessageBox.critical(self, "Input Error", f"Bet {idx} ({name}): Invalid Confidence: {e}")
                return

            bets.append(Bet(name, odds, min_conf, max_conf))

        if strategy_type in ["Accumulator", "Parlay"]:
            num_bets = len(bets)
            if folds != num_bets:
                QMessageBox.warning(
                    self, "Strategy Adjustment",
                    f"Number of folds ({folds}) adjusted to match the number of bets ({num_bets})."
                )
                folds = num_bets
                self.folds_input.setText(str(folds))

        if folds > len(bets):
            QMessageBox.critical(self, "Input Error", f"Number of folds ({folds}) cannot exceed the number of bets ({len(bets)}).")
            return

        # Create BettingStrategy
        self.strategy = BettingStrategy(total_budget, strategy_type, folds)
        self.strategy.generate_combinations(bets)
        self.strategy.allocate_stakes_kelly()

        # Display Results
        self.display_results()

    def display_results(self):
        self.results_table.setRowCount(0)
        self.explanations_text.clear()  # Clear previous explanations

        if not self.strategy:
            return

        combinations = self.strategy.combinations
        total_payout = 0
        explanations = []

        # Prepare a list to store all rows for sorting later
        rows = []

        for combo in combinations:
            bet_names = ", ".join([bet.name for bet in combo.bets])
            combined_odds = round(combo.combined_odds, 2)
            # Find the stake allocation for this combination
            index = self.strategy.combinations.index(combo)
            stake_allocation = round(self.strategy.stake_allocation[index], 2)
            potential_payout = round(combined_odds * stake_allocation, 2)
            total_payout += potential_payout

            # Save row data for sorting
            rows.append((bet_names, combined_odds, stake_allocation, potential_payout))

            # Generate explanation
            explanation = f"Combination: {bet_names}\n" \
                        f"Combined Odds: {combined_odds}\n" \
                        f"Stake Allocation: ${stake_allocation}\n" \
                        f"Potential Payout: ${potential_payout}\n"
            explanations.append(explanation)

        # Sort rows by the "Potential Payout" column (index 3) in descending order
        rows.sort(key=lambda x: x[3], reverse=True)

        # Populate the table with sorted data
        for bet_names, combined_odds, stake_allocation, potential_payout in rows:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            self.results_table.setItem(row_position, 0, QTableWidgetItem(bet_names))
            self.results_table.setItem(row_position, 1, QTableWidgetItem(f"{combined_odds:.2f}"))
            self.results_table.setItem(row_position, 2, QTableWidgetItem(f"{stake_allocation:.2f}"))
            self.results_table.setItem(row_position, 3, QTableWidgetItem(f"{potential_payout:.2f}"))

        # Add total payout row
        row_position = self.results_table.rowCount()
        self.results_table.insertRow(row_position)
        total_item = QTableWidgetItem("Total")
        total_item.setTextAlignment(Qt.AlignCenter)
        total_item.setFlags(total_item.flags() ^ Qt.ItemIsEditable)
        self.results_table.setItem(row_position, 0, total_item)
        self.results_table.setItem(row_position, 1, QTableWidgetItem(""))
        self.results_table.setItem(row_position, 2, QTableWidgetItem(""))
        total_payout_item = QTableWidgetItem(f"{total_payout:.2f}")
        total_payout_item.setTextAlignment(Qt.AlignCenter)
        total_payout_item.setFlags(total_payout_item.flags() ^ Qt.ItemIsEditable)
        self.results_table.setItem(row_position, 3, total_payout_item)

        # Populate Explanations Section
        self.explanations_text.append("<h3>Strategy Decision Explanations</h3>")
        for explanation in explanations:
            self.explanations_text.append(explanation)
            self.explanations_text.append("<hr>")  # Separator between explanations

        # Center align all rows in the table
        for row in range(self.results_table.rowCount()):
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
                    if row == row_position and col == 0:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

        # Set equal column widths
        header = self.results_table.horizontalHeader()
        for col in range(self.results_table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

    def save_strategy(self):
        """
        Saves the current betting strategy to a JSON file.
        """
        if not self.strategy:
            QMessageBox.warning(self, "Warning", "No strategy to save. Please process a strategy first.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Strategy", "", "JSON Files (*.json);;All Files (*)", options=options)
        if not file_path:
            return  # User cancelled

        # Serialize the strategy
        data = {
            "total_budget": self.strategy.total_budget,
            "strategy_type": self.strategy.strategy_type,
            "folds": self.strategy.folds,
            "combinations": [
                {
                    "bets": [
                        {
                            "name": bet.name,
                            "odds": bet.odds,
                            "confidence_min": bet.confidence_min,
                            "confidence_max": bet.confidence_max
                        } for bet in combo.bets
                    ]
                } for combo in self.strategy.combinations
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
        """
        Loads a betting strategy from a JSON file.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Strategy", "", "JSON Files (*.json);;All Files (*)", options=options)
        if not file_path:
            return  # User cancelled

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Validate required fields
            required_fields = ["total_budget", "strategy_type", "folds", "combinations", "stake_allocation"]
            if not all(field in data for field in required_fields):
                raise ValueError("Invalid strategy file format.")

            # Load betting strategy
            combinations = []
            for combo in data["combinations"]:
                bets = [Bet(
                    name=bet["name"],
                    odds=bet["odds"],
                    confidence_min=bet["confidence_min"],
                    confidence_max=bet["confidence_max"]
                ) for bet in combo["bets"]]
                combinations.append(Combination(bets))

            self.strategy = BettingStrategy(
                total_budget=data["total_budget"],
                strategy_type=data["strategy_type"],
                folds=data["folds"],
                combinations=combinations,
                stake_allocation=data["stake_allocation"]
            )

            # Update GUI fields
            self.budget_input.setText(str(self.strategy.total_budget))
            index = self.strategy_type_combo.findText(self.strategy.strategy_type)
            if index >= 0:
                self.strategy_type_combo.setCurrentIndex(index)
            self.folds_input.setText(str(self.strategy.folds))

            # Clear existing bet entries
            while self.bets_vbox.count():
                child = self.bets_vbox.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.bet_widgets.clear()

            # Recreate bet entries based on loaded combinations
            unique_bets = {}
            for combo in self.strategy.combinations:
                for bet in combo.bets:
                    unique_bets[bet.name] = bet
            for idx, bet in enumerate(unique_bets.values(), start=1):
                self.add_bet_entry(bet.name, str(bet.odds), str(bet.confidence_min), str(bet.confidence_max))

            # Allocate stakes again to ensure consistency
            self.strategy.allocate_stakes_kelly()

            # Display Results
            self.display_results()

            QMessageBox.information(self, "Success", f"Strategy loaded successfully from {file_path}.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load strategy: {e}")

def main():
    app = QApplication(sys.argv)
    window = BettingApp()
    window.showFullScreen()  # Launch the app in full-screen mode
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
