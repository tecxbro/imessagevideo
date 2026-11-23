"""Synthesize the two measured chimes and mux the saved picture replay."""
import argparse
from array import array
import math
from pathlib import Path
import subprocess
import sys
import wave


def make_sound(destination):
    rate = 48000
    samples = array("h", [0]) * (3 * rate)
    cues = [(34, 523.25, 0.15, 0.273), (61, 783.99, 0.30, 0.365)]
    for frame, frequency, duration, amplitude in cues:
        start = round(frame * rate / 30)
        for i in range(round(duration * rate)):
            t = i / rate
            gain = min(1, t / 0.012, (duration - t) / 0.018) * math.exp(-12 * t)
            samples[start + i] = round(32767 * amplitude * gain * math.sin(2 * math.pi * frequency * t))
    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(str(destination), "wb") as out:
        out.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        out.writeframes(samples.tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("picture", type=Path)
    parser.add_argument("stem", type=Path)
    parser.add_argument("master", type=Path)
    args = parser.parse_args()
    make_sound(args.stem)
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(args.picture), "-i", str(args.stem),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(args.master),
    ], check=True)
