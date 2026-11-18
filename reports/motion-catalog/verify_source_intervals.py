#!/usr/bin/env python3
"""Verify source hashes and decoded timestamps for the measured motion entries."""

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "skill/imessage-motion-recreation/director/motion-library/catalog.json"


def verify_source(entry):
    evidence = entry["evidence"]
    movie = ROOT / evidence["localMovie"]
    with movie.open("rb") as file:
        digest = hashlib.file_digest(file, "sha256").hexdigest()
    if digest != evidence["sha256"]:
        raise ValueError(f"{movie}: SHA-256 differs from catalog")

    probe = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_frames", "-show_streams",
            "-show_entries",
            "frame=stream_index,best_effort_timestamp"
            ":stream=index,codec_type,codec_name,width,height,time_base,r_frame_rate"
            ",avg_frame_rate,sample_rate,channels",
            "-of", "json",
            str(movie),
        ],
        text=True,
    )
    result = json.loads(probe)
    video = next(stream for stream in result["streams"] if stream["codec_type"] == "video")
    time_base = Fraction(video["time_base"])
    frames = [frame for frame in result["frames"] if frame["stream_index"] == video["index"]]
    first, last = evidence["framesInclusive"]
    if not 0 <= first <= last < len(frames) - 1:
        raise ValueError(f"{movie}: interval needs decoded frames and the next frame's timestamp")
    # The next display timestamp gives the half-open end of the inspected interval.
    times = [
        int(frame["best_effort_timestamp"]) * time_base
        for frame in frames[first:last + 2]
    ]
    bounds = [float(times[0]), float(times[-1])]
    for recorded, decoded in zip(evidence["secondsHalfOpen"], bounds, strict=True):
        if round(recorded, 6) != round(decoded, 6):
            raise ValueError(f"{movie}: catalog time {recorded} differs from decoded {decoded}")
    steps = sorted({end - start for start, end in zip(times, times[1:])})
    if any(step <= 0 for step in steps):
        raise ValueError(f"{movie}: display timestamps are out of order")
    audio = [
        {key: stream[key] for key in ("codec_name", "sample_rate", "channels")}
        for stream in result["streams"]
        if stream["codec_type"] == "audio"
    ]
    return {
        "entry": entry["id"],
        "source": evidence["localMovie"],
        "sha256": digest,
        "framesInclusive": [first, last],
        "intervalFrameCount": last - first + 1,
        "exactSecondsHalfOpen": [str(times[0]), str(times[-1])],
        "secondsPerFrameInInterval": [str(step) for step in steps],
        "sourceSizePx": [video["width"], video["height"]],
        "sourceTimeBase": str(time_base),
        "reportedSourceRates": [video["r_frame_rate"], video["avg_frame_rate"]],
        "sourceAudioStreams": audio,
    }


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    measurements = [
        verify_source(entry)
        for entry in catalog["entries"]
        if entry["evidence"]["kind"] == "measured-film"
    ]
    if not measurements:
        raise ValueError("catalog has no measured source entries")
    print(json.dumps(measurements, indent=2))


if __name__ == "__main__":
    main()
