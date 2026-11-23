#!/usr/bin/env python3
"""Compare two local moving pictures at an explicitly selected event frame."""

import argparse
from bisect import bisect_right
from fractions import Fraction
from hashlib import file_digest
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont


BACKGROUND = "#161b21"
GAP = 8
CAPTION = 44


def probe(path):
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-show_frames",
        "-show_entries", "stream=width,height,time_base:frame=best_effort_timestamp,duration,pkt_duration",
        "-of", "json", str(path),
    ]))
    stream = data["streams"][0]
    time_base = Fraction(stream["time_base"])
    times = [int(frame["best_effort_timestamp"]) * time_base for frame in data["frames"]]
    if not times or any(right < left for left, right in zip(times, times[1:])):
        raise ValueError(f"Expected ordered video timestamps in {path}")
    last_frame = data["frames"][-1]
    last_duration = int(last_frame.get("duration", last_frame.get("pkt_duration", 0)))
    with path.open("rb") as source:
        sha256 = file_digest(source, "sha256").hexdigest()
    return {
        "path": path, "times": times, "end": times[-1] + time_base * last_duration,
        "width": stream["width"], "height": stream["height"], "sha256": sha256,
        "rounding": min(time_base, Fraction(1, 1_000_000)),
    }


def select_frames(source, anchor, offsets, fps):
    times = source["times"]
    if not 0 <= anchor < len(times):
        raise ValueError(f"Anchor frame {anchor} is outside {source['path']}")
    requested = [times[anchor] + Fraction(offset, fps) for offset in offsets]
    if requested[0] < times[0] or requested[-1] > max(times[-1], source["end"]):
        raise ValueError(f"Comparison reaches outside {source['path']}. Reduce --before or --after.")
    return [anchor if offset == 0 else bisect_right(times, time + source["rounding"]) - 1
            for offset, time in zip(offsets, requested)]


def decode(source, first, last, size, directory):
    width, height = size
    directory.mkdir()
    filters = (
        f"select='between(n,{first},{last})',"
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x161b21,setsar=1,"
        "setpts=N/TB"
    )
    # Output timestamps only transport decoded pictures. The comparison is driven by probe().
    subprocess.run([
        "ffmpeg", "-v", "error", "-threads", "1", "-filter_threads", "1", "-i", str(source["path"]),
        "-map", "0:v:0", "-an", "-vf", filters, "-fps_mode", "passthrough",
        "-start_number", str(first), "-c:v", "png", "-threads", "1", str(directory / "%06d.png"),
    ], check=True)
    if sum(1 for _ in directory.glob("*.png")) != last - first + 1:
        raise ValueError(f"Unexpected decoded range from {source['path']}")


def panel(directory, index, size, label, pts_ms):
    width, height = size
    result = Image.new("RGB", (width, height + CAPTION), BACKGROUND)
    with Image.open(directory / f"{index:06d}.png") as picture:
        result.paste(picture, (0, 0))
    draw = ImageDraw.Draw(result)
    draw.text((8, height + 4), label, fill="#ffffff", font=ImageFont.load_default(size=13))
    draw.text((8, height + 21), f"frame {index}   PTS {pts_ms:.1f} ms", fill="#bac5d1",
              font=ImageFont.load_default(size=12))
    return result


