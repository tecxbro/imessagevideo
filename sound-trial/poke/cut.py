#!/usr/bin/env python3
"""Extract the same zero-based Poke frame range for every treatment."""

import argparse
import subprocess
from pathlib import Path

from mix import probe, run, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("silent_master", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if sha256(args.silent_master) != "61286445805216b985028595c7e3f0f8dd01c2da44695b658a867145eef0d772":
        parser.error("Use the pinned silent Poke GSAP master")
    # Reclock the selected frames at native cadence so the last frame gets a full duration.
    with subprocess.Popen([
        "ffmpeg", "-v", "error", "-threads", "2", "-i", str(args.silent_master),
        "-map", "0:v:0", "-vf", "trim=start_frame=540:end_frame=770",
        "-fps_mode", "passthrough", "-pix_fmt", "yuv420p", "-f", "rawvideo", "-",
    ], stdout=subprocess.PIPE) as decoder:
        run(
            "ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pixel_format", "yuv420p",
            "-video_size", "1440x1080", "-framerate", "30000/1001", "-i", "-",
            "-c:v", "libx264", "-crf", "16", "-threads", "3", "-preset", "fast",
            "-movflags", "+faststart", str(args.output), stdin=decoder.stdout,
        )
        if decoder.wait():
            raise RuntimeError("Could not decode Poke master")
    print(probe(args.output))
    print(sha256(args.output))


if __name__ == "__main__":
    main()
