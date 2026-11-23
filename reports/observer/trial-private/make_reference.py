import functools
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT, FPS, FRAMES = 720, 900, 30, 420
RATE = 48000
LINE = "#6d7974"
BACK = "#dbebdd"
DARK = "#20372c"
BLUE = "#0878ff"
HIGHLIGHT = "#ffcb6e"
CUES = ((78, 510), (113, 700), (162, 850), (218, 420), (247, 610), (312, 760), (368, 550))


@functools.cache
def face(size, bold=False):
    return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=1 if bold else 0)


def ease(frame, start, end):
    progress = min(1, max(0, (frame - start) / (end - start)))
    return progress * progress * (3 - 2 * progress)


def label(draw, point, copy, size, fill=DARK, anchor="lt", bold=False):
    draw.text(point, copy, font=face(size, bold), fill=fill, anchor=anchor)


def bubble(draw, y, copy, outgoing=False):
    left, right = (161, 369) if outgoing else (20, 319)
    fill = BLUE if outgoing else "#e9eeeb"
    draw.rounded_rectangle((left, y, right, y + 43), 18, fill=fill)
    tip = right + 5 if outgoing else left - 5
    root = right - 12 if outgoing else left + 12
    draw.polygon([(root, y + 28), (tip, y + 42), (root, y + 40)], fill=fill)
    label(draw, (left + 14, y + 11), copy, 19, "white" if outgoing else DARK)


def ticket(draw, x, y, night=False, selected=False):
    fill = "#c7daff" if night else "#ffe4a9"
    draw.rounded_rectangle((x, y, x + 258, y + 138), 19, fill=fill)
    draw.ellipse((x + 173, y + 12, x + 232, y + 70), fill="#eaf7ff" if night else "#f4a046")
    if night:
        draw.ellipse((x + 183, y + 5, x + 237, y + 60), fill=fill)
        draw.line([(x + 166, y + 33), (x + 166, y + 53)], fill=DARK, width=2)
        draw.line([(x + 156, y + 43), (x + 176, y + 43)], fill=DARK, width=2)
    label(draw, (x + 15, y + 16), "FIELD NOTES", 12)
    label(draw, (x + 15, y + 37), "Twilight walk" if night else "Dawn walk", 26, bold=True)
    label(draw, (x + 15, y + 73), "7:10 PM · North Gate" if night else "6:20 AM · East Gate", 16)
    draw.line((x + 14, y + 98, x + 242, y + 98), fill="#69777e")
    label(draw, (x + 15, y + 111), "SELECTED" if selected else "VIEW PASS", 13)
    if selected:
        draw.ellipse((x + 218, y + 105, x + 241, y + 128), fill=BLUE)
        draw.line([(x + 223, y + 116), (x + 228, y + 121), (x + 236, y + 111)], width=2, fill="white")


@functools.cache
def mask():
    screen = Image.new("L", (392, 652))
    ImageDraw.Draw(screen).rounded_rectangle((0, 0, 391, 651), radius=44, fill=255)
    return screen


