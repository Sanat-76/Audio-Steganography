import numpy as np
from scipy.io import wavfile
from scipy.fft import fft, ifft

class FFTSteganography:
    def __init__(self, frame_size=1024, freq_range=(100, 300), step=0.1):
        """
        Initialize the steganography engine.
        :param frame_size: Size of FFT frames.
        :param freq_range: Range of frequency bins (mid-frequencies) to use for embedding.
        :param step: Magnitude quantization step for embedding.
        """
        self.frame_size = frame_size
        self.freq_range = freq_range
        self.step = step
        self.terminator = "###END###"

    def _text_to_bits(self, text):
        bits = []
        for char in text:
            bin_val = bin(ord(char))[2:].zfill(8)
            bits.extend([int(b) for b in bin_val])
        return bits

    def _bits_to_text(self, bits):
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8:
                break
            char_code = int("".join(map(str, byte)), 2)
            chars.append(chr(char_code))
        return "".join(chars)

    def embed(self, input_path, message, output_path):
        """
        Embed message into audio file.
        """
        sample_rate, data = wavfile.read(input_path)
        
        # Convert to mono float64
        if len(data.shape) > 1:
            audio = data.mean(axis=1).astype(np.float64)
        else:
            audio = data.astype(np.float64)

        # Normalize to [-1, 1] if it was 16-bit PCM
        if data.dtype == np.int16:
            audio /= 32768.0

        message_with_term = message + self.terminator
        bits = self._text_to_bits(message_with_term)
        bit_idx = 0
        total_bits = len(bits)

        num_frames = len(audio) // self.frame_size
        stego_audio = np.zeros_like(audio)

        for i in range(num_frames):
            frame = audio[i * self.frame_size : (i + 1) * self.frame_size]
            
            # FFT
            f_transform = fft(frame)
            magnitudes = np.abs(f_transform)
            phases = np.angle(f_transform)

            # Embed bits into magnitude
            # Use only freq_range to avoid audible distortion in lows/highs
            for freq in range(self.freq_range[0], self.freq_range[1]):
                if bit_idx < total_bits:
                    bit = bits[bit_idx]
                    
                    # QIM (Quantization Index Modulation) on magnitude
                    # magnitude' = round(magnitude / step) * step
                    # If bit is 1, shift by step/2
                    m = magnitudes[freq]
                    q = np.floor(m / self.step)
                    
                    if bit == 1:
                        if q % 2 == 0:
                            magnitudes[freq] = (q + 1) * self.step
                        else:
                            magnitudes[freq] = q * self.step
                    else:
                        if q % 2 == 1:
                            magnitudes[freq] = (q + 1) * self.step
                        else:
                            magnitudes[freq] = q * self.step
                    
                    # Also update the symmetric component for real FFT result
                    magnitudes[self.frame_size - freq] = magnitudes[freq]
                    
                    bit_idx += 1

            # Reconstruct frame
            new_f_transform = magnitudes * np.exp(1j * phases)
            stego_frame = np.real(ifft(new_f_transform))
            stego_audio[i * self.frame_size : (i + 1) * self.frame_size] = stego_frame

        if bit_idx < total_bits:
            raise ValueError(f"Message too long for the given audio. Embedded {bit_idx}/{total_bits} bits.")

        # Convert back to 16-bit PCM
        # Clip to avoid overflow
        stego_audio = np.clip(stego_audio, -1, 1)
        stego_audio_int = (stego_audio * 32767).astype(np.int16)
        
        wavfile.write(output_path, sample_rate, stego_audio_int)
        return True

    def extract(self, stego_path):
        """
        Extract message from audio file.
        """
        sample_rate, data = wavfile.read(stego_path)
        
        # Audio is likely already mono from our process, but handle just in case
        if len(data.shape) > 1:
            audio = data.mean(axis=1).astype(np.float64)
        else:
            audio = data.astype(np.float64)

        if data.dtype == np.int16:
            audio /= 32768.0

        bits = []
        num_frames = len(audio) // self.frame_size

        for i in range(num_frames):
            frame = audio[i * self.frame_size : (i + 1) * self.frame_size]
            f_transform = fft(frame)
            magnitudes = np.abs(f_transform)

            for freq in range(self.freq_range[0], self.freq_range[1]):
                m = magnitudes[freq]
                q = np.round(m / self.step)
                bits.append(int(q % 2))

            # Partial extraction check for terminator
            # Check every frame for efficiency
            current_text = self._bits_to_text(bits)
            if self.terminator in current_text:
                return current_text.split(self.terminator)[0]

        return "Terminator not found. Extraction may be incomplete."

if __name__ == "__main__":
    # Quick test
    import os
    
    # Create a dummy silent wav for testing if needed
    fs = 44100
    t = 2.0
    samples = np.zeros(int(fs * t))
    wavfile.write("test_init.wav", fs, (samples * 32767).astype(np.int16))
    
    engine = FFTSteganography()
    msg = "Hello Stego World!"
    engine.embed("test_init.wav", msg, "stego.wav")
    extracted = engine.extract("stego.wav")
    
    print(f"Original: {msg}")
    print(f"Extracted: {extracted}")
    
    if os.path.exists("test_init.wav"): os.remove("test_init.wav")
    if os.path.exists("stego.wav"): os.remove("stego.wav")
