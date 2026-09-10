"""Compare the Python and C MFCC implementations on the same file.

Build the C side first:
    gcc -o src/mfcc/c_impl/mfcc_test src/mfcc/c_impl/*.c -lm

It should take a WAV path and print 49 lines of 10 numbers.

    python src/mfcc/parity_test.py test-data/test_audio.wav
"""

import subprocess
import sys

import numpy as np
from python_speech_features import mfcc
from scipy.io import wavfile

RATE = 16000
WIN = 0.030
HOP = 0.020
NCEP = 10
NFRAMES = 49

C_BIN = "src/mfcc/c_impl/mfcc_test"
MEAN_LIMIT = 2.0
MAX_LIMIT = 10.0


def from_python(path):
    rate, sig = wavfile.read(path)
    if rate != RATE:
        sys.exit(f"{path} is {rate} Hz, expected {RATE}")
    if sig.ndim > 1:
        sys.exit(f"{path} is not mono")
    return mfcc(sig, RATE, winlen=WIN, winstep=HOP, numcep=NCEP, preemph=0.97)[:NFRAMES]


def from_c(path):
    try:
        out = subprocess.run([C_BIN, path], capture_output=True, text=True,
                             check=True).stdout
    except FileNotFoundError:
        sys.exit(f"{C_BIN} not built")
    except subprocess.CalledProcessError as e:
        sys.exit(f"{C_BIN} exited {e.returncode}\n{e.stderr}")
    return np.array([l.split() for l in out.split("\n") if l.strip()], dtype=float)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "test-data/test_audio.wav"
    py, c = from_python(path), from_c(path)

    if py.shape != c.shape:
        sys.exit(f"shape mismatch: python {py.shape}, c {c.shape}")

    diff = np.abs(py - c) / np.maximum(np.abs(py), 1e-6) * 100
    frame, coef = np.unravel_index(diff.argmax(), diff.shape)

    print(f"{path}  {py.shape}")
    print(f"mean {diff.mean():.2f}%   worst {diff.max():.2f}% at frame {frame}, coef {coef}")

    for i in range(3):
        print(f"\nframe {i}")
        print("  py", " ".join(f"{v:7.2f}" for v in py[i]))
        print("  c ", " ".join(f"{v:7.2f}" for v in c[i]))

    if diff.mean() <= MEAN_LIMIT and diff.max() <= MAX_LIMIT:
        print("\npass")
        return 0

    print("\nfail")
    print("check: preemph, window function, mel filter count, Q15 shifts, DCT scaling")
    return 1


if __name__ == "__main__":
    sys.exit(main())
