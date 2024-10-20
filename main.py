# main.py

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("resources/styles.qss"))
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

def load_stylesheet(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Stylesheet not found: {path}")
        return ""

if __name__ == "__main__":
    main()
