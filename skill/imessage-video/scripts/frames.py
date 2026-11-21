#!/usr/bin/env python3
"""Compare native decoded video frames in presentation order. See references/frame-review.md."""
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageStat

FFPROBE_ENTRIES = (
    "stream=width,height,sample_aspect_ratio,display_aspect_ratio,avg_frame_rate,time_base,start_pts,duration_ts:"
    "stream_side_data=rotation:frame=width,height,best_effort_timestamp,duration,pkt_duration"
)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect(path):
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames", "-show_streams",
        "-show_entries", FFPROBE_ENTRIES, "-of", "json", str(path),
    ])
    probe = json.loads(raw)
    frames = probe.get("frames", [])
    if not frames or not probe.get("streams"):
        raise ValueError(f"No decodable video frames in {path}")
    stream = probe["streams"][0]
    base = Fraction(stream["time_base"])
    geometry = (stream["width"], stream["height"])
    if any((frame["width"], frame["height"]) != geometry for frame in frames):
        raise ValueError(f"Frame dimensions change within {path}; split at the dimension change.")
    ticks = [f.get("best_effort_timestamp") for f in frames]
    pts = [None if t is None else int(t) * base for t in ticks]
    ordered = all(a is not None and b is not None and a < b for a, b in zip(pts, pts[1:]))
    durations = [int(f.get("duration") or f.get("pkt_duration") or 0) * base for f in frames]
    tail = None
    if durations[-1] > 0 and pts[-1] is not None:
        tail = pts[-1] + durations[-1]
    elif stream.get("start_pts") is not None and stream.get("duration_ts") is not None:
        tail = (int(stream["start_pts"]) + int(stream["duration_ts"])) * base
    rotation = next((int(d["rotation"]) % 360 for d in stream.get("side_data_list", [])
                     if "rotation" in d), 0)
    raw_sar = stream.get("sample_aspect_ratio")
    raw_dar = stream.get("display_aspect_ratio")
    effective_sar, aspect_basis = Fraction(1), "implicit square pixels"
    for ratio, basis in ((raw_sar, "sample_aspect_ratio"), (raw_dar, "display_aspect_ratio")):
        if ratio and ratio not in ("N/A", "0:1", "0:0"):
            parsed = Fraction(ratio.replace(":", "/"))
            if parsed > 0:
                effective_sar = parsed if basis == "sample_aspect_ratio" else parsed * geometry[1] / geometry[0]
                aspect_basis = basis
                break
    meta = {
        "path": str(path), "sha256": sha256(path), "width": geometry[0], "height": geometry[1],
        "sample_aspect_ratio": raw_sar, "display_aspect_ratio": raw_dar,
        "effective_sample_aspect_ratio": f"{effective_sar.numerator}:{effective_sar.denominator}",
        "sample_aspect_basis": aspect_basis, "rotation": rotation,
        "average_frame_rate": stream.get("avg_frame_rate"), "time_base": str(base),
        "frame_count": len(frames), "missing_pts": ticks.count(None),
        "strictly_increasing_pts": ordered and ticks.count(None) == 0,
        "first_pts_seconds": seconds(pts[0]), "last_pts_seconds": seconds(pts[-1]),
        "end_seconds_exclusive": seconds(tail),
    }
    return meta, pts, tail


def seconds(t):
    return None if t is None else float(t)


@contextmanager
def decoder(path):
    # Keep presentation order and every decoded frame. Probe and decode the same stream.
    proc = subprocess.Popen([
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-noautorotate", "-threads", "2",
        "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn", "-fps_mode", "passthrough",
        "-pix_fmt", "rgb24", "-c:v", "rawvideo", "-threads", "1", "-f", "rawvideo", "pipe:1",
    ], stdout=subprocess.PIPE)
    try:
        yield proc.stdout
        if proc.stdout.read(1):
            raise ValueError(f"Decoder returned more frames than ffprobe for {path}")
        if proc.wait() != 0:
            raise ValueError(f"Video decoding failed for {path}")
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.kill()
        proc.wait()


def read_frame(stream, size, index, path):
    needed = size[0] * size[1] * 3
    data = stream.read(needed)
    if len(data) != needed:
        raise ValueError(f"Incomplete decoded frame {index} in {path}")
    return Image.frombytes("RGB", size, data)


def parse_roi(text):
    try:
        name, coords = text.split(":", 1)
        x, y, width, height = map(int, coords.split(","))
        if not name or name == "full" or min(x, y) < 0 or min(width, height) <= 0:
            raise ValueError
        return name, (x, y, x + width, y + height)
    except ValueError:
        raise argparse.ArgumentTypeError("Use NAME:X,Y,WIDTH,HEIGHT, with positive dimensions.")


