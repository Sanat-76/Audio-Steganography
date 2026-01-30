import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from scipy.io import wavfile
from steganography import FFTSteganography

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stego_engine = FFTSteganography()
        self.loaded_audio_path = None
        self.stego_audio_path = None
        self.player = QMediaPlayer()
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FFT Audio Steganography')
        self.setGeometry(100, 100, 600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Loaded Audio Section
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        self.info_label = QLabel("No audio file loaded.")
        self.info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label)
        
        # Playback Controls Overlay-style
        controls_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Audio")
        self.load_btn.clicked.connect(self.load_audio)
        controls_layout.addWidget(self.load_btn)

        self.play_load_btn = QPushButton("▶")
        self.play_load_btn.setObjectName("PlayBtn")
        self.play_load_btn.clicked.connect(lambda: self.toggle_play(self.loaded_audio_path, self.play_load_btn))
        self.play_load_btn.setEnabled(False)
        controls_layout.addWidget(self.play_load_btn)
        
        info_layout.addLayout(controls_layout)
        layout.addWidget(info_frame)

        # Message Section
        layout.addWidget(QLabel("Secret Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter message to embed or view extracted message here...")
        layout.addWidget(self.message_input)

        # Action Buttons (Embed/Extract)
        action_frame = QFrame()
        action_layout = QHBoxLayout(action_frame)
        
        self.embed_btn = QPushButton("Embed Message")
        self.embed_btn.clicked.connect(self.embed_message)
        action_layout.addWidget(self.embed_btn)
        
        self.load_stego_btn = QPushButton("Load Stego")
        self.load_stego_btn.clicked.connect(self.load_stego)
        action_layout.addWidget(self.load_stego_btn)

        self.extract_btn = QPushButton("Extract Message")
        self.extract_btn.clicked.connect(self.extract_message)
        action_layout.addWidget(self.extract_btn)
        layout.addWidget(action_frame)

        # Stego Playback Section (Sticky Bottom)
        self.stego_playback_frame = QFrame()
        stego_layout = QHBoxLayout(self.stego_playback_frame)
        stego_layout.addWidget(QLabel("Stego Audio:"))
        
        self.play_stego_btn = QPushButton("▶")
        self.play_stego_btn.setObjectName("PlayBtn")
        self.play_stego_btn.clicked.connect(lambda: self.toggle_play(self.stego_audio_path, self.play_stego_btn))
        self.play_stego_btn.setEnabled(False)
        stego_layout.addWidget(self.play_stego_btn)
        
        self.stego_name_label = QLabel("None")
        stego_layout.addWidget(self.stego_name_label)
        layout.addWidget(self.stego_playback_frame)

        # Connect player state change
        self.player.stateChanged.connect(self.on_state_changed)
        self.active_play_btn = None

        # Status Bar
        self.statusBar().showMessage("Ready")

        central_widget.setLayout(layout)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "WAV Files (*.wav)")
        if path:
            self.loaded_audio_path = path
            self.update_audio_info(path)
            self.play_load_btn.setEnabled(True)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(path)}")

    def play_audio(self, path, btn):
        if path and os.path.exists(path):
            # If playing the same file, just pause/resume
            if self.player.mediaStatus() != QMediaPlayer.NoMedia and self.active_play_btn == btn:
                if self.player.state() == QMediaPlayer.PlayingState:
                    self.player.pause()
                else:
                    self.player.play()
                return

            # Otherwise, load new file
            self.active_play_btn = btn
            url = QUrl.fromLocalFile(os.path.abspath(path))
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
            self.statusBar().showMessage(f"Playing: {os.path.basename(path)}")
        else:
            QMessageBox.warning(self, "Error", "Audio file not found.")

    def toggle_play(self, path, btn):
        self.play_audio(path, btn)

    def on_state_changed(self, state):
        if self.active_play_btn:
            if state == QMediaPlayer.PlayingState:
                self.active_play_btn.setText("⏸")
            else:
                self.active_play_btn.setText("▶")

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
                self.stego_audio_path = save_path
                self.stego_name_label.setText(os.path.basename(save_path))
                self.play_stego_btn.setEnabled(True)
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
            self.stego_name_label.setText(os.path.basename(path))
            self.play_stego_btn.setEnabled(True)
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
