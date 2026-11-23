#!/usr/bin/env python3
"""Independently generated faults for the recreation comparison CLI."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from struct import pack, unpack_from
import subprocess
import sys

import numpy as np


WIDTH, HEIGHT, COUNT, TIMESCALE = 160, 90, 64, 30000
CHECKER = Path(__file__).resolve().parents[1] / "recreate.py"


def ffmpeg(out, *arguments, pixels=None):
    subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", *arguments, str(out)],
        input=pixels.tobytes() if pixels is not None else None,
        check=True,
    )


def encode(out, pixels):
    ffmpeg(
        out, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", "30",
        "-i", "pipe:0", "-c:v", "libx264rgb", "-crf", "0", "-bf", "0",
        "-video_track_timescale", str(TIMESCALE), pixels=pixels,
    )


def add_clean_aperture(base):
    """Add a centered 125×80 MP4 clean aperture without touching the video samples."""
    containers = {b"moov": 0, b"trak": 0, b"mdia": 0, b"minf": 0, b"stbl": 0, b"stsd": 8}
    aperture = pack(">I4s8I", 40, b"clap", 125, 1, 80, 1, 0, 1, 0, 1)

    def add_to_sample_entry(boxes):
        result = bytearray()
        offset = 0
        while offset < len(boxes):
            size, kind = unpack_from(">I4s", boxes, offset)
            if not 8 <= size <= len(boxes) - offset:
                raise ValueError(f"Invalid fixture atom {kind!r} at {offset}")
            body = boxes[offset + 8:offset + size]
            if kind in containers:
                lead = containers[kind]
                body = body[:lead] + add_to_sample_entry(body[lead:])
            elif kind == b"avc1":
                body += aperture
            result.extend(pack(">I4s", 8 + len(body), kind) + body)
            offset += size
        return result

    # FFmpeg writes moov after mdat in this fixture, so no sample offsets move.
    data = add_to_sample_entry(base.read_bytes())
    if aperture not in data:
        raise ValueError("No AVC sample entry in the aperture fixture")
    return data


def make_media(out):
    pictures = np.full((COUNT, HEIGHT, WIDTH, 3), 245, np.uint8)
    pictures[15:19, 25:55, 20:55] = [15, 30, 90]
    pictures[29:, 69:72, 122:125] = [12, 73, 212]
    base = out / "base.mp4"
    encode(base, pictures)
    one_pixel = pictures.copy()
    one_pixel[17, 89, 159, 0] += 1
    encode(out / "one-pixel.mp4", one_pixel)
    encode(out / "dropped-and-padded.mp4", np.concatenate([pictures[:15], pictures[16:], pictures[-1:]]))
    encode(out / "extra-tail.mp4", np.concatenate([pictures, pictures[-3:]]))
    delayed = pictures.copy()
    delayed[29:31] = delayed[28]
    encode(out / "late-selection.mp4", delayed)

    remux = ("-map", "0:v", "-c:v", "copy", "-video_track_timescale", str(TIMESCALE))
    ffmpeg(out / "off-grid.mp4", "-i", str(base), *remux, "-bsf:v", r"setts=ts=TS+eq(N\,17)*417")
    ffmpeg(
        out / "extended-hold.mp4", "-i", str(base), *remux,
        "-bsf:v", r"setts=duration=DURATION+eq(N\,63)*7000",
    )
    ffmpeg(out / "mirror-v.mp4", "-display_vflip", "-i", str(base), *remux)
    ffmpeg(
        out / "pq.mp4", "-i", str(base), *remux,
        "-bsf:v", "h264_metadata=transfer_characteristics=16:colour_primaries=9",
    )
    b_frames = out / "b-frames.mp4"
    ffmpeg(
        b_frames, "-i", str(base), "-map", "0:v", "-c:v", "libx264rgb", "-crf", "8", "-bf", "3",
        "-x264-params", "b-adapt=0:scenecut=0", "-video_track_timescale", str(TIMESCALE),
    )
    frame_types = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "V:0", "-show_entries", "frame=pict_type",
        "-of", "csv=p=0", str(b_frames),
    ], text=True)
    if "B" not in frame_types.splitlines():
        raise ValueError("The coded-order fixture lacks B pictures")
    (out / "clean-aperture.mp4").write_bytes(add_clean_aperture(base))

    rgba = np.full((8, HEIGHT, WIDTH, 4), 255, np.uint8)
    rgba[:, 24:48, 40:70, :3] = [0, 120, 30]
    for name, alpha in (("alpha-opaque", 255), ("alpha-transparent", 0)):
        rgba[:, 24:48, 40:70, 3] = alpha
        ffmpeg(
            out / f"{name}.mov", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{WIDTH}x{HEIGHT}",
            "-r", "30", "-i", "pipe:0", "-c:v", "qtrle", "-video_track_timescale", str(TIMESCALE),
            pixels=rgba,
        )

    with_audio = out / "audio-base.mp4"
    ffmpeg(
        with_audio, "-i", str(base), "-f", "lavfi", "-i", "sine=d=3:r=48000",
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
        "-video_track_timescale", str(TIMESCALE),
    )
    ffmpeg(
        out / "audio-picture-delayed.mp4", "-itsoffset", "0.25", "-i", str(base),
        "-i", str(with_audio), "-map", "0:v", "-map", "1:a", "-c", "copy",
        "-video_track_timescale", str(TIMESCALE),
    )


def make_checks(out):
    region = {"id": "mark", "start": 27, "end": 32, "rect": [120, 67, 7, 7], "mae": 1}
    gate_profiles = {
        "roi": {"regions": [region]},
        "motion": {"regions": [{**region, "mae": 255, "step_mae": 0}]},
        "tile": {"tile": {"size": 12, "mae": 1}},
        "invalid_roi": {"regions": [{**region, "start": 63, "end": 64}]},
        "sync": {"audio": "present", "audio_checks": {"max_start_delta_seconds": "1/100"}},
    }
    for name, profile in gate_profiles.items():
        (out / f"{name}.json").write_text(json.dumps(profile, indent=2) + "\n")


def measure(out, label, candidate, code, check=None, span=None, profile=None, reference="base", exact=False):
    destination = out / label

    def movie(name):
        return str(out / (name if Path(name).suffix else f"{name}.mp4"))

    command = [
        sys.executable, "-B", str(CHECKER), "compare", movie(reference), movie(candidate),
        "--out", str(destination),
    ]
    if profile:
        command.extend(["--checks", str(out / f"{profile}.json")])
    if exact:
        command.append("--exact")
    result = subprocess.run(command, capture_output=True, text=True)
    report_path = destination / "report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    failures = report.get("failures", [])
    expected_verdict = {0: "PASS", 1: "FAIL", 2: "ERROR"}[code]
    located = not check or any(
        item["check"] == check and (span is None or span in item.get("spans", []))
        for item in failures
    )
    passed = result.returncode == code and report.get("verdict") == expected_verdict and located
    record = {
        "case": label, "meets_expectation": passed, "expected_verdict": expected_verdict,
        "expected_check": check, "expected_span": span, "exit_code": result.returncode,
        "verdict": report.get("verdict"), "compared_frames": report.get("compared_frames"),
        "mean_abs_rgb": report.get("mean_abs_rgb"), "failures": failures, "error": report.get("message"),
    }
    if not report:
        record["stderr"] = result.stderr
    print(json.dumps(record), flush=True)
    return record


def review_single_pixel(out):
    diagnostic = out / "pixel-diagnostic" / "report.json"
    exact = out / "pixel-exact" / "report.json"
    def read(path):
        return json.loads(path.read_text())

    def write(name, value):
        path = out / name
        path.write_text(json.dumps(value))
        return path

    def digest(path):
        return sha256(path.read_bytes()).hexdigest()

    source = out / "base.mp4"
    pixel = out / "one-pixel.mp4"
    frames = [0, COUNT - 1]
    plan = write("plan.json", {
        "reference_sha256": digest(source), "comparison_checks_sha256": None, "frame_count": COUNT,
        "rgb_diagnostics": ["whole_frame_mae"],
        "shots": [{"id": "shot", "frames": frames,
                   "checks": {"criterion": {"frames": frames, "target": "Motion observed"}}}],
    })
    result_path = out / "acceptance.json"
    results = {"shot": {"criterion": {"verdict": "pass", "frames": frames, "observation": "Timing passes",
                                      "evidence": "pixel-diagnostic/frames.csv"}}}
    comparisons = [
        ("one-pixel-cannot-pass-review", diagnostic, pixel, 1, "FAIL", 0),
        ("identity-can-pass-review", out / "identity-exact" / "report.json", source, 0, "PASS", 1),
    ]
    records = []
    for case, comparison, candidate, code, verdict, count in comparisons:
        observations = write("observations.json", {"plan_sha256": digest(plan), "candidate_sha256": digest(candidate),
                                                    "comparison_sha256": digest(comparison), "results": results})
        result = subprocess.run([
            sys.executable, str(CHECKER), "verify-review", str(candidate), "--plan", str(plan),
            "--comparison", str(comparison), "--review", str(observations), "--out", str(result_path),
        ], capture_output=True, text=True)
        actual = read(result_path) if result.returncode != 2 else {}
        expected_pixel = {"frame": 17, "changed_pixels": 1, "max_channel_delta": 1, "rect": [159, 89, 1, 1]}
        located = read(exact)["pixel_equality"]["first_difference"] == expected_pixel
        record = {
            "case": case, "meets_expectation": located and result.returncode == code
            and actual.get("verdict") == verdict and actual.get("passed_shots") == count,
            "result": actual,
        }
        print(json.dumps(record), flush=True)
        records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    make_media(out)
    make_checks(out)
    evidence = [
        measure(out, "identity", "base", 0),
        measure(out, "identity-exact", "base", 0, exact=True),
        measure(out, "pixel-diagnostic", "one-pixel", 0),
        measure(out, "pixel-exact", "one-pixel", 1, "pixel_equality", exact=True),
        measure(out, "b-frames-preserve-display-order", "b-frames", 0, profile="tile"),
        measure(out, "interior-frame-loss", "dropped-and-padded", 1, "whole_frame_mae", [18, 18]),
        measure(out, "extra-tail-frames", "extra-tail", 1, "extra_candidate_frames", [64, 66]),
        measure(out, "variable-pts", "off-grid", 1, "presentation_clock", [17, 17]),
        measure(out, "extended-final-hold", "extended-hold", 1, "final_hold"),
        measure(out, "late-selection-roi", "late-selection", 1, "region", [29, 30], profile="roi"),
        measure(out, "late-selection-motion", "late-selection", 1, "region_motion", [29, 29], profile="motion"),
        measure(out, "late-selection-tile", "late-selection", 1, "local_tile_mae", [29, 30], profile="tile"),
        measure(out, "invalid-roi", "base", 2, profile="invalid_roi"),
        measure(out, "vertical-display-reflection", "mirror-v", 1, "display_geometry"),
        measure(out, "pq-display-tag", "pq", 1, "display_color"),
        measure(out, "clean-aperture-identity", "clean-aperture", 0, reference="clean-aperture"),
        measure(out, "unexpected-clean-aperture", "clean-aperture", 1, "display_geometry"),
        measure(out, "unsupported-transparency", "alpha-transparent.mov", 1,
                "unsupported_alpha_comparison", reference="alpha-opaque.mov"),
        measure(out, "video-delayed-from-audio", "audio-picture-delayed", 1,
                "audio_relative_start", profile="sync", reference="audio-base"),
    ]
    evidence.extend(review_single_pixel(out))
    (out / "suite.json").write_text(json.dumps(evidence, indent=2) + "\n")
    return 0 if all(case["meets_expectation"] for case in evidence) else 1


if __name__ == "__main__":
    sys.exit(main())
