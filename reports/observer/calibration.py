import argparse
import itertools
import json
import random
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT, FPS, FRAMES, SAMPLE_RATE = 480, 640, 30, 180, 48000
SAMPLES_PER_FRAME = SAMPLE_RATE // FPS
PINK = (255, 49, 111)
BACK = (27, 39, 66)
FAULTS = ("clean", "mask-leak", "wrong-reaction", "substituted-fade", "late-cue", "missing-tail")
ZONES = {
    "phone-edge": (54, 235, 84, 385),
    "reaction-targets": (190, 145, 382, 310),
    "attachment-gesture": (88, 225, 392, 400),
}


def font(size):
    return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


def draw_card(surface, left, top, second=False):
    draw = ImageDraw.Draw(surface)
    draw.rounded_rectangle((left, top, left + 232, top + 142), 19,
                           fill="#9ee8d2" if second else "#bfcfff")
    draw.ellipse((left + 15, top + 17, left + 60, top + 62), fill="#293a78")
    draw.text((left + 75, top + 22), "West Dock" if second else "East Dock",
              fill="#101b3c", font=font(23))
    draw.text((left + 18, top + 92), "6:40 PM" if second else "6:15 PM",
              fill="#101b3c", font=font(22))


def draw_frame(frame, fault):
    picture = Image.new("RGB", (WIDTH, HEIGHT), BACK)
    exterior = ImageDraw.Draw(picture)
    exterior.rounded_rectangle((76, 31, 404, 610), 37, fill="#121825")
    screen = Image.new("RGB", picture.size, "white")
    mask = Image.new("L", picture.size)
    ImageDraw.Draw(mask).rounded_rectangle((84, 39, 396, 602), 30, fill=255)
    draw = ImageDraw.Draw(screen)
    draw.rounded_rectangle((210, 51, 270, 64), 7, fill="#19212f")
    draw.text((240, 99), "Avery", fill="#111528", font=font(24), anchor="mm")
    draw.line((84, 126, 396, 126), fill="#d5deeb", width=2)
    draw.rounded_rectangle((154, 154, 370, 200), 20, fill="#087df6")
    draw.text((168, 164), "Which dock is open?", font=font(18), fill="white")
    draw.rounded_rectangle((99, 204, 318, 244), 18, fill="#e7eaf1")
    draw.text((111, 212), "Try these two times", font=font(18), fill="#17243d")
    if frame >= 36:
        left = min(129, -112 + (frame - 36) * 11)
        amount = min(1, max(0, (frame - 90) / 24))
        if fault == "substituted-fade" and 90 < frame < 114:
            first, second = screen.copy(), screen.copy()
            draw_card(first, 129, 258)
            draw_card(second, 129, 258, True)
            screen = Image.blend(first, second, amount)
        elif frame < 114:
            draw_card(screen, left - round(amount * 294), 258)
            if frame > 90:
                draw_card(screen, left + 294 - round(amount * 294), 258, True)
        else:
            draw_card(screen, 129, 258, True)
    draw = ImageDraw.Draw(screen)
    if frame >= 70 and (frame < 114 or fault == "wrong-reaction"):
        displacement = round(min(1, max(0, (frame - 90) / 24)) * 294)
        anchor_x, anchor_y = (356, 150) if fault == "wrong-reaction" else (340 - displacement, 256)
        draw.ellipse((anchor_x - 16, anchor_y - 16, anchor_x + 16, anchor_y + 16), fill=PINK)
        draw.polygon([(anchor_x - 9, anchor_y - 3), (anchor_x - 4, anchor_y - 8),
                      (anchor_x, anchor_y - 4), (anchor_x + 4, anchor_y - 8),
                      (anchor_x + 9, anchor_y - 3), (anchor_x, anchor_y + 8)], fill="white")
    if frame >= 128:
        draw.rounded_rectangle((102, 435, 334, 481), 20, fill="#e7eaf1")
        draw.text((117, 445), "West Dock is open.", font=font(20), fill="#17243d")
    draw.rounded_rectangle((119, 547, 365, 579), 15, outline="#bac5d7", width=2)
    draw.text((135, 554), "iMessage", fill="#8693aa", font=font(16))
    picture.paste(screen, mask=mask)
    if fault == "mask-leak" and frame == 55:
        ImageDraw.Draw(picture).rectangle((62, 280, 75, 323), fill="#bfcfff")
    return picture


