"""Independent authored benchmark input. Keep this oracle out of builder view."""
import argparse
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


WIDTH, HEIGHT, FPS, LENGTH = 480, 270, 30, 90
SAMPLE_RATE = 48000
FIXED = (107, 176)


def smoothstep(frame, start, stop):
    t = min(1, max(0, (frame - start) / (stop - start)))
    return t * t * (3 - 2 * t)


def shuttle(frame):
    return (173 + 196 * smoothstep(frame, 14, 34),
            176 - 88 * smoothstep(frame, 41, 61))


def picture(frame):
    scale = 2
    canvas = Image.new("RGB", (WIDTH * scale, HEIGHT * scale), "#141a29")
    paint = ImageDraw.Draw(canvas)

    def coords(points):
        return tuple(round(coordinate * scale) for coordinate in points)

    def rect(box, fill, radius=0):
        paint.rounded_rectangle(coords(box), radius * scale, fill=fill)

    def dot(x, y, radius, fill):
        paint.ellipse(coords((x - radius, y - radius, x + radius, y + radius)), fill=fill)

    rect((38, 37, 442, 231), "#202b42", 18)
    rect((54, 56, 96, 61), "#4be0bd", 2)
    rect((104, 56, 131, 61), "#405677", 2)
    rect((54, 211, 426, 212), "#405677")
    dot(369, 88, 19, "#3f4b69")
    dot(369, 88, 14, "#202b42")
    x, y = shuttle(frame)
    x0, y0 = FIXED
    angle = math.atan2(y - y0, x - x0)
    fx, fy = -math.sin(angle) * 3, math.cos(angle) * 3
    paint.polygon([coords(pt) for pt in ((x0 + fx, y0 + fy), (x0 - fx, y0 - fy),
                                          (x - fx, y - fy), (x + fx, y + fy))], fill="#68a9ed")
    dot(x0, y0, 11, "#4be0bd")
    dot(x0, y0, 4, "#202b42")
    rect((x - 18, y - 12, x + 18, y + 12), "#ed93ff", 9)
    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def soundtrack(path):
    result = np.zeros(LENGTH * SAMPLE_RATE // FPS)
    for frame, frequency, duration, gain in ((34, 523.25, .15, .28), (61, 783.99, .3, .38)):
        length = round(duration * SAMPLE_RATE)
        time = np.arange(length) / SAMPLE_RATE
        envelope = np.minimum(time / .012, 1) * np.exp(-12 * time) * np.minimum((duration - time) / .02, 1)
        start = frame * SAMPLE_RATE // FPS
        result[start:start + length] = gain * envelope * np.sin(2 * np.pi * frequency * time)
    with wave.open(str(path), "wb") as audio:
        audio.setparams((1, 2, SAMPLE_RATE, len(result), "NONE", "not compressed"))
        audio.writeframes(np.int16(result * 32767).astype("<i2").tobytes())


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("output", type=Path)
    output = args.parse_args().output
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as scratch:
        wav = Path(scratch) / "original.wav"
        soundtrack(wav)
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
                   "-s", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS), "-i", "pipe:0", "-i", str(wav),
                   "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "aac",
                   "-b:a", "128k", "-movflags", "+faststart", str(output)]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as encode:
            for frame in range(LENGTH):
                encode.stdin.write(picture(frame).tobytes())
            encode.stdin.close()
            if encode.wait():
                raise RuntimeError("Could not encode the unseen reference")


if __name__ == "__main__":
    main()
