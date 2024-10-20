# main.py

import sys
import json
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def load_stylesheet(path: str) -> str:
    """
    Load the stylesheet from the given path.

    :param path: Path to the QSS stylesheet file.
    :return: Stylesheet as a string.
    """
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Stylesheet not found: {path}")
        return ""

def main():
    """Main entry point for the Betting Strategy Simulator application."""
    app = QApplication(sys.argv)

    # Apply stylesheet
    stylesheet = load_stylesheet("resources/styles.qss")
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Initialize and display the main window
    window = MainWindow()
    window.showMaximized()

    # Execute the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
s