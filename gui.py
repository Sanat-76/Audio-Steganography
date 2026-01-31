import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox, QFrame, QStackedWidget)
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
        self.active_play_btn = None
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FFT Audio Steganography')
        self.setGeometry(100, 100, 700, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create Screens
        self.home_screen = self.create_home_screen()
        self.embed_screen = self.create_embed_screen()
        self.extract_screen = self.create_extract_screen()

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.embed_screen)
        self.stack.addWidget(self.extract_screen)

        self.player.stateChanged.connect(self.on_state_changed)
        self.setStatusBar(None)

    def create_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Audio Steganography")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("Secure your messages inside audio files using FFT technology.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("margin-bottom: 40px;")
        layout.addWidget(desc)

        btn_layout = QHBoxLayout()
        
        self.goto_embed_btn = QPushButton("Embed Message")
        self.goto_embed_btn.setObjectName("NavBtn")
        self.goto_embed_btn.clicked.connect(self.show_embed_screen)
        btn_layout.addWidget(self.goto_embed_btn)

        self.goto_extract_btn = QPushButton("Extract Message")
        self.goto_extract_btn.setObjectName("NavBtn")
        self.goto_extract_btn.clicked.connect(self.show_extract_screen)
        btn_layout.addWidget(self.goto_extract_btn)

        layout.addLayout(btn_layout)
        return widget

    def create_embed_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Back Button
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("BackBtn")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

        title = QLabel("Embed a Secret Message")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Audio Section
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        self.embed_info_label = QLabel("No audio file loaded.")
        info_layout.addWidget(self.embed_info_label)

        controls_layout = QHBoxLayout()
        load_btn = QPushButton("Load Audio")
        load_btn.clicked.connect(self.load_audio)
        controls_layout.addWidget(load_btn)

        self.play_load_btn = QPushButton("▶")
        self.play_load_btn.setObjectName("PlayBtn")
        self.play_load_btn.setEnabled(False)
        self.play_load_btn.clicked.connect(lambda: self.toggle_play(self.loaded_audio_path, self.play_load_btn))
        controls_layout.addWidget(self.play_load_btn)
        info_layout.addLayout(controls_layout)
        layout.addWidget(info_frame)

        # Message Input
        layout.addWidget(QLabel("Secret Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter the message you want to hide...")
        layout.addWidget(self.message_input)

        # Action Button
        self.embed_btn = QPushButton("Run Embedding")
        self.embed_btn.clicked.connect(self.embed_message)
        layout.addWidget(self.embed_btn)

        return widget

    def create_extract_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Back Button
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("BackBtn")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

        title = QLabel("Extract a Hidden Message")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Audio Section
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        self.extract_info_label = QLabel("No stego audio file loaded.")
        info_layout.addWidget(self.extract_info_label)

        controls_layout = QHBoxLayout()
        load_btn = QPushButton("Load Stego Audio")
        load_btn.clicked.connect(self.load_stego)
        controls_layout.addWidget(load_btn)

        self.play_stego_btn = QPushButton("▶")
        self.play_stego_btn.setObjectName("PlayBtn")
        self.play_stego_btn.setEnabled(False)
        self.play_stego_btn.clicked.connect(lambda: self.toggle_play(self.stego_audio_path, self.play_stego_btn))
        controls_layout.addWidget(self.play_stego_btn)
        info_layout.addLayout(controls_layout)
        layout.addWidget(info_frame)

        # Result Section
        layout.addWidget(QLabel("Extracted Message:"))
        self.extracted_text_display = QTextEdit()
        self.extracted_text_display.setReadOnly(True)
        self.extracted_text_display.setPlaceholderText("The secret message will appear here...")
        layout.addWidget(self.extracted_text_display)

        # Action Button
        self.extract_btn = QPushButton("Run Extraction")
        self.extract_btn.clicked.connect(self.extract_message)
        layout.addWidget(self.extract_btn)

        return widget

    def show_embed_screen(self):
        self.stack.setCurrentWidget(self.embed_screen)

    def show_extract_screen(self):
        self.stack.setCurrentWidget(self.extract_screen)

    def go_back(self):
        self.player.stop()
        self.stack.setCurrentWidget(self.home_screen)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "WAV Files (*.wav)")
        if path:
            self.loaded_audio_path = path
            self.update_audio_info(path, self.embed_info_label)
            self.play_load_btn.setEnabled(True)

    def load_stego(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Stego Audio File", "", "WAV Files (*.wav)")
        if path:
            self.stego_audio_path = path
            self.update_audio_info(path, self.extract_info_label)
            self.play_stego_btn.setEnabled(True)

    def update_audio_info(self, path, label):
        try:
            sample_rate, data = wavfile.read(path)
            duration = len(data) / sample_rate
            info = f"File: {os.path.basename(path)} | {sample_rate}Hz | {duration:.2f}s"
            label.setText(info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read audio file: {e}")

    def play_audio(self, path, btn):
        if path and os.path.exists(path):
            if self.player.mediaStatus() != QMediaPlayer.NoMedia and self.active_play_btn == btn:
                if self.player.state() == QMediaPlayer.PlayingState:
                    self.player.pause()
                else:
                    self.player.play()
                return

            self.active_play_btn = btn
            url = QUrl.fromLocalFile(os.path.abspath(path))
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
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

    def embed_message(self):
        if not self.loaded_audio_path:
            QMessageBox.warning(self, "Warning", "Please load an audio file first.")
            return
        
        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Warning", "Please enter a message to embed.")
            return

        QApplication.processEvents()

        try:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Stego Audio", "stego_audio.wav", "WAV Files (*.wav)")
            if save_path:
                self.stego_engine.embed(self.loaded_audio_path, message, save_path)
                self.message_input.clear()
                QMessageBox.information(self, "Success", f"Stego audio saved to {save_path}")
            else:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def extract_message(self):
        if not self.stego_audio_path:
            QMessageBox.warning(self, "Warning", "Please load a stego audio file first.")
            return

        QApplication.processEvents()

        try:
            extracted_text = self.stego_engine.extract(self.stego_audio_path)
            self.extracted_text_display.setPlainText(extracted_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