def write_pair(path, left, right, index, label):
    originals = []
    for im in (left, right):
        copy = im.copy()
        copy.thumbnail((720, 480))
        originals.append(copy)
    width = max(i.width for i in originals)
    canvas = Image.new("RGB", (2 * width, max(i.height for i in originals) + 24), "#222222")
    draw = ImageDraw.Draw(canvas)
    for j, (title, im) in enumerate(zip(("Source", "Output"), originals)):
        canvas.paste(im, (j * width, 24))
        draw.text((width * j + 5, 5), f"{title} | frame {index} | {label}", fill="white")
    canvas.save(path)


def signature(frame):
    return np.asarray(frame.resize((24, 16), Image.Resampling.BOX), dtype=np.int16)


def estimate_offset(source, output, window):
    # All candidate shifts use exactly the same interior source frames.
    n = min(len(source), len(output))
    window = min(window, (n - 3) // 2)
    if window < 1:
        return None
    a, b = np.stack(source[:n]), np.stack(output[:n])
    ref = a[window:n-window]
    scores = {k: float(np.abs(ref - b[window+k:n-window+k]).mean())
              for k in range(-window, window+1)}
    best = min(scores, key=lambda k: (scores[k], abs(k)))
    return {
        "best_output_minus_source_frames": best, "compared_source_frames": len(ref),
        "search_radius": window, "unaligned_mean_error": scores[0], "best_mean_error": scores[best],
        "possible_constant_offset": best != 0 and scores[0] - scores[best] >= 0.25
                                    and scores[best] <= scores[0] * 0.8,
    }


def compare(args, directory):
    paths = [args.source.resolve(), args.output.resolve()]
    (src, sp, st), (out, op, ot) = [inspect(p) for p in paths]
    dims = [(m["width"], m["height"]) for m in (src, out)]
    count = min(len(sp), len(op))
    same_size = dims[0] == dims[1]
    areas = {"full": None, **dict(args.roi)}
    if len(areas) != 1 + len(args.roi):
        raise ValueError("Each ROI needs a unique name.")
    for key, box in args.roi:
        if not same_size or box[2] > dims[0][0] or box[3] > dims[0][1]:
            raise ValueError(f"ROI {key} needs equal native dimensions and must fit within the frame.")
    errors = {key: [] for key in areas}
    maxima = {key: (-1.0, None) for key in areas}
    source_signatures, output_signatures = [], []
    worst_frame, worst_score = None, -1.0
    common_errors = [abs(a - b) for a, b in zip(sp, op) if a is not None and b is not None]
    max_pts = max(common_errors, default=None)
    tail_error = None if st is None or ot is None else abs(st - ot)
    common_issues = []
    for field in ("width", "height", "effective_sample_aspect_ratio", "rotation", "frame_count"):
        if src[field] != out[field]:
            common_issues.append(f"different {field}")
    if not all(m["strictly_increasing_pts"] for m in (src, out)):
        common_issues.append("missing or non-increasing PTS")
    issues = common_issues.copy()
    if len(common_errors) != count or max_pts != 0:
        issues.append("unmatched frame PTS")
    if tail_error is None or tail_error != 0:
        issues.append("missing or different exclusive end timestamp")

    tolerance = Fraction(str(args.max_pts_error_ms or 0)) / 1000
    within_tolerance_issues = common_issues.copy()
    if len(common_errors) != count or max_pts is None or max_pts > tolerance:
        within_tolerance_issues.append("missing or out-of-tolerance frame PTS")
    if tail_error is None or tail_error > tolerance:
        within_tolerance_issues.append("missing or out-of-tolerance exclusive end timestamp")

    cols = ["frame", "source_pts_seconds", "output_pts_seconds", "pts_error_ms", "status",
            "source_pts_ticks", "output_pts_ticks"]
    bases = [Fraction(m["time_base"]) for m in (src, out)]
    with (directory / "frames.csv").open("w", newline="") as table, decoder(paths[0]) as ds, decoder(paths[1]) as do:
        writer = csv.writer(table, lineterminator="\n")
        writer.writerow(cols + [f"mae_{key}" for key in areas])
        for i in range(max(len(sp), len(op))):
            a = read_frame(ds, dims[0], i, paths[0]) if i < len(sp) else None
            b = read_frame(do, dims[1], i, paths[1]) if i < len(op) else None
            at, bt = sp[i] if a is not None else None, op[i] if b is not None else None
            status = "paired" if i < count else ("source_only" if a is not None else "output_only")
            delta = abs(at - bt) * 1000 if at is not None and bt is not None else None
            row = [i, seconds(at), seconds(bt), seconds(delta), status,
                   int(at / bases[0]) if at is not None else None,
                   int(bt / bases[1]) if bt is not None else None]
            scores = []
            if i < count and same_size:
                diff = ImageChops.difference(a, b)
                for key, box in areas.items():
                    diff_area = diff.crop(box) if box is not None else diff
                    score = sum(ImageStat.Stat(diff_area).mean) / 3
                    scores.append(score)
                    errors[key].append(score)
                    if score > maxima[key][0]:
                        maxima[key] = (score, i)
                if args.shift_window:
                    source_signatures.append(signature(a))
                    output_signatures.append(signature(b))
            if i < count and (worst_frame is None or (scores and max(scores) > worst_score)):
                worst_score = max(scores) if scores else -1
                worst_frame = (i, a, b)
            writer.writerow(row + scores + [""] * (len(areas) - len(scores)))

    metrics = {k: {"mean_frame_mae": sum(values)/len(values), "max_frame_mae": maxima[k][0],
                   "worst_frame": maxima[k][1]} for k, values in errors.items() if values}
    if worst_frame:
        i, a, b = worst_frame
        label = "largest frame/ROI MAE" if same_size else "native dimensions differ"
        write_pair(directory / "worst.png", a, b, i, label)
    offset = estimate_offset(source_signatures, output_signatures, args.shift_window)
    failures = []
    audio = None
    if getattr(args, 'check_audio', False):
        from audio_review import compare as compare_audio
        audio = compare_audio(*paths)
        failures.extend(audio['failures'])
    if args.reject_detected_shift and (offset is None or offset["possible_constant_offset"]):
        failures.append("visual offset check is unavailable or a possible offset was detected")
    if args.require_structure_match and within_tolerance_issues:
        failures.extend(within_tolerance_issues)
    if args.max_pts_error_ms is not None:
        if (len(sp) != len(op) or len(common_errors) != count or tail_error is None or
            max([tail_error, *common_errors]) * 1000 > Fraction(str(args.max_pts_error_ms))):
            failures.append("timeline is incomplete or PTS/end exceeds the requested tolerance")
    if args.max_mae is not None and (len(sp) != len(op) or not metrics or any(
            v["max_frame_mae"] > args.max_mae for v in metrics.values())):
        failures.append("native frame MAE is unavailable for one or more frames or exceeds --max-mae")
    requested = any((args.require_structure_match, args.reject_detected_shift, audio is not None,
                     args.max_mae is not None, args.max_pts_error_ms is not None))
    return {
        "schema_version": 1, "inputs": {"source": src, "output": out}, "compared_frames": count if same_size else 0,
        "paired_indices": count, "source_only_tail_frames": len(sp)-count, "output_only_tail_frames": len(op)-count,
        "alignment": "native presentation order, paired by zero-based index, without resampling",
        "max_paired_pts_error_ms": seconds(max_pts * 1000) if max_pts is not None else None,
        "exclusive_end_error_ms": seconds(tail_error * 1000) if tail_error is not None else None,
        "structure_match": not issues, "structure_issues": issues,
        "structure_within_tolerance": not within_tolerance_issues,
        "structure_tolerance_issues": within_tolerance_issues, "roi_xyxy": dict(args.roi),
        "metrics": metrics, "possible_frame_shift": offset, "audio": audio,
        "thresholds": {"max_mae": args.max_mae, "max_pts_error_ms": args.max_pts_error_ms,
                       "require_structure_match": args.require_structure_match, "reject_detected_shift": args.reject_detected_shift},
        "limits_passed": not failures if requested else None, "failures": failures,
        "worst_pair_index": worst_frame[0] if worst_frame else None,
        "artifacts": {"all_frame_measurements": "frames.csv", "comparison_image": "worst.png"},
    }


def nonnegative(value):
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("Use a finite number greater than or equal to 0.")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--roi", type=parse_roi, action="append", default=[])
    parser.add_argument("--max-mae", type=nonnegative, help="Maximum single-frame RGB MAE, 0–255, for full frame and every ROI")
    parser.add_argument("--max-pts-error-ms", type=nonnegative, help="Includes exclusive end and paired absolute PTS")
    parser.add_argument("--require-structure-match", action="store_true")
    parser.add_argument("--check-audio", action="store_true", help="Compare presented audio coverage, cue timing and spectrum")
    parser.add_argument("--reject-detected-shift", action="store_true", help="Fail on a possible constant offset or unavailable offset check")
    parser.add_argument("--shift-window", type=int, default=5, help="Offset hint search radius in frames, 0 disables")
    args = parser.parse_args()
    if args.reject_detected_shift and args.shift_window == 0:
        parser.error("--reject-detected-shift requires a positive --shift-window")
    if args.shift_window < 0:
        parser.error("--shift-window must be nonnegative")
    if any((args.out / name).resolve() in (args.source.resolve(), args.output.resolve())
           for name in ("report.json", "frames.csv", "worst.png")):
        parser.error("Choose an evidence directory distinct from the source and output videos.")
    try:
        args.out.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=args.out) as scratch:
            stage = Path(scratch)
            report = compare(args, stage)
            (stage / "report.json").write_text(json.dumps(report, indent=2) + "\n")
            for name in ("frames.csv", "worst.png", "report.json"):
                (stage / name).replace(args.out / name)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"frames.py: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"report": str(args.out / "report.json"), "compared_frames": report["compared_frames"],
                      "limits_passed": report["limits_passed"], "failures": report["failures"]}))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
