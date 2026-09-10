# Kalpana – Low Latency Edge Voice Activator

## 1. Project Information

- **Project Title:** Kalpana – Low Latency and Efficient Voice Activator for Edge Devices
- **PS ID:** SIH26172
- **PS Title:** Low Latency and Efficient Voice Activator for Edge Devices
- **Category:** Hardware
- **Theme:** Miscellaneous
- **Organisation:** ISRO

## 2. Problem Statement

Voice assistants on most consumer devices send audio to the cloud before they can decide whether the user was speaking to them at all. This introduces network latency, requires constant connectivity, and raises privacy concerns because audio leaves the device before any filtering has taken place.

Edge devices used in field and mission settings often have neither reliable connectivity nor the compute budget to run a full speech model. What they need is a small always-listening component that can recognise a single custom activation word locally, using very little memory and almost no CPU while idle, and only then involve the network.

The constraints set by the problem statement are under 256 KB of RAM, under 10% CPU utilisation while idle, open-source ML and TinyML frameworks only, and a custom keyword rather than a generic pre-trained wake word.

## 3. Proposed Solution

Kalpana is a custom keyword spotting system that runs entirely on an ESP32-S3 microcontroller with an INMP441 digital microphone.

Audio is captured continuously over I2S into a small ring buffer. Every 200 ms the most recent one second of audio is converted into MFCC features and passed to a quantised INT8 neural network, which classifies the window as the keyword, unknown speech, or silence. All of this happens on the device, offline, with no audio leaving the board.

When the keyword "Kalpana" is detected, the device opens a TCP connection and streams the audio that follows to a laptop, including 500 ms retained from before the detection fired so the sentence is not clipped at the start. On the laptop, Vosk performs offline speech recognition and returns the transcribed text.

The heavy speech model therefore runs only when it is actually needed, and the always-on component stays inside the memory and CPU budget.

## 4. Key Features

- Custom keyword detection trained on our own recorded dataset, not a pre-trained wake word
- Fully offline keyword detection on the microcontroller, with no audio sent to any server before detection
- INT8 quantised model under 64 KB, running within the 256 KB RAM budget
- Fixed-point MFCC feature extraction on the device, validated against a Python reference implementation
- 500 ms pre-roll buffer so the streamed audio includes the start of the utterance
- Framed TCP audio streaming that detects and recovers from byte misalignment
- Offline speech recognition on the receiving machine, with no cloud dependency
- Measured RAM, idle CPU, latency, accuracy and false-activation rate

## 5. Technology Stack

- Microcontroller: ESP32-S3 (dual-core, 240 MHz)
- Microphone: INMP441 I2S digital MEMS microphone
- Firmware: C / C++, Arduino core for ESP32, FreeRTOS
- On-device inference: TensorFlow Lite for Microcontrollers with ESP-NN
- Signal processing: fixed-point MFCC, ESP-DSP for FFT
- Model training: Python, TensorFlow / Keras, NumPy
- Speech recognition: Vosk (offline)
- Networking: TCP over Wi-Fi, raw PCM audio

## 6. Architecture

See [docs/architecture.md](docs/architecture.md).
Interface values shared across modules are recorded in [docs/interface-contract.md](docs/interface-contract.md).

```
INMP441 Microphone
  |
  v  I2S
Audio Capture (16 kHz, 16-bit mono)
  |
  v
Ring Buffer (1.5-2 s, 500 ms pre-roll)
  |
  v
MFCC Feature Extraction (49 x 10, fixed-point)
  |
  v
INT8 Keyword Model (keyword / unknown / silence)
  |
  +----> not keyword: discard, keep listening
  |
  v  keyword detected
TCP Audio Stream over Wi-Fi
  |
  v
Laptop Server
  |
  v
Vosk Offline ASR
  |
  v
Transcribed Text
```

## 7. Repository Structure

```
SIH-Kalpana/
├── README.md
├── SUBMISSION_GUIDE.md
├── submission/
│   ├── PRESENTATION.md
│   └── DEMO.md
├── src/
│   ├── firmware/          ESP32 firmware: capture, buffer, inference
│   ├── mfcc/              Python reference and fixed-point C feature extraction
│   ├── model/             Training, augmentation and quantisation scripts
│   ├── server/            TCP audio server and Vosk transcription
│   └── measurements/      Benchmark scripts for RAM, CPU, latency, accuracy
├── docs/
│   ├── architecture.md
│   ├── interface-contract.md
│   └── hardware.md
├── assets/
│   └── screenshots/
├── test-data/
├── requirements.txt
├── .gitignore
└── LICENSE
```

### What goes where?

| Item | Location |
|---|---|
| Firmware and Python source | `src/` |
| Architecture and technical documentation | `docs/` |
| Wiring diagram and hardware notes | `docs/hardware.md` |
| Prototype photos and screenshots | `assets/screenshots/` |
| Final PPT / presentation | `submission/` |
| Demo video link | `submission/DEMO.md` |
| Project overview | `README.md` |

Recorded voice datasets are not committed to this repository. They are held in the team's shared drive folder. Only the final quantised model is committed.

## 8. Final Presentation

The final SIH presentation is kept in `submission/`.

See [submission/PRESENTATION.md](submission/PRESENTATION.md) for the format and the accessible viewer link.

## 9. Demo Video

The demo video link is in [submission/DEMO.md](submission/DEMO.md).

It shows the device detecting the keyword offline and the transcribed text appearing on the receiving machine.

## 10. Screenshots / Prototype Photos

Hardware photos, captured waveforms and transcription output are in:

`assets/screenshots/`

## 11. Installation

```
git clone <YOUR_REPOSITORY_URL>
cd SIH-Kalpana
pip install -r requirements.txt
```

Download the Vosk model `vosk-model-small-en-us-0.15` from https://alphacephei.com/vosk/models and unzip it into `src/server/`. It is not committed because of its size.

For the firmware, install the ESP32 board package in the Arduino IDE, select **ESP32S3 Dev Module**, and set Partition Scheme to **No OTA (2MB APP / 2MB SPIFFS)**.

## 12. Run

Start the receiving server on the laptop:

```
python src/server/server.py
```

Then flash the firmware in `src/firmware/` to the ESP32-S3 and power the board. Set the server IP address at the top of the firmware to match the laptop before flashing.

To verify that the on-device and reference feature extraction agree:

```
python src/mfcc/parity_test.py test-data/test_audio.wav
```

To retrain the model:

```
python src/model/train.py
```

## 13. Future Scope

- Offload the MFCC computation to an FPGA or a custom digital block, which would reduce CPU load further and is the natural path towards a dedicated low-power keyword spotting ASIC
- Improve noise robustness with multi-condition training and a wider range of recording environments
- Add deep sleep and wake-on-sound so the device can run on battery for extended periods
- Support multiple keywords and a small command vocabulary on the device
- Move the design to a custom PCB with an integrated microphone and power management
- Extend the dataset across more speakers, accents and languages

## Important

Before submission, make sure the repository is accessible to reviewers. Do **not** upload passwords, API keys, access tokens, `.env` files containing secrets, or other confidential credentials.

Wi-Fi credentials must not be committed. Keep them in a local configuration file that is listed in `.gitignore`.