def write_audio(path, fault):
    samples = np.zeros(FRAMES * SAMPLES_PER_FRAME)
    cues = [(99 if fault == "late-cue" else 96, 920)]
    if fault != "missing-tail":
        cues.append((158, 560))
    for frame, frequency in cues:
        time = np.arange(4160) / SAMPLE_RATE
        wavelet = 0.54 * np.sin(2 * np.pi * frequency * time) * np.exp(-66 * time)
        start = frame * SAMPLES_PER_FRAME
        samples[start:start + time.size] = wavelet
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
        out.writeframes((samples * 32767).astype("<i2").tobytes())


def render(path, fault):
    with tempfile.TemporaryDirectory() as temp:
        sound = Path(temp) / "cue.wav"
        write_audio(sound, fault)
        with subprocess.Popen(
            ["ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-i", str(sound),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(path)],
            stdin=subprocess.PIPE,
        ) as encoder:
            for frame in range(FRAMES):
                encoder.stdin.write(draw_frame(frame, fault).tobytes())
            encoder.stdin.close()
            if encoder.wait():
                raise RuntimeError(f"Encode failed: {path}")


def picture_frames(path):
    with subprocess.Popen(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0", "-f",
         "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
    ) as decoder:
        while frame := decoder.stdout.read(WIDTH * HEIGHT * 3):
            yield np.frombuffer(frame, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3)
        if decoder.wait():
            raise RuntimeError(f"Decode failed: {path}")


def cue_starts(path):
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:a:0",
         "-f", "f32le", "-ar", str(SAMPLE_RATE), "-ac", "1", "-"]
    )
    samples = np.frombuffer(raw, dtype="<f4")
    active = np.flatnonzero(np.abs(samples) > 0.10)
    groups = np.split(active, np.where(np.diff(active) > SAMPLES_PER_FRAME)[0] + 1)
    return [int(group[0]) for group in groups if group.size]


def intervals(frames):
    spans = []
    for _, group in itertools.groupby(enumerate(frames), lambda point: point[1] - point[0]):
        values = [value for _, value in group]
        spans.append([values[0], values[-1]])
    return spans


def inspect(reference, candidate):
    hits = {zone: [] for zone in ZONES}
    global_mae = []
    for frame, (want, got) in enumerate(zip(picture_frames(reference), picture_frames(candidate),
                                              strict=True)):
        delta = np.abs(want.astype(np.int16) - got.astype(np.int16))
        global_mae.append(float(delta.mean()))
        substantial = delta.max(axis=2) > 45
        for name, (left, top, right, bottom) in ZONES.items():
            if np.count_nonzero(substantial[top:bottom, left:right]) >= 96:
                hits[name].append(frame)
    if len(global_mae) != FRAMES:
        raise RuntimeError(f"Wrong decoded count: {candidate}")
    wanted, found = cue_starts(reference), cue_starts(candidate)
    return {
        "frame_count": len(global_mae),
        "max_full_frame_mae": max(global_mae),
        "coarse_10_frame_scan": {zone: [frame for frame in frames if frame % 10 == 0]
                                 for zone, frames in hits.items() if any(f % 10 == 0 for f in frames)},
        "all_frame_zone_intervals": {zone: intervals(frames) for zone, frames in hits.items() if frames},
        "expected_cue_starts_samples": wanted,
        "actual_cue_starts_samples": found,
        "audio_match": len(wanted) == len(found) and all(abs(a - b) < 120 for a, b in zip(wanted, found)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("build", "inspect"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    lab = args.directory
    if args.mode == "build":
        lab.mkdir(mode=0o700)
        (lab / "masked").mkdir()
        render(lab / "reference.mp4", "clean")
        shuffled = list(FAULTS)
        random.SystemRandom().shuffle(shuffled)
        key = {f"clip-{index + 1:02d}": fault for index, fault in enumerate(shuffled)}
        for label, fault in key.items():
            render(lab / "masked" / f"{label}.mp4", fault)
        with (lab / "key.json").open("x") as out:
            json.dump(key, out, indent=2)
    else:
        candidates = sorted((lab / "masked").glob("*.mp4"))
        if len(candidates) != len(FAULTS):
            raise RuntimeError("Incomplete anonymous calibration set")
        results = {path.stem: inspect(lab / "reference.mp4", path) for path in candidates}
        verdicts = {label: "revision needed" if value["all_frame_zone_intervals"] or
                    not value["audio_match"] else "fixture passed" for label, value in results.items()}
        with (lab / "locked-verdicts.json").open("x") as out:
            json.dump({"verdicts": verdicts, "evidence": results}, out, indent=2)


if __name__ == "__main__":
    main()
