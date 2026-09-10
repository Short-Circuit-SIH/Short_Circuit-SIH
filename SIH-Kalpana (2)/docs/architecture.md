# Architecture

The system splits the work between a microcontroller and a laptop. The microcontroller can run continuously on very little power but cannot understand sentences. The laptop can, but should not be involved until it has to be. So: keyword detection on the device, speech recognition off it.

```
INMP441
  |  I2S, 16 kHz, 16-bit mono
Audio capture
  |
Ring buffer, 2 s, 500 ms pre-roll kept
  |  last 1 s, every 200 ms
MFCC, 49 frames x 10 coefficients, fixed point
  |
INT8 model  ->  keyword / unknown / silence
  |
  |  keyword, agreed across 3 consecutive windows
TCP stream, raw PCM, 0xA5A5 + 4 byte length framing
  |  Wi-Fi
Laptop server
  |
Vosk
  |
text
```

## Capture

The INMP441 is a digital microphone, so there is no ADC or amplifier in the path. The ESP32 reads it over I2S using DMA. The microphone sends 32-bit slots of which only part carries signal; converting to 16-bit is a right shift by 11.

## Ring buffer

Audio arrives at 32 KB/s and cannot all be kept. A circular buffer holds the most recent 2 seconds, with new samples overwriting the oldest. The last second is therefore always available for inference at fixed memory cost and one write per sample. Shifting an array instead would cost roughly 256 million operations a second, which is not possible inside the CPU budget.

The buffer also keeps 500 ms of history, which matters at the streaming stage.

## Features

A small classifier does badly on raw samples. Each 1-second window is cut into 30 ms frames with a 20 ms hop, giving 49 frames, and each frame is reduced to 10 MFCC coefficients. The 49x10 result is roughly consistent across repeated utterances of the same word, so the problem becomes pattern matching on a small image.

The device version uses fixed-point arithmetic because floating point is too slow here. A Python version is kept alongside it for training, and `src/mfcc/parity_test.py` checks the two against each other on the same file. If they disagree the model trains on one kind of input and gets fed another: high accuracy in training, poor accuracy on hardware, and no error raised anywhere. That is why the check exists.

## Inference

A small convolutional network, quantised to INT8, classifies each window. Detection is only accepted when three consecutive windows agree, which removes most single-frame false triggers. The threshold is set high, trading a few more missed detections for considerably fewer false ones.

## Streaming

Streaming starts 500 ms before the detection point, pulled from the ring buffer. By the time inference fires, the keyword and part of what follows has already gone past — inference takes about 100 ms and the word itself around 800 ms. Without the rewind the server receives the sentence with its beginning missing.

Each chunk is preceded by `0xA5A5` and a 4-byte length. TCP keeps order and completeness but not chunk boundaries, and samples are 2 bytes wide, so a reader starting on an odd byte rebuilds every sample from halves of two different values. The result is noise, with nothing to indicate a fault. The marker lets the server detect that and resynchronise.

## Recognition

Vosk takes audio incrementally and can return partial results before the utterance finishes. It runs offline, so there is no cloud dependency and no network requirement beyond the local link.

## Memory

The 256 KB budget is internal SRAM. The board has 8 MB of PSRAM, which is external. The tensor arena, ring buffer and audio buffers are kept in internal SRAM on purpose, and memory is reported as internal SRAM rather than total heap.

| | Approx |
|---|---|
| Ring buffer, 2 s | 64 KB |
| Model | under 64 KB |
| Tensor arena | 60 KB |
| MFCC scratch | 8 KB |
