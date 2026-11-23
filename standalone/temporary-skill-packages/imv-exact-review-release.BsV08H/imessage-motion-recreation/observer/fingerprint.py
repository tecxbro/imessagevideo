#!/usr/bin/env python3
"""Make exclusions for complete films and check a candidate before intake."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

from PIL import Image

ALGORITHM = "film-visual-v1"
SAMPLE_FPS = 4
THUMBNAIL_SIZE = 96
DCT_SIZE = 24
DCT_BASIS = tuple(
    tuple(math.cos(math.pi * k * (2 * n + 1) / (2 * DCT_SIZE)) for n in range(DCT_SIZE))
    for k in range(8)
)
VIEW_CROPS = (0, 0.08, 0.15)
VIEW_PAIRS = ((0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (1, 1))
FRAME_LIMIT = 0.30
MIN_FRAMES = 8

View = tuple[int, int, int, int]
Frame = tuple[View, ...]


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as film:
        for chunk in iter(lambda: film.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def video_frames(path: Path) -> list[Image.Image]:
    try:
        process = subprocess.run(
            [
                "ffmpeg", "-v", "error", "-xerror", "-nostdin", "-protocol_whitelist", "file,pipe,crypto",
                "-i", str(path.resolve()),
                "-map", "0:V:0", "-an", "-sn", "-dn",
                "-vf", f"fps={SAMPLE_FPS}:round=up,scale={THUMBNAIL_SIZE}:{THUMBNAIL_SIZE}:flags=area,format=gray",
                "-threads", "1", "-f", "rawvideo", "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError as error:
        raise ValueError("ffmpeg is required") from error
    except subprocess.CalledProcessError as error:
        raise ValueError("ffmpeg could not decode the video track") from error

    dimensions = (THUMBNAIL_SIZE, THUMBNAIL_SIZE)
    stride = THUMBNAIL_SIZE**2
    frames = [
        Image.frombytes("L", dimensions, process.stdout[start:start + stride])
        for start in range(0, len(process.stdout), stride)
        if start + stride <= len(process.stdout)
    ]
    if not frames:
        raise ValueError("video has no sampled frames")
    return frames


def trim_box(frames: list[Image.Image]) -> tuple[int, int, int, int]:
    """Find extreme, uniform edges shared across most of the movie."""
    size = THUMBNAIL_SIZE
    count = min(24, len(frames))
    samples = [frames[index * len(frames) // count].tobytes() for index in range(count)]
    scan_limit = round(size * 0.37)

    def is_border(line: bytes) -> bool:
        low, high = min(line), max(line)
        return high - low <= 14 and (high <= 18 or low >= 237)

    def depth(horizontal: bool, reversed_edge: bool) -> int:
        for offset in range(scan_limit):
            position = size - 1 - offset if reversed_edge else offset
            border_count = sum(
                is_border(sample[position * size:(position + 1) * size] if horizontal else sample[position::size])
                for sample in samples
            )
            if border_count < math.ceil(0.9 * count):
                return offset if offset > 1 else 0
        return scan_limit

    left, right = depth(False, False), depth(False, True)
    top, bottom = depth(True, False), depth(True, True)
    if left == right == scan_limit:
        left = right = 0
    if top == bottom == scan_limit:
        top = bottom = 0
    return left, top, size - right, size - bottom


def descriptor(image: Image.Image) -> View:
    low = image.resize((DCT_SIZE, DCT_SIZE), Image.Resampling.BOX).tobytes()
    rows = [low[start:start + DCT_SIZE] for start in range(0, len(low), DCT_SIZE)]
    row_coefficients = [
        [sum(value * weight for value, weight in zip(row, basis)) for row in rows]
        for basis in DCT_BASIS
    ]
    frequencies = [
        sum(value * weight for value, weight in zip(column, basis))
        for column in row_coefficients
        for basis in DCT_BASIS
    ][1:]
    midpoint = statistics.median(frequencies)
    perceptual_hash = sum(1 << index for index, value in enumerate(frequencies) if value > midpoint + 0.001)

    grid = image.resize((8, 8), Image.Resampling.BOX).tobytes()
    gradients = [
        grid[row * 8 + column + 1] - grid[row * 8 + column]
        for row in range(8)
        for column in range(7)
    ] + [grid[index + 8] - grid[index] for index in range(56)]
    edge_hash = sum(1 << index for index, value in enumerate(gradients) if value >= 4)
    comparisons = [
        grid[(index + offset) % len(grid)] - grid[index]
        for offset in (10, 29)
        for index in range(len(grid))
    ]
    contrast_hash = sum(1 << index for index, value in enumerate(comparisons) if value >= 8)
    brightness = statistics.fmean(grid)
    variation = statistics.pstdev(grid)
    tone = round(brightness / 8.25) << 5 | min(31, round(variation / 4))
    return perceptual_hash, edge_hash, contrast_hash, tone


def frame_descriptor(image: Image.Image) -> Frame:
    views = []
    for fraction in VIEW_CROPS:
        x = round(image.width * fraction)
        y = round(image.height * fraction)
        views.append(descriptor(image.crop((x, y, image.width - x, image.height - y))))
    return tuple(views)


def make_fingerprint(path: Path, digest: str | None = None) -> dict:
    digest = digest or file_digest(path)
    frames = video_frames(path)
    bounds = trim_box(frames)
    return {
        "algorithm": ALGORITHM,
        "sample_fps": SAMPLE_FPS,
        "sha256": digest,
        "frames": [
            [
                [f"{phash:016x}", f"{edges:028x}", f"{contrast:032x}", f"{tone:04x}"]
                for phash, edges, contrast, tone in frame_descriptor(frame.crop(bounds))
            ]
            for frame in frames
        ],
    }


def decode_frames(payload: dict) -> list[Frame]:
    if not isinstance(payload, dict) or payload.get("algorithm") != ALGORITHM or payload.get("sample_fps") != SAMPLE_FPS:
        raise ValueError("exclusion is not a supported film fingerprint")
    digest = payload.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError("exclusion has an invalid SHA-256")
    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("exclusion has no frames")

    result = []
    for frame in frames:
        if not isinstance(frame, list) or len(frame) != len(VIEW_CROPS):
            raise ValueError("exclusion has an invalid frame")
        views = []
        for view in frame:
            if not isinstance(view, list) or len(view) != 4 or any(
                not isinstance(field, str) or len(field) != width
                or any(char not in "0123456789abcdef" for char in field)
                for field, width in zip(view, (16, 28, 32, 4))
            ):
                raise ValueError("exclusion has an invalid frame descriptor")
            phash, edges, contrast, tone = (int(field, 16) for field in view)
            if phash >= 1 << 63 or tone >= 1 << 10:
                raise ValueError("exclusion frame descriptor is out of range")
            views.append((phash, edges, contrast, tone))
        result.append(tuple(views))
    return result


def frame_distance(left: Frame, right: Frame) -> float:
    best = 1.0
    for first, second in VIEW_PAIRS:
        phash_left, edges_left, contrast_left, tone_left = left[first]
        phash_right, edges_right, contrast_right, tone_right = right[second]
        brightness_delta = abs((tone_left >> 5) - (tone_right >> 5))
        local_left, local_right = tone_left & 31, tone_right & 31
        if local_left <= 1 and local_right <= 1:
            distance = brightness_delta / 31
        else:
            distance = (
                0.50 * (phash_left ^ phash_right).bit_count() / 63
                + 0.24 * (edges_left ^ edges_right).bit_count() / 112
                + 0.19 * (contrast_left ^ contrast_right).bit_count() / 128
                + 0.07 * min(1.0, (brightness_delta + abs(local_left - local_right)) / 16)
            )
        best = min(best, distance)
        if best == 0:
            break
    return best


def compare_frames(reference: list[Frame], candidate: list[Frame]) -> dict[str, float] | None:
    if min(len(reference), len(candidate)) < MIN_FRAMES:
        return None
    if min(len(reference), len(candidate)) / max(len(reference), len(candidate)) < 0.70:
        return None

    anchors = (
        round((len(reference) - 1) * fraction)
        for fraction in (0.08, 0.26, 0.44, 0.62, 0.80, 0.94)
    )
    speeds = (1.0, 0.98, 1.02, 0.96, 1.04)
    guesses = Counter()
    for reference_index in anchors:
        scores = sorted(
            (frame_distance(reference[reference_index], frame), index)
            for index, frame in enumerate(candidate)
        )
        for distance, candidate_index in scores[:5]:
            if distance <= FRAME_LIMIT:
                for speed in speeds:
                    offset = candidate_index - round(reference_index * speed)
                    guesses[(speed, offset)] += 1 - distance

    attempts = list(dict.fromkeys([(1.0, 0), *((speed, offset) for (speed, offset), _ in guesses.most_common(24))]))
    best = None
    best_score = math.inf
    for speed, offset in attempts:
        distances = []
        for index, frame in enumerate(reference):
            projected = round(index * speed) + offset
            if not 0 <= projected < len(candidate):
                continue
            candidates = candidate[max(projected - 1, 0):projected + 2]
            distances.append(min(frame_distance(frame, option) for option in candidates))
        if len(distances) < MIN_FRAMES:
            continue
        compared = min(len(distances), len(candidate))
        coverage = compared / max(len(reference), len(candidate))
        short_coverage = compared / min(len(reference), len(candidate))
        if coverage < 0.70 or short_coverage < 0.84:
            continue
        matching = sum(distance <= FRAME_LIMIT for distance in distances) / len(distances)
        mean_distance = statistics.fmean(distances)
        if matching < 0.86 or mean_distance > 0.22:
            continue
        score = mean_distance + (1 - coverage) * 0.15
        if score < best_score:
            best_score = score
            best = {"coverage": coverage, "matching_frames": matching, "mean_distance": mean_distance}
    if best is None:
        return None
    return {key: round(value, 3) for key, value in best.items()}


def load_exclusions(paths: list[Path]) -> list[tuple[dict, list[Frame]]]:
    exclusions = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload if isinstance(payload, list) else [payload]
        if not entries:
            raise ValueError("exclusion list is empty")
        exclusions.extend((entry, decode_frames(entry)) for entry in entries)
    return exclusions


def check_candidate(path: Path, paths: list[Path]) -> dict:
    exclusions = load_exclusions(paths)
    digest = file_digest(path)
    for entry, _ in exclusions:
        if digest == entry["sha256"]:
            return {"status": "excluded", "method": "sha256", "sha256": digest, "exclusion_sha256": digest}

    candidate_frames = decode_frames(make_fingerprint(path, digest))
    for entry, reference_frames in exclusions:
        evidence = compare_frames(reference_frames, candidate_frames)
        if evidence is not None:
            return {
                "status": "excluded", "method": "visual", "sha256": digest,
                "exclusion_sha256": entry["sha256"], **evidence,
            }
    return {"status": "clear", "sha256": digest, "exclusions_checked": len(exclusions)}


def write_json(payload: dict, output: Path | None = None) -> None:
    value = json.dumps(payload, separators=(",", ":")) + "\n"
    if output is None:
        print(value, end="")
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, mode="w", encoding="utf-8", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(value)
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("fingerprint", help="emit a fingerprint with no source metadata")
    make.add_argument("video", type=Path)
    make.add_argument("--output", type=Path)
    check = commands.add_parser("check", help="exit 1 if a candidate matches any exclusion")
    check.add_argument("video", type=Path)
    check.add_argument("--exclusions", type=Path, action="append", required=True, help="fingerprint object or array; repeatable")
    args = parser.parse_args()
    try:
        if args.command == "fingerprint":
            if args.output is not None and args.output.resolve() == args.video.resolve():
                raise ValueError("output would replace the video")
            write_json(make_fingerprint(args.video), args.output)
            return 0
        result = check_candidate(args.video, args.exclusions)
        write_json(result)
        return int(result["status"] == "excluded")
    except json.JSONDecodeError:
        print("fingerprint: invalid exclusion JSON", file=sys.stderr)
    except OSError:
        print("fingerprint: could not read input or write output", file=sys.stderr)
    except ValueError as error:
        print(f"fingerprint: {error}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
