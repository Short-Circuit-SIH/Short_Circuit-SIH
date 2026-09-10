# Kalpana

Custom wake word detection on an ESP32-S3. Says nothing to the network until it hears the word.

## 1. Project Information

- **Project Title:** Kalpana – Low Latency and Efficient Voice Activator for Edge Devices
- **PS ID:** SIH26172
- **PS Title:** Low Latency and Efficient Voice Activator for Edge Devices
- **Category:** Hardware
- **Theme:** Miscellaneous
- **Organisation:** ISRO
- **Team:** Short Circuit, NSUT

## 2. Problem Statement

Most voice assistants send audio to a server before deciding whether the user was even talking to them. That needs a network connection, adds delay, and means audio leaves the device before anything has filtered it.

Edge devices in the field often have neither reliable connectivity nor the compute for a full speech model. What they need is a small always-on component that recognises one activation word locally, in very little memory, using almost no CPU while idle.

The PS sets the limits: under 256 KB RAM, under 10% idle CPU, open-source frameworks, and a custom keyword rather than a stock wake word.

## 3. Proposed Solution

Kalpana runs keyword spotting entirely on an ESP32-S3 with an INMP441 microphone.

Audio is captured over I2S into a ring buffer. Every 200 ms the last second is converted to MFCC features and run through a quantised INT8 network that labels it keyword, unknown, or silence. Nothing leaves the board during this.

When "Kalpana" is detected the device opens a TCP connection and streams the audio that follows to a laptop, starting 500 ms before the detection point so the sentence isn't clipped. Vosk transcribes it offline.

The large speech model only runs when it is actually needed. The part that runs all the time stays inside the memory and CPU budget.

## 4. Key Features

- Keyword trained on our own recordings, not a stock wake word
- Detection runs offline on the microcontroller
- INT8 model under 64 KB
- Fixed-point MFCC on device, checked against a Python reference
- 500 ms pre-roll so the streamed audio includes the start of the sentence
- Framed TCP stream that can detect and recover from byte misalignment
- Offline ASR on the receiving machine

## 5. Technology Stack

- ESP32-S3, dual core 240 MHz
- INMP441 I2S MEMS microphone
- C/C++, Arduino core for ESP32, FreeRTOS
- TensorFlow Lite for Microcontrollers with ESP-NN
- ESP-DSP for FFT
- Python, TensorFlow/Keras for training
- Vosk for offline speech recognition

## 6. Architecture

```
INMP441
  |  I2S, 16 kHz mono
Ring buffer (2 s, 500 ms pre-roll)
  |  last 1 s, every 200 ms
MFCC  ->  49 x 10, fixed point
  |
INT8 model  ->  keyword / unknown / silence
  |
  |  keyword
TCP stream over Wi-Fi
  |
Laptop  ->  Vosk  ->  text
```

More detail in [docs/architecture.md](docs/architecture.md). Wiring and board settings in [docs/hardware.md](docs/hardware.md).

## 7. Repository Structure

```
SIH-Kalpana/
├── README.md
├── SUBMISSION_GUIDE.md
├── submission/
│   ├── PRESENTATION.md
│   └── DEMO.md
├── src/
│   ├── firmware/       ESP32 code
│   ├── mfcc/           feature extraction, Python and C
│   ├── model/          training and quantisation
│   ├── server/         TCP server and Vosk
│   └── measurements/   benchmark scripts
├── docs/
├── assets/screenshots/
├── test-data/
├── requirements.txt
├── .gitignore
└── LICENSE
```

### What goes where?

| Item | Location |
|---|---|
| Source code | `src/` |
| Technical documentation | `docs/` |
| Prototype photos | `assets/screenshots/` |
| Final PPT | `submission/` |
| Demo video link | `submission/DEMO.md` |

Voice recordings are not in this repo. They are on the team drive. Only the final model is committed.

## 8. Final Presentation

See [submission/PRESENTATION.md](submission/PRESENTATION.md).

## 9. Demo Video

See [submission/DEMO.md](submission/DEMO.md).

## 10. Screenshots / Prototype Photos

In [assets/screenshots/](assets/screenshots/).

## 11. Installation

```
git clone https://github.com/Short-Circuit-SIH/SIH-Kalpana
cd SIH-Kalpana
pip install -r requirements.txt
```

Download `vosk-model-small-en-us-0.15` from https://alphacephei.com/vosk/models and unzip it into `src/server/`. It is not committed, it is around 50 MB.

For firmware, install the ESP32 board package in the Arduino IDE. Board is ESP32S3 Dev Module, partition scheme No OTA (2MB APP / 2MB SPIFFS).

Copy `src/firmware/config.example.h` to `config.h` and fill in your Wi-Fi and server IP.

## 12. Run

Start the server:

```
python src/server/server.py
```

Flash `src/firmware/` and power the board.

Check that the device and reference feature extraction agree:

```
python src/mfcc/parity_test.py test-data/test_audio.wav
```

Retrain:

```
python src/model/train.py
```

## 13. Future Scope

- Move MFCC into an FPGA block, then towards a dedicated low power KWS ASIC
- Multi-condition training for noisier environments
- Deep sleep with wake-on-sound for battery operation
- More than one keyword, small on-device command set
- Custom PCB with the microphone and power management integrated

## 14. Team

| Member | Area |
|---|---|
| Rachit Mittal | Integration, firmware architecture |
| Devansh Nagar | Audio capture, I2S, buffering |
| Anshika Arpan | Feature extraction, Python and fixed-point C |
| Anmol Aggarwal | Model training and quantisation |
| Ridha Kansal | Networking and speech recognition |
| Saksham Mittal | Dataset, benchmarking, documentation |

## Important

Do not commit Wi-Fi credentials, API keys, tokens, or `.env` files. Wi-Fi settings belong in `src/firmware/config.h`, which is gitignored.
