# Hardware

## Parts

| Component | Part |
|---|---|
| Microcontroller | ESP32-S3 DevKitC-1 (N8R8) |
| Microphone | INMP441 |
| Prototyping | 830-point breadboard, jumper wires |
| Cable | USB-C, must carry data |

The S3 was chosen over the classic ESP32 because ESP-NN uses its vector instructions, which the older LX6 core does not have. Inference comes out roughly 3-4x faster, and that margin is what makes the idle CPU target comfortable rather than marginal.

## Wiring

| INMP441 | ESP32-S3 |
|---|---|
| VDD | 3.3 V |
| GND | GND |
| SCK | GPIO, bit clock |
| WS | GPIO, word select |
| SD | GPIO, data |
| L/R | GND, selects left channel |

3.3 V only. 5 V destroys the module.

Pin order on the header differs between manufacturers, so read the silkscreen rather than copying a photo from a tutorial. The sound port is on the underside, so do not mount it flat against the breadboard.

## Audio settings

| | |
|---|---|
| Sample rate | 16 kHz |
| Format | 16-bit signed |
| Channels | mono |
| I2S slot | 32-bit |
| Shift to 16-bit | right by 11 |

## Arduino IDE

- Board: ESP32S3 Dev Module
- Partition Scheme: No OTA (2MB APP / 2MB SPIFFS)

If the board has two USB-C ports, flash through the UART one.

## Known issues

**Recording silent or very faint.** The INMP441 sends 32-bit slots and shifting right by 16 throws away nearly all the signal. Shift by 11.

**Sketch too large.** Change the partition scheme as above. This appears once the model is added.

**No serial port.** Either the USB cable is charge-only, or the board is plugged into its native USB port instead of UART. Test the cable by connecting a phone and checking whether file transfer is offered.

**Works, then doesn't, then works again.** Usually a loose jumper on the I2S clock line. Swap the jumpers before looking at the code.

**Detection succeeds intermittently, no crash.** If MFCC takes longer than the 200 ms stride, the buffer writer overtakes the reader and the analysis window ends up as two spliced fragments. Copy the window into a scratch array before processing, and log the gap between the read and write pointers.
