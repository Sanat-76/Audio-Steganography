import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Optional: Apply some basic styling for better aesthetics
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QLabel {
            font-size: 14px;
        }
        QTextEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
