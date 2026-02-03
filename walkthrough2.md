# Audio Steganography: Core Processes

This document provides a visual representation of how the FFT-based audio steganography system embeds and extracts messages.

## 1. Embedding Process

The embedding process uses **Quantization Index Modulation (QIM)** in the frequency domain.

```mermaid
graph TD
    A["Input Audio File"] --> B["Read WAV & Convert to Mono"]
    B --> C["Normalize Audio Samples"]
    D["Secret Message"] --> E["Add Terminator & Convert to Bits"]
    C --> F["Divide Audio into Frames"]
    E --> G["Process Each Frame"]
    F --> G
    
    subgraph "Per Frame Processing"
        G --> H["Fast Fourier Transform (FFT)"]
        H --> I["Get Magnitudes & Phases"]
        I --> J["Modify Magnitudes using QIM"]
        J --> K["Symmetric Update for Real FFT"]
        K --> L["Inverse FFT (IFFT)"]
    end
    
    L --> M["Reconstruct Stego Audio"]
    M --> N["Clip & Convert to 16-bit PCM"]
    N --> O["Save Stego WAV File"]
```

---

## 2. Extraction Process

The extraction process reverses the quantization to retrieve the bitstream.

```mermaid
graph TD
    A["Stego Audio File"] --> B["Read WAV & Convert to Mono"]
    B --> C["Divide Audio into Frames"]
    C --> D["Process Each Frame"]
    
    subgraph "Per Frame Extraction"
        D --> E["Fast Fourier Transform (FFT)"]
        E --> F["Get Magnitudes"]
        F --> G["Check Bin Magnitudes"]
        G --> H["Quantize Magnitude / Step"]
        H --> I["Extract Bit: Q % 2"]
    end
    
    I --> J["Append Bits to Buffer"]
    J --> K["Convert Bits to Text"]
    K --> L{"Terminator Found?"}
    L -- "Yes" --> M["Stop & Return Message"]
    L -- "No" --> D
    
    M --> N["Final Secret Message"]
```

## Key Technologies
- **FFT (Fast Fourier Transform):** Transitions audio from time domain to frequency domain.
- **QIM (Quantization Index Modulation):** Encodes bits by forcing frequency magnitudes to even or odd multiples of a quantization step.
- **Complexity:** Minimal audible distortion by targeting mid-range frequencies.