def phone(frame):
    device = Image.new("RGBA", (416, 676))
    ImageDraw.Draw(device).rounded_rectangle((0, 0, 415, 675), 54, fill="#1c2625")
    screen = Image.new("RGB", (392, 652), "#fcfdfc")
    draw = ImageDraw.Draw(screen)
    if frame < 270:
        if frame >= 78:
            bubble(draw, 130, "Any walks after work?", True)
        if 88 <= frame < 113:
            for index in range(3):
                shade = "#81948b" if (frame // 4) % 3 == index else "#bbc9c0"
                draw.ellipse((31 + index * 14, 197, 39 + index * 14, 205), fill=shade)
        if frame >= 113:
            bubble(draw, 180, "Two options for Friday.")
            shift = round(276 * ease(frame, 186, 218))
            arrival = round(307 * (1 - ease(frame, 116, 139)))
            if frame < 218:
                ticket(draw, 38 - shift - arrival, 248)
            if frame > 186:
                ticket(draw, 314 - shift, 248, night=True, selected=frame >= 247)
            if 162 <= frame < 218:
                reaction_x = 269 - shift
                draw.ellipse((reaction_x - 16, 228, reaction_x + 16, 260), fill=HIGHLIGHT)
                draw.polygon([(reaction_x, 250), (reaction_x - 9, 240), (reaction_x - 4, 235),
                              (reaction_x, 239), (reaction_x + 4, 235), (reaction_x + 9, 240)], fill="#b64867")
            for index in range(2):
                dot = BLUE if index == int(frame >= 218) else "#c4cfca"
                draw.ellipse((182 + index * 16, 410, 189 + index * 16, 417), fill=dot)
    else:
        bubble(draw, 130, "Twilight walk, please.", True)
        if frame >= 312:
            rise = round(14 * (1 - ease(frame, 311, 322)))
            bubble(draw, 183 + rise, "Saved. Meet at North Gate.")
            ticket(draw, 24, 250 + rise, night=True, selected=True)
    draw.rectangle((0, 0, 392, 108), fill="#f3f8f4")
    draw.rounded_rectangle((166, 11, 226, 23), 6, fill="#1c2625")
    draw.ellipse((179, 33, 212, 66), fill="#357559")
    label(draw, (196, 50), "F", 17, "white", "mm", True)
    label(draw, (196, 81), "Field Notes", 21, DARK, "mm", True)
    draw.line((0, 108, 392, 108), fill="#d6e1d7", width=2)
    draw.rounded_rectangle((48, 590, 367, 627), 17, outline="#b7c6bc", width=2)
    label(draw, (62, 601), "iMessage", 16, LINE)
    draw.line((24, 599, 24, 617), fill=LINE, width=2)
    draw.line((15, 608, 33, 608), fill=LINE, width=2)
    device.paste(screen, (12, 12), mask())
    return device


def frame_image(frame):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACK)
    draw = ImageDraw.Draw(image)
    if frame < 54 or frame >= 360:
        draw.rounded_rectangle((88, 212, 632, 682), 45, fill="#f5faf2")
        badge = "#357559" if frame < 360 or frame >= 368 else "#738f81"
        draw.ellipse((334, 291, 386, 343), fill=badge)
        label(draw, (360, 318), "F", 29, "white", "mm", True)
        label(draw, (360, 411), "Field Notes" if frame < 54 else "You're on the list.",
              51, DARK, "mm", True)
        label(draw, (360, 487), "Make a little time outside." if frame < 54 else "7:10 PM · North Gate",
              25, LINE, "mm")
        return image
    scale = 1 + 0.25 * ease(frame, 174, 220) - 0.25 * ease(frame, 229, 263)
    device = phone(frame)
    device = device.resize((round(416 * scale), round(676 * scale)), Image.Resampling.LANCZOS)
    x = (WIDTH - device.width) // 2
    y = (HEIGHT - device.height) // 2
    image.paste(device, (x, y), device)
    return image


def audio(path):
    samples = np.zeros(FRAMES * RATE // FPS)
    for frame, freq in CUES:
        time = np.arange(6750) / RATE
        pulse = (np.sin(2 * np.pi * freq * time) + 0.32 * np.sin(4 * np.pi * freq * time))
        pulse *= 0.25 * (1 - np.exp(-430 * time)) * np.exp(-37 * time)
        start = frame * RATE // FPS
        samples[start:start + pulse.size] += pulse
    with wave.open(str(path), "wb") as sound:
        sound.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        sound.writeframes((samples * 32767).astype("<i2").tobytes())


def main():
    destination = Path(__file__).with_name("reference.mp4")
    with tempfile.TemporaryDirectory() as temp:
        wav = Path(temp) / "original.wav"
        audio(wav)
        command = ["ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
                   "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-i", str(wav),
                   "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(destination)]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
            for number in range(FRAMES):
                encoder.stdin.write(frame_image(number).tobytes())
            encoder.stdin.close()
            if encoder.wait():
                raise RuntimeError("Fixture encode failed")


if __name__ == "__main__":
    main()
