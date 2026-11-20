"""Resolve landmarks from decoded picture pixels and presentation timestamps."""

from fractions import Fraction
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryFile

import numpy as np
from PIL import Image


def _picture_frames(picture):
    command = [
        "ffprobe", "-v", "error", "-select_streams", "V:0", "-show_frames",
        "-show_entries", "stream=width,height,time_base:frame=best_effort_timestamp,width,height",
        "-of", "json", str(picture),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode or result.stderr.strip():
        raise ValueError(f"{picture}: timestamp probe failed: {result.stderr.strip()}")
    probe = json.loads(result.stdout)
    try:
        stream = probe["streams"][0]
        width, height = stream["width"], stream["height"]
        ticks = [int(frame["best_effort_timestamp"]) for frame in probe["frames"]]
        time_base = Fraction(stream["time_base"])
    except (KeyError, IndexError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{picture}: missing decoded frame dimensions or timestamps") from exc
    if not ticks or width <= 0 or height <= 0 or time_base <= 0:
        raise ValueError(f"{picture}: invalid video dimensions or clock")
    if any(right <= left for left, right in zip(ticks, ticks[1:])):
        raise ValueError(f"{picture}: video timestamps must strictly increase")
    if any((frame.get("width"), frame.get("height")) != (width, height) for frame in probe["frames"]):
        raise ValueError(f"{picture}: video dimensions change within the cut")
    return width, height, [(tick - ticks[0]) * time_base for tick in ticks]


def _pixel_box(roi, width, height):
    if not isinstance(roi, (list, tuple)) or len(roi) != 4:
        raise ValueError("expected roi = [left, top, width, height] in normalized coordinates")
    left, top, span_x, span_y = (Fraction(str(value)) for value in roi)
    right, bottom = left + span_x, top + span_y
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ValueError("ROI must fit within the picture and have positive width and height")
    x0, y0 = round(left * width), round(top * height)
    x1, y1 = round(right * width), round(bottom * height)
    if x0 >= x1 or y0 >= y1:
        raise ValueError("ROI is smaller than one pixel at this resolution")
    return x0, y0, x1, y1


def _sampled_size(width, height):
    scale = min(1, 128 / max(width, height))
    return max(1, round(width * scale)), max(1, round(height * scale))


def _fraction(value, label):
    value = float(value)
    if not 0 <= value <= 1:
        raise ValueError(f"{label} must be between 0 and 1")
    return value


def _scorer(detector, shape, base_dir):
    if ("color" in detector) == ("template" in detector):
        raise ValueError("set exactly one of color or template")

    if "color" in detector:
        color = detector["color"]
        if not isinstance(color, (list, tuple)) or len(color) != 3 or any(
            type(channel) is not int or not 0 <= channel <= 255 for channel in color
        ):
            raise ValueError("color must contain three integer RGB channels in [0,255]")
        target = np.asarray(color, dtype=np.int16)
        tolerance = detector.get("tolerance", 24)
        if type(tolerance) is not int or not 0 <= tolerance <= 255:
            raise ValueError("tolerance must be an integer in [0,255]")
        threshold = _fraction(detector.get("min_fraction", 0.5), "min_fraction")
        if threshold == 0:
            raise ValueError("min_fraction must be greater than zero")

        def score(frame):
            distance = np.abs(frame - target).max(axis=-1)
            return float(np.count_nonzero(distance <= tolerance) / distance.size)

        return score, threshold

    path = base_dir / detector["template"]
    with Image.open(path) as image:
        image = image.convert("RGB")
        if "template_roi" in detector:
            image = image.crop(_pixel_box(detector["template_roi"], *image.size))
        target = np.asarray(image.resize(shape, Image.Resampling.BOX), dtype=np.int16)
    threshold = 1 - _fraction(detector.get("max_distance", 0.08), "max_distance")

    def score(frame):
        return float(1 - np.abs(frame - target).mean() / 255)

    return score, threshold


def _rgb_frames(picture, box, size, frame_count):
    x0, y0, x1, y1 = box
    width, height = size
    filter_graph = f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0}:exact=1,format=rgb24"
    if size != (x1 - x0, y1 - y0):
        filter_graph += f",scale={width}:{height}:flags=area"
    command = [
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-filter_threads", "1", "-noautorotate",
        "-i", str(picture), "-map", "0:V:0", "-vf", filter_graph, "-pix_fmt", "rgb24",
        "-c:v", "rawvideo", "-threads:v", "1", "-fps_mode", "passthrough", "-f", "rawvideo",
        "pipe:1",
    ]
    bytes_per_frame = width * height * 3
    with TemporaryFile() as errors, subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=errors
    ) as process:
        for index in range(frame_count):
            raw = process.stdout.read(bytes_per_frame)
            if len(raw) != bytes_per_frame:
                process.stdout.close()
                process.wait()
                errors.seek(0)
                detail = errors.read().decode(errors="replace").strip()
                raise ValueError(f"decoded picture stopped before frame {index}. {detail}")
            yield np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 3)
        if process.stdout.read(1):
            process.stdout.close()
            process.wait()
            raise ValueError("picture decode returned more frames than the timestamp probe")
        if process.wait():
            errors.seek(0)
            raise ValueError(f"picture decode failed: {errors.read().decode(errors='replace').strip()}")


