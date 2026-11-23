"""Original paper taps and a sparse pitched score for the Pinch Hit trial."""
import argparse
from pathlib import Path
import wave

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    rate = 48_000
    track = np.zeros((rate * 20, 2))
    random = np.random.default_rng(18)

    def place(seconds, signal, pan):
        start = round(seconds * rate)
        track[start:start+len(signal)] += signal[:, None] * [1-pan, pan]

    for start, pitch, pan in [
        (.26, 130.81, .4), (4.72, 164.81, .55), (5.76, 196, .44),
        (9.22, 146.83, .6), (10.94, 220, .52), (13.76, 261.63, .42),
        (15.04, 329.63, .6), (17.72, 392, .48),
    ]:
        t = np.arange(round(rate * 1.24)) / rate
        fade = np.minimum(1, t / .015) * np.minimum(1, (t[-1]-t) / .12)
        note = (np.sin(2*np.pi*pitch*t) + .12*np.sin(4*np.pi*pitch*t)) * np.exp(-t*4) * .12
        place(start, note * fade, pan)
        tap = random.standard_normal(480) * np.hanning(480) * .017
        place(start, tap, pan)

    output = args.project / "assets" / "score.wav"
    with wave.open(str(output), "wb") as file:
        file.setparams((2, 2, rate, 0, "NONE", "not compressed"))
        file.writeframes(np.round(track * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    main()
