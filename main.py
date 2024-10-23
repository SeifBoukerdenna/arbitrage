import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main entry point for the Betting Strategy Simulator application."""
    app = QApplication(sys.argv)

    # Apply stylesheet
    with open("resources/styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    # Initialize and display the main window
    window = MainWindow()
    window.show()

    # Execute the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
