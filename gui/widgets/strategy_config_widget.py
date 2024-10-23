from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QGroupBox
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class StrategyConfigWidget(QGroupBox):
    """Widget for configuring the betting strategy."""

    def __init__(self):
        super().__init__("Betting Strategy Configuration")
        self.init_ui()

    def init_ui(self):
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

        self.setLayout(config_layout)

    def get_total_budget(self) -> float:
        return float(self.budget_input.text().strip())

    def get_strategy_type(self) -> str:
        return self.strategy_type_combo.currentText()

    def get_risk_preference(self) -> str:
        return self.risk_combo.currentText()

    def set_strategy(self, strategy):
        self.budget_input.setText(f"{strategy.total_budget:.2f}")
        self.strategy_type_combo.setCurrentText(strategy.strategy_type)
        self.risk_combo.setCurrentText(strategy.risk_preference)
        self.folds_input.setText(str(strategy.folds))

    def reset(self):
        self.budget_input.setText("100.00")
        self.strategy_type_combo.setCurrentIndex(0)
        self.risk_combo.setCurrentIndex(1)
        self.folds_input.setText("4")
        self.folds_input.setEnabled(False)
