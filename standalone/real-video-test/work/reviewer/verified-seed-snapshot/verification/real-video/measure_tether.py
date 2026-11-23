"""Measure the visible colored shuttle in the independent three-second test film."""
import argparse
import csv
import json
import math
from pathlib import Path
import subprocess

import numpy as np


def keys(values):
    return [{"t": i / 30, "value": value} for i, value in enumerate(values)]


def rect(layer_id, x, y, width, height, fill, radius=0, **extras):
    return dict(id=layer_id, type="rect", x=x, y=y, width=width, height=height,
                fill=fill, radius=radius, **extras)


def circle(layer_id, x, y, radius, fill):
    return dict(id=layer_id, type="circle", x=x, y=y, radius=radius, fill=fill)


def measure(source):
    data = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(source), "-map", "0:v:0",
        "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ])
    frames = np.frombuffer(data, np.uint8).reshape(-1, 270, 480, 3)
    if len(frames) != 90:
        raise ValueError("Expected the benchmark's 90 native frames")
    centers = []
    for frame in frames.astype(np.int16):
        r, g, b = frame.transpose(2, 0, 1)
        y, x = np.where((r > 170) & (b > 180) & (g < 195) & (r > g + 35))
        centers.append((float((x.min() + x.max() + 1) / 2), float((y.min() + y.max() + 1) / 2)))
    return centers


def author(source, output):
    output.mkdir(parents=True, exist_ok=True)
    centers = measure(source)
    with (output / "trajectory.csv").open("w", newline="") as evidence:
        writer = csv.writer(evidence)
        writer.writerow(("frame", "seconds", "shuttle_center_x", "shuttle_center_y"))
        writer.writerows((i, i / 30, x, y) for i, (x, y) in enumerate(centers))

    pivot = (107, 176)
    board = "#212a44"
    length = [math.hypot(x - pivot[0], y - pivot[1]) for x, y in centers]
    angle = [math.degrees(math.atan2(y - pivot[1], x - pivot[0])) for x, y in centers]
    layers = [
        rect("board", 38, 37, 404, 195, board, 17),
        rect("heading-mark", 53, 56, 43, 6, "#45e5bd", 3),
        rect("heading-dash", 104, 56, 27, 6, "#405578", 3),
        rect("baseline", 54, 211, 372, 1, "#485772", 0),
        circle("dock", 351, 70, 18, "#3e4a68"),
        circle("dock-center", 355, 74, 14, board),
        rect("elastic-tether", pivot[0], pivot[1] - 3, length[0], 6, "#65aaef", 3, originY=3,
             keyframes={"width": keys(length), "rotation": keys(angle)}),
        circle("pivot-ring", 95, 165, 12, "#47e1be"),
        circle("pivot-center", 102.5, 172.5, 4.5, board),
        rect("shuttle", centers[0][0] - 18, centers[0][1] - 12, 36, 24, "#ef94ff", 9,
             keyframes={"x": keys([x - 18 for x, _ in centers]),
                        "y": keys([y - 12 for _, y in centers])}),
    ]
    scene = {"width": 480, "height": 270, "fps": 30, "duration": 3,
             "background": "#121a26", "layers": layers}
    recipe = {
        "id": "tether-extend-then-pivot-dock",
        "title": "Extend a tether, then pivot it into a fixed dock",
        "description": "A horizontal shuttle pulls out a tether, pauses at full reach, then turns upward on the same tether into a fixed dock.",
        "scene": "scene.json", "assets": {}, "renderer": "pillow", "antialias": 3,
        "fits": ["A latched endpoint moves horizontally, holds, then pivots an attached tether into a fixed dock"],
        "avoid": ["A free particle without a fixed pivot or a static traced route"],
        "moving": ["elastic-tether", "shuttle"],
        "fixed": ["board", "heading-mark", "heading-dash", "baseline", "dock", "dock-center",
                  "pivot-ring", "pivot-center"],
        "tags": ["tether", "pivot", "right-angle path", "docking"],
        "parameters": {
            "shuttle-color": "/layers/9/fill",
            "tether-color": "/layers/6/fill",
            "shuttle-x-frame-24": "/layers/9/keyframes/x/24/value",
        },
        "source": {"label": "Independently authored unseen test original", "start_frame": 0,
                   "observation": "Shuttle starts near (173,176), holds near (369,176), rises with the tether and lands near (369,88), then holds through frame 89."},
        "checks": {
            "rois": {"shuttle-and-tether": [92, 69, 302, 123], "swipe-midpoint": [219, 161, 75, 31],
                     "fixed-heading": [47, 50, 92, 20],
                     "fixed-baseline": [48, 202, 383, 19]},
            "max_mae": 6, "max_pts_error_ms": 0,
            "reason": "Allows renderer anti-alias and MP4 color conversion error. ROIs include both shuttle phases and the fixed marks.",
            "negative_control": {"set": {"shuttle-x-frame-24": centers[0][0] - 18},
                                 "reason": "A one-frame shuttle snap breaks the moving ROI."},
        },
    }
    for name, payload in (("scene.json", scene), ("candidate.json", recipe)):
        (output / name).write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    author(args.source, args.output)