def _detect(detector, scores, threshold, stamps):
    settle = detector.get("settle_frames", 1)
    if type(settle) is not int or settle < 1:
        raise ValueError("settle_frames must be a positive integer")
    allow_initial = detector.get("allow_initial", False)
    if type(allow_initial) is not bool:
        raise ValueError("allow_initial must be a boolean")
    start, end = stamps[0], stamps[-1]
    if "search_s" in detector:
        interval = detector["search_s"]
        if not isinstance(interval, (list, tuple)) or len(interval) != 2:
            raise ValueError("search_s must contain two picture-relative times in seconds")
        start, end = (Fraction(str(value)) for value in interval)
        if not 0 <= start <= end:
            raise ValueError("search_s must be a nonnegative, increasing time interval")

    matches = [score >= threshold for score in scores]
    candidates = [
        index for index in range(0 if allow_initial else 1, len(scores) - settle + 1)
        if start <= stamps[index] <= end
        and (index == 0 or not matches[index - 1])
        and all(matches[index:index + settle])
    ]
    if not candidates:
        peak = max(scores)
        raise ValueError(f"no visible absent-to-present transition (peak score {peak:.3f}, threshold {threshold:.3f})")
    if len(candidates) > 1:
        frames = ", ".join(f"{index} at {float(stamps[index]):.3f}s" for index in candidates)
        raise ValueError(f"ambiguous visible transition; matched frames {frames}")
    frame = candidates[0]
    return {"frame": frame, "pts": stamps[frame], "score": scores[frame]}


def resolve_landmarks(picture: Path, detectors: dict, base_dir: Path | None = None) -> dict:
    """Find a unique visible absent-to-present boundary for each landmark ID.

    Every detector has normalized roi=[left, top, width, height], measured on
    decoded pixels in stored orientation. Use either color=[R,G,B] with
    tolerance (default 24, per channel) and min_fraction (default 0.5), or
    template="after.png" with max_distance (default 0.08, mean RGB error /
    255). A full frame template can supply template_roi. Templates are
    resolved relative to base_dir, or the working directory if omitted.
    Crops wider or taller than 128 px are area-downsampled.

    Optional settle_frames requires that many consecutive matches and still
    returns the first matched frame. Set allow_initial=true to allow a match
    on frame zero, such as a visible opening title. Optional inclusive
    search_s=[start,end] disambiguates repeated visual events. A search
    boundary cannot create a match. Keep this window independent of cue
    placement and wide enough for expected picture edits. Frames start at
    zero. pts is an exact Fraction in seconds from the first displayed frame.
    score is matched color fraction or 1 minus the normalized template distance.
    """
    picture = Path(picture).resolve()
    base_dir = Path.cwd() if base_dir is None else Path(base_dir)
    if not detectors:
        return {}
    width, height, stamps = _picture_frames(picture)
    resolved = {}
    for name, detector in detectors.items():
        try:
            box = _pixel_box(detector.get("roi"), width, height)
            size = _sampled_size(box[2] - box[0], box[3] - box[1])
            score, threshold = _scorer(detector, size, base_dir)
            scores = [score(frame) for frame in _rgb_frames(picture, box, size, len(stamps))]
            resolved[name] = _detect(detector, scores, threshold, stamps)
        except (AttributeError, OSError, TypeError, ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"landmark {name!r}: {exc}") from exc
    return resolved
