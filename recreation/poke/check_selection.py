#!/usr/bin/env python3
"""Check the third restaurant's selected state in an actual decoded Poke export."""

import argparse
import json
from pathlib import Path
import subprocess


FIRST, LAST = 620, 650
WIDTH, HEIGHT = 480, 360
EXPECTED_FRAME = 633


def blue_area(frame, box):
    x0, y0, x1, y1 = box
    count = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            i = 3 * (y * WIDTH + x)
            r, g, b = frame[i:i + 3]
            count += r < 65 and 90 < g < 200 and b > 200
    return count


def measure(movie, first, last, boxes):
    command = [
        "ffmpeg", "-v", "error", "-xerror", "-i", str(movie), "-an",
        "-vf", f"select=between(n\\,{first}\\,{last}),scale={WIDTH}:{HEIGHT}",
        "-frames:v", str(last - first + 1), "-fps_mode", "passthrough",
        "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ]
    data = memoryview(subprocess.check_output(command))
    frame_bytes = WIDTH * HEIGHT * 3
    if len(data) != frame_bytes * (last - first + 1):
        raise ValueError(f"Incomplete decode of frames {first}–{last}")
    values = []
    for n in range(first, last + 1):
        start = (n - first) * frame_bytes
        frame = data[start:start + frame_bytes]
        values.append({"frame": n, **{name: blue_area(frame, box) for name, box in boxes.items()}})
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("movie", type=Path)
    args = parser.parse_args()
    frames = measure(args.movie, FIRST, LAST, {
        "zareens": (352, 135, 393, 201),
        "khazana": (352, 55, 393, 104),
        "darbar": (352, 224, 393, 284),
    })
    selected = [f["frame"] for f in frames if f["zareens"] > 35]
    neighbors_clear = all(max(f["khazana"], f["darbar"]) <= 35 for f in frames)
    expected = list(range(EXPECTED_FRAME, LAST + 1))
    calendar = measure(args.movie, 228, 240, {
        "7:30 PM": (84, 170, 184, 198),
        "10:30 PM": (203, 170, 296, 198),
    })
    calendar_selected = [f["frame"] for f in calendar if f["7:30 PM"] > 1500]
    calendar_passed = calendar_selected == list(range(232, 241)) and all(
        f["10:30 PM"] <= 1500 for f in calendar
    )
    passed = selected == expected and neighbors_clear and calendar_passed
    print(json.dumps({
        "movie": str(args.movie),
        "first_selected_frame": selected[0] if selected else None,
        "expected_first_selected_frame": EXPECTED_FRAME,
        "persistent_through": LAST if selected == expected else None,
        "neighbor_controls_unselected": neighbors_clear,
        "calendar_control_first_selected": calendar_selected[0] if calendar_selected else None,
        "calendar_control_pass": calendar_passed,
        "pass": passed,
        "frames": frames,
        "calendar_frames": calendar,
    }, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