def contact_sheet(pictures, path, columns):
    width, height = pictures[0].size
    rows = (len(pictures) + columns - 1) // columns
    sheet = Image.new("RGB", (width * columns, height * rows), BACKGROUND)
    for index, picture in enumerate(pictures):
        sheet.paste(picture, ((index % columns) * width, (index // columns) * height))
    sheet.save(path)


def ordinal_window(source, anchor, count):
    first = max(0, anchor - (count - 1) // 3)
    last = min(len(source["times"]), first + count)
    return range(max(0, last-count), last)


def compare(args):
    source_paths = [args.reference, args.render]
    labels = [args.reference_label, args.render_label]
    anchors = [args.reference_frame, args.render_frame]
    offsets = list(range(-args.before, args.after + 1))
    sources = [probe(path) for path in source_paths]
    selected = [select_frames(source, anchor, offsets, args.fps)
                for source, anchor in zip(sources, anchors)]
    intervals = [ordinal_window(source, anchor, args.consecutive)
                 for source, anchor in zip(sources, anchors)]
    width, height = args.panel
    composite_width = width * 2 + GAP
    composite_height = height + CAPTION + 24
    output_frames = len(offsets)
    checkpoints = {0, args.before, output_frames - 1}
    # Show both slower settlement and near-onset motion in the paired sheet.
    checkpoints.update(args.before + offset for offset in (-2, 1, 3, 6, 12, 24)
                       if 0 <= args.before + offset < output_frames)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="messages-compare-") as temp:
        directories = [Path(temp) / kind for kind in ("reference", "render")]
        for source, indices, interval, directory, label in zip(sources, selected, intervals, directories, labels):
            needed = list(interval) + indices
            decode(source, min(needed), max(needed), args.panel, directory)
            consecutive = [panel(directory, index, args.panel, label, float(source["times"][index]) * 1000)
                           for index in interval]
            contact_sheet(consecutive, args.out_dir / f"{directory.name}-consecutive.png", min(5, len(interval)))

        evidence = []
        video_tmp = args.out_dir / ".comparison.pending.mp4"
        try:
            with subprocess.Popen([
                "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                "-video_size", f"{composite_width}x{composite_height}", "-framerate", str(args.fps),
                "-i", "pipe:", "-an", "-c:v", "libx264", "-threads", "2", "-crf", "16",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_tmp),
            ], stdin=subprocess.PIPE) as encoder:
                for comparison_frame, (offset, *indices) in enumerate(zip(offsets, *selected)):
                    image = Image.new("RGB", (composite_width, composite_height), BACKGROUND)
                    for column, (source, label, directory, index) in enumerate(zip(sources, labels, directories, indices)):
                        picture = panel(directory, index, args.panel, label, float(source["times"][index]) * 1000)
                        image.paste(picture, (column * (width + GAP), 24))
                    ImageDraw.Draw(image).text((8, 4), f"Event {offset / args.fps * 1000:+.1f} ms",
                                               fill="#e0eaf2", font=ImageFont.load_default(size=12))
                    if comparison_frame in checkpoints:
                        evidence.append(image)
                    encoder.stdin.write(image.tobytes())
                encoder.stdin.close()
                if encoder.wait():
                    raise ValueError("FFmpeg could not encode comparison.mp4")
            video_tmp.replace(args.out_dir / "comparison.mp4")
        finally:
            video_tmp.unlink(missing_ok=True)

    contact_sheet(evidence, args.out_dir / "checkpoints.png", min(3, len(evidence)))
    report = {
        "fps": args.fps, "anchorComparisonFrame": args.before,
        "sampling": "most recent display timestamp at each event-relative render time, allowing up to 1 µs for PTS rounding",
        "sources": [{
            "label": label, "file": source["path"].name, "sha256": source["sha256"],
            "sizePx": [source["width"], source["height"]], "decodedFrames": len(source["times"]),
            "anchorFrame": anchor, "anchorPTS": str(source["times"][anchor]),
            "consecutiveFrames": [interval.start, interval.stop-1],
        } for source, label, anchor, interval in zip(sources, labels, anchors, intervals)],
        "pairs": [{
            "comparisonFrame": index, "relativeTime": str(Fraction(offset, args.fps)),
            "referenceFrame": ref, "referencePTS": str(sources[0]["times"][ref]),
            "renderFrame": render, "renderPTS": str(sources[1]["times"][render]),
        } for index, (offset, ref, render) in enumerate(zip(offsets, *selected))],
    }
    (args.out_dir / "alignment.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"{args.out_dir / 'comparison.mp4'} ({output_frames} frames at {args.fps} fps)")


def panel_size(value):
    try:
        width, height = map(int, value.split("x"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected even WIDTHxHEIGHT, both at least 160") from error
    if min(width, height) < 160 or width % 2 or height % 2:
        raise argparse.ArgumentTypeError("expected even WIDTHxHEIGHT, both at least 160")
    return width, height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("render", type=Path)
    parser.add_argument("--reference-frame", required=True, type=int, help="zero-based decoded first action frame")
    parser.add_argument("--render-frame", required=True, type=int, help="zero-based decoded first action frame")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--reference-label", default="Reference capture")
    parser.add_argument("--render-label", default="Editable scene")
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--before", type=int, default=12, help="comparison frames before the event")
    parser.add_argument("--after", type=int, default=70, help="comparison frames after the event")
    parser.add_argument("--consecutive", type=int, default=20, help="original adjacent frames per contact sheet")
    parser.add_argument("--panel", type=panel_size, default=(260, 564))
    args = parser.parse_args()
    if args.fps < 1 or min(args.before, args.after) < 0 or not 1 <= args.consecutive <= 40:
        parser.error("fps must be positive, before/after cannot be negative, and consecutive must be 1–40")
    try:
        compare(args)
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
