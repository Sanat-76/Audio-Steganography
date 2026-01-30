import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from scipy.io import wavfile
from steganography import FFTSteganography

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stego_engine = FFTSteganography()
        self.loaded_audio_path = None
        self.stego_audio_path = None
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FFT Audio Steganography')
        self.setGeometry(100, 100, 600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Audio Info Section
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        self.info_label = QLabel("No audio file loaded.")
        self.info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_frame)

        # Message Section
        layout.addWidget(QLabel("Secret Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter message to embed or view extracted message here...")
        layout.addWidget(self.message_input)

        # Buttons Section
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Audio")
        self.load_btn.clicked.connect(self.load_audio)
        btn_layout.addWidget(self.load_btn)

        self.embed_btn = QPushButton("Embed Message")
        self.embed_btn.clicked.connect(self.embed_message)
        btn_layout.addWidget(self.embed_btn)
        
        self.save_btn = QPushButton("Save Stego Audio")
        self.save_btn.clicked.connect(self.save_stego)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        btn_layout_2 = QHBoxLayout()
        self.load_stego_btn = QPushButton("Load Stego Audio")
        self.load_stego_btn.clicked.connect(self.load_stego)
        btn_layout_2.addWidget(self.load_stego_btn)

        self.extract_btn = QPushButton("Extract Message")
        self.extract_btn.clicked.connect(self.extract_message)
        btn_layout_2.addWidget(self.extract_btn)
        layout.addLayout(btn_layout_2)

        # Status Bar
        self.statusBar().showMessage("Ready")

        central_widget.setLayout(layout)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "WAV Files (*.wav)")
        if path:
            self.loaded_audio_path = path
            self.update_audio_info(path)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(path)}")

    def update_audio_info(self, path):
        try:
            sample_rate, data = wavfile.read(path)
            duration = len(data) / sample_rate
            channels = len(data.shape)
            info = (f"File: {os.path.basename(path)}\n"
                    f"Sample Rate: {sample_rate} Hz\n"
                    f"Channels: {'Stereo' if channels > 1 else 'Mono'}\n"
                    f"Duration: {duration:.2f} seconds")
            self.info_label.setText(info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read audio file: {e}")

    def embed_message(self):
        if not self.loaded_audio_path:
            QMessageBox.warning(self, "Warning", "Please load an audio file first.")
            return
        
        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Warning", "Please enter a message to embed.")
            return

        self.statusBar().showMessage("Embedding message...")
        QApplication.processEvents()

        try:
            # Temporarily save stego audio to a temp file or memory
            # For this app, we'll ask where to save it right away
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Stego Audio", "stego_audio.wav", "WAV Files (*.wav)")
            if save_path:
                self.stego_engine.embed(self.loaded_audio_path, message, save_path)
                self.statusBar().showMessage("Message embedded successfully!")
                QMessageBox.information(self, "Success", f"Stego audio saved to {save_path}")
            else:
                self.statusBar().showMessage("Embedding cancelled.")
        except Exception as e:
            self.statusBar().showMessage("Embedding failed.")
            QMessageBox.critical(self, "Error", str(e))

    def load_stego(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Stego Audio File", "", "WAV Files (*.wav)")
        if path:
            self.stego_audio_path = path
            self.update_audio_info(path)
            self.statusBar().showMessage(f"Loaded Stego: {os.path.basename(path)}")

    def extract_message(self):
        if not self.stego_audio_path:
            # Try to use loaded_audio_path if stego_audio_path is not set
            if self.loaded_audio_path:
                self.stego_audio_path = self.loaded_audio_path
            else:
                QMessageBox.warning(self, "Warning", "Please load a stego audio file first.")
                return

        self.statusBar().showMessage("Extracting message...")
        QApplication.processEvents()

        try:
            extracted_text = self.stego_engine.extract(self.stego_audio_path)
            self.message_input.setPlainText(extracted_text)
            self.statusBar().showMessage("Message extracted successfully!")
        except Exception as e:
            self.statusBar().showMessage("Extraction failed.")
            QMessageBox.critical(self, "Error", str(e))

    def save_stego(self):
        QMessageBox.information(self, "Info", "Use 'Embed Message' to select a location and save the stego audio.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
