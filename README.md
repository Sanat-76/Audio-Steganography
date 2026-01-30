# Audio Steganography using FFT

A Python desktop application for embedding and extracting secret messages within audio files (WAV) using Frequency-Domain Steganography (FFT).

## Features
- **FFT-based Steganography**: Embeds data in the frequency domain for better robustness compared to simple LSB techniques.
- **Graphical User Interface**: Built with PyQt5 for an easy-to-use experience.
- **Audio Quality Preservation**: Targeted frequency range embedding to minimize audible distortion.
- **Real-time Extraction**: Instantly extract messages from steganographic audio files.

## Prerequisites
- Python 3.7+
- A virtual environment (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url> audiosteg
   cd audiosteg
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Generate Sample Audio** (Optional):
   If you don't have a WAV file handy, run the sample generator:
   ```bash
   python generate_samples.py
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Embedding a Message**:
   - Click **Load Audio** and select a `.wav` file.
   - Type your secret message in the text box.
   - Click **Embed Message** and choose a location to save the new audio file.

4. **Extracting a Message**:
   - Click **Load Stego Audio** and select the file containing the hidden message.
   - Click **Extract Message** to view the hidden text.

## Project Structure
- `main.py`: Entry point of the application.
- `gui.py`: GUI implementation using PyQt5.
- `steganography.py`: Core logic for FFT embedding and extraction.
- `generate_samples.py`: Helper script to generate test audio files.
- `verify.py`: Script to verify embedding/extraction integrity.
