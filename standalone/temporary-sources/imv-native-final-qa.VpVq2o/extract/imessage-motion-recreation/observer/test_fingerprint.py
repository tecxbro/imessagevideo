#!/usr/bin/env python3
"""Exercise the intake CLI with generated films and transformed copies."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

TOOL = Path(__file__).with_name("fingerprint.py")
SIZE = (256, 384)
FPS = 24
DURATION = 10


def run(*arguments: str) -> None:
    subprocess.run(arguments, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def generate_film(path: Path, alternate: bool = False) -> None:
    encode = [
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{SIZE[0]}x{SIZE[1]}", "-framerate", str(FPS), "-i", "pipe:0",
        "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(path),
    ]
    with subprocess.Popen(encode, stdin=subprocess.PIPE) as encoder:
        assert encoder.stdin is not None
        for frame in range(FPS * DURATION):
            image = Image.new("RGB", SIZE, "#292239")
            draw = ImageDraw.Draw(image)
            cut, progress = divmod(frame, FPS * 2)
            advance = progress * 2
            draw.rounded_rectangle((20, 18, 236, 366), radius=22, fill="#f1eedb")
            draw.rectangle((32, 42, 224, 65), fill="#3a5d78")
            draw.rectangle((32, 304, 224, 348), fill="#e1cfa9")
            colors = ("#34469f", "#c2484b", "#147456", "#521473", "#963f1e")
            if alternate:
                for index in range(5):
                    position = 71 + index * 45
                    span = 24 + (index * 23 + advance) % 130
                    draw.rounded_rectangle(
                        (44, position, 44 + span, position + 28),
                        radius=9,
                        fill=colors[(index + cut) % len(colors)],
                    )
            else:
                x = 46 + advance // 2
                y = 80 + 38 * cut
                color = colors[cut]
                shapes = (
                    lambda: draw.ellipse((x, y, x + 110, y + 78), fill=color),
                    lambda: draw.polygon(((x, y), (x + 106, y), (x + 17, y + 110)), fill=color),
                    lambda: draw.rectangle((x - 12, y - 64, x + 45, y + 91), fill=color),
                    lambda: draw.line(((x, 90), (192, y), (x, 290)), width=19, fill=color),
                    lambda: draw.rectangle((41, y - 70, 42 + advance, y + 44), fill=color),
                )
                shapes[cut]()
                for index in range(cut + 1):
                    draw.ellipse((49 + 26 * index, 320, 59 + 26 * index, 330), fill=color)
            encoder.stdin.write(image.tobytes())
        encoder.stdin.close()
        if encoder.wait() != 0:
            raise RuntimeError("FFmpeg could not generate the test film")


def check_case(candidate: Path, exclusions: Path, expected_status: int, expected_method: str | None = None) -> None:
    result = subprocess.run(
        [sys.executable, str(TOOL), "check", str(candidate), "--exclusions", str(exclusions)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == expected_status, (candidate.name, result.returncode, result.stdout, result.stderr)
    if result.returncode == 2:
        assert result.stderr == "fingerprint: invalid exclusion JSON\n", result.stderr
        print(f"{candidate.stem}: invalid manifest blocked")
        return
    payload = json.loads(result.stdout)
    assert payload.get("method") == expected_method, payload
    assert payload["status"] == ("excluded" if expected_status == 1 else "clear"), payload
    assert candidate.name not in result.stdout and str(exclusions) not in result.stdout
    evidence = ""
    if expected_method == "visual":
        evidence = f" at {payload['coverage']:.0%} coverage with mean distance {payload['mean_distance']}"
    print(f"{candidate.stem}: {payload['status']}{evidence}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="film-fingerprint-test-") as temporary:
        directory = Path(temporary)
        original = directory / "source-name-must-not-leak.mp4"
        exclusions = directory / "exclusions.json"
        generate_film(original)
        run(sys.executable, str(TOOL), "fingerprint", str(original), "--output", str(exclusions))
        fingerprint_text = exclusions.read_text()
        payload = json.loads(fingerprint_text)
        assert payload.keys() == {"algorithm", "sample_fps", "frames", "sha256"}
        assert original.name not in fingerprint_text and temporary not in fingerprint_text
        assert len(payload["frames"]) == DURATION * payload["sample_fps"]
        check_case(original, exclusions, 1, "sha256")

        variants = {
            "resized-reencoded": "scale=192:288,fps=30",
            "padded-cropped-watermarked": (
                "crop=iw*0.84:ih*0.84,scale=212:318,pad=400:360:94:20:black,"
                "drawbox=x=132:y=39:w=24:h=11:c=white@0.8:t=fill"
            ),
            "added-intro-trimmed-tail": "trim=end=9.8,tpad=start_duration=1.1:color=black",
            "reversed-story": "reverse",
            "rotated-story": "hflip,vflip",
        }
        for name, filters in variants.items():
            destination = directory / f"{name}.mp4"
            run(
                "ffmpeg", "-v", "error", "-i", str(original), "-vf", filters, "-an",
                "-c:v", "libx264", "-threads", "1", "-crf", "31", "-pix_fmt", "yuv420p", str(destination),
            )
            positive = name in {"resized-reencoded", "padded-cropped-watermarked", "added-intro-trimmed-tail"}
            check_case(destination, exclusions, int(positive), "visual" if positive else None)

        different = directory / "same-layout-different-film.mp4"
        generate_film(different, alternate=True)
        check_case(different, exclusions, 0)

        exclusion_array = directory / "exclusion-array.json"
        exclusion_array.write_text(json.dumps([payload]))
        check_case(original, exclusion_array, 1, "sha256")

        malformed = directory / "malformed-exclusions.json"
        malformed.write_text("{")
        check_case(original, malformed, 2)


if __name__ == "__main__":
    main()
