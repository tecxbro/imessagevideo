#!/usr/bin/env python3
"""Record the decoded video timeline without resampling it."""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import subprocess


def ffprobe(path, *args):
    return json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", *args, "-of", "json", str(path)]
    ))


def probe(path):
    media = ffprobe(path, "-show_format", "-show_streams")
    stream = next(s for s in media["streams"] if s["codec_type"] == "video")
    time_base = Fraction(stream["time_base"])
    frames = ffprobe(
        path, "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=pts,best_effort_timestamp,duration,pkt_duration",
    )["frames"]
    ticks = [int(f.get("pts", f.get("best_effort_timestamp"))) for f in frames]
    if not ticks or any(a >= b for a, b in zip(ticks, ticks[1:])):
        raise ValueError("Expected strictly increasing presentation timestamps")

    rate = Fraction(stream["avg_frame_rate"]) if stream["avg_frame_rate"] != "0/0" else 0
    # A coarse container time base can quantize adjacent CFR intervals differently.
    step = 1 / (rate * time_base) if rate else None
    constant = step is not None and all(
        abs(tick - ticks[0] - i * step) < 1 for i, tick in enumerate(ticks)
    )
    last = frames[-1]
    last_duration = last.get("duration") or last.get("pkt_duration")
    if not last_duration and "duration_ts" in stream:
        remaining = int(stream.get("start_pts", ticks[0])) + int(stream["duration_ts"]) - ticks[-1]
        last_duration = remaining if remaining > 0 else None

    decoded = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-xerror", "-noautorotate", "-i", str(path),
         "-map", "0:v:0", "-fps_mode", "passthrough", "-f", "framemd5", "-"],
        text=True,
    )
    hashes = [line.rsplit(",", 1)[1].strip() for line in decoded.splitlines()
              if line and not line.startswith("#")]
    if len(hashes) != len(ticks):
        raise ValueError(f"ffprobe reported {len(ticks)} frames, ffmpeg decoded {len(hashes)}")
    tail = len(hashes) - 1
    while tail > 0 and hashes[tail - 1] == hashes[-1]:
        tail -= 1

    with path.open("rb") as source:
        sha256 = hashlib.file_digest(source, "sha256").hexdigest()
    rotation = next((item["rotation"] for item in stream.get("side_data_list", [])
                     if "rotation" in item), 0)
    width, height = stream["width"], stream["height"]
    if rotation % 180 == 90:
        width, height = height, width
    orientation = "square" if width == height else "landscape" if width > height else "portrait"
    return {
        "file": path.name,
        "sha256": sha256,
        "container_duration_seconds": media["format"].get("duration"),
        "video": stream,
        "rotation_degrees": rotation,
        "display_orientation": orientation,
        "audio_streams": [s for s in media["streams"] if s["codec_type"] == "audio"],
        "presentation": {
            "time_base": str(time_base),
            "decoded_frames": len(ticks),
            "pts_ticks_in_frame_order": ticks,
            "estimated_timestamp_frames": [i for i, f in enumerate(frames) if "pts" not in f],
            "cadence": ("undetermined" if len(ticks) < 2 else
                        "cfr" if constant else "nonuniform"),
            "cfr_rate": str(rate) if constant and len(ticks) > 1 else None,
            "last_frame_duration_ticks": int(last_duration) if last_duration else None,
            "last_identical_run_start_frame": tail,
            "last_identical_run_frames": len(hashes) - tail,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = probe(args.video)
    with args.out.open("x") as out:
        json.dump(result, out, indent=2)
        out.write("\n")


if __name__ == "__main__":
    main()
