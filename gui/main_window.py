# main_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from .widgets.strategy_config_widget import StrategyConfigWidget
from .widgets.bets_entry_widget import BetsEntryWidget
from .widgets.action_buttons_widget import ActionButtonsWidget
from .widgets.results_explanations_widget import ResultsExplanationsWidget
from .widgets.visualization_widget import VisualizationWidget
from models.betting_strategy import BettingStrategy
from utils.combination_utils import generate_combinations
from utils.stake_allocation_utils import allocate_stakes


class MainWindow(QWidget):
    """Main window for the Betting Strategy Simulator."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Betting Strategy Simulator")
        self.setMinimumSize(900, 700)
        self.strategy = None
        self.init_ui()
        self.apply_light_mode()

    def apply_light_mode(self):
        """Ensure the application uses light mode colors."""
        pass  # Implement light mode styling if needed

    def init_ui(self):
        """Initialize the user interface."""

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Main Splitter to divide the window vertically
        main_splitter = QSplitter(Qt.Vertical)

        # Strategy Configuration Section
        self.config_widget = StrategyConfigWidget()
        main_splitter.addWidget(self.config_widget)

        # Bets Entry Section
        self.bets_widget = BetsEntryWidget()
        main_splitter.addWidget(self.bets_widget)

        # Action Buttons Section
        self.action_buttons_widget = ActionButtonsWidget()
        main_splitter.addWidget(self.action_buttons_widget)

        # Connect action buttons to methods
        self.action_buttons_widget.process_btn.clicked.connect(self.process_strategy)
        self.action_buttons_widget.save_btn.clicked.connect(self.save_strategy)
        self.action_buttons_widget.load_btn.clicked.connect(self.load_strategy)
        self.action_buttons_widget.reset_btn.clicked.connect(self.reset_app)

        # Results and Explanations Section
        self.results_widget = ResultsExplanationsWidget()
        # Visualization Widget
        self.visualization_widget = VisualizationWidget()

        # Add a splitter to hold results and visualizations side by side
        results_visual_splitter = QSplitter(Qt.Horizontal)
        results_visual_splitter.addWidget(self.results_widget)
        results_visual_splitter.addWidget(self.visualization_widget)
        results_visual_splitter.setStretchFactor(0, 3)
        results_visual_splitter.setStretchFactor(1, 2)

        main_splitter.addWidget(results_visual_splitter)

        # Add the splitter to the main layout
        main_layout.addWidget(main_splitter)

        # Set the main layout
        self.setLayout(main_layout)

    def process_strategy(self):
        """Process the betting strategy based on user input."""
        try:
            # Retrieve configuration data
            total_budget = self.config_widget.get_total_budget()
            strategy_type = self.config_widget.get_strategy_type()
            risk_preference = self.config_widget.get_risk_preference()

            # Retrieve folds if strategy_type is System
            folds = None
            if strategy_type == "System":
                folds = self.config_widget.get_folds()

            # Retrieve bets data
            bets = self.bets_widget.get_bets()

            # Error checking
            if total_budget <= 0:
                self.results_widget.show_warning("Total budget must be greater than zero.")
                return
            if not bets:
                self.results_widget.show_warning("Please enter at least one bet.")
                return

            # Generate combinations
            self.strategy = BettingStrategy(total_budget, strategy_type, folds, risk_preference)
            self.strategy.combinations = generate_combinations(
                bets, strategy_type, risk_preference, folds=folds
            )

            # Filter and sort combinations based on risk preference
            self.strategy.filter_and_sort_combinations()

            if not self.strategy.combinations:
                self.results_widget.show_warning("No suitable combinations found based on your risk preference.")
                return

            # Allocate stakes
            allocate_stakes(self.strategy)

            # Display results
            self.display_results()
        except Exception as e:
            self.results_widget.show_warning(str(e))

    def display_results(self):
        """Display the results and explanations based on the processed strategy."""
        self.results_widget.display_results(self.strategy)
        self.visualization_widget.set_strategy(self.strategy)

    def save_strategy(self):
        """Save the current betting strategy to a JSON file."""
        self.results_widget.save_strategy(self.strategy)

    def load_strategy(self):
        """Load a betting strategy from a JSON file."""
        self.strategy = self.results_widget.load_strategy()
        if self.strategy:
            # Update UI with loaded data
            self.config_widget.set_strategy(self.strategy)
            self.bets_widget.set_bets(self.strategy.get_unique_bets())
            self.display_results()

    def reset_app(self):
        """Reset the application to its initial state."""
        self.config_widget.reset()
        self.bets_widget.reset()
        self.results_widget.reset()
        self.visualization_widget.set_strategy(None)
        self.strategy = None
