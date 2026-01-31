import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Optional: Apply some basic styling for better aesthetics
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        QFrame {
            border: 1px solid #333;
            border-radius: 10px;
            background-color: #252525;
            padding: 10px;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 14px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #0086f1;
        }
        QPushButton:disabled {
            background-color: #444;
            color: #888;
        }
        QPushButton#PlayBtn {
            font-size: 20px;
            border-radius: 20px;
            min-width: 40px;
            min-height: 40px;
            padding: 5px;
            background-color: #28a745;
        }
        QPushButton#PlayBtn:hover {
            background-color: #218838;
        }
        QPushButton#NavBtn {
            font-size: 18px;
            padding: 20px;
            border-radius: 12px;
            background-color: #0078d7;
            min-width: 200px;
            margin: 10px;
        }
        QPushButton#NavBtn:hover {
            background-color: #0086f1;
        }
        QPushButton#BackBtn {
            background-color: #444;
            max-width: 100px;
        }
        QPushButton#BackBtn:hover {
            background-color: #555;
        }
        QLabel#TitleLabel {
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 20px;
        }
        QLabel {
            font-size: 14px;
            color: #aaa;
        }
        QTextEdit {
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            color: white;
            font-family: 'Consolas', monospace;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
