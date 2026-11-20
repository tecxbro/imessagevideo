"""Cache source measurements; inspect exact native frames separately from rendering."""
import csv
from fractions import Fraction
from hashlib import sha256
from math import ceil
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from compare import intervals
from media import MediaError, audio_samples, audio_streams, digest, video_clock, video_frames, write_json


def collage(path, items, width=230, columns=5):
    if not items:
        return
    height = max(round(width * image.height / image.width) for _, image in items)
    columns = min(columns, len(items))
    canvas = Image.new("RGB", (width * columns, (height + 21) * ceil(len(items) / columns)), "#17202a")
    draw = ImageDraw.Draw(canvas)
    for n, (label, image) in enumerate(items):
        x, y = (n % columns) * width, (n // columns) * (height + 21)
        draw.text((x + 4, y + 3), label, fill="white")
        canvas.paste(image.resize((width, round(width * image.height / image.width)),
                                   Image.Resampling.LANCZOS), (x, y + 21))
    canvas.save(path)


def audio_evidence(path, clock, out):
    rate, window, hop = 48000, 960, 240
    tracks = []
    for stream in audio_streams(path):
        first, signal = audio_samples(path, stream, rate)
        start = first - clock.origin
        # Max per-channel envelope avoids hiding an onset in stereo cancellation.
        signal = np.clip(signal, -8, 8)
        positions = np.arange(0, len(signal), hop)
        rms = np.empty(len(positions))
        peak = np.empty(len(positions))
        for n, index in enumerate(positions):
            block = signal[index:index + window]
            rms[n] = np.sqrt(np.max(np.mean(block * block, axis=0)))
            peak[n] = np.max(np.abs(block))
        previous = np.r_[rms[0], rms[:-1]]
        rise = np.maximum(rms - previous, 0)
        threshold = max(0.002, float(np.quantile(rise, 0.95)))
        candidates = []
        offset = float(start)
        frame_times = np.array(clock.times, dtype=float)
        with (out / f"audio-{stream['index']}.csv").open("w", newline="") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerow(("window_start_sample", "video_relative_seconds", "rms_linear", "peak_linear", "rms_rise"))
            for n, index in enumerate(positions):
                writer.writerow((index, offset + index / rate, rms[n], peak[n], rise[n]))
        # The rising edge is usually within the 20ms analysis window, not at its first sample.
        for n in range(len(positions)):
            low, high = max(0, n - 5), min(len(rise), n + 6)
            if rise[n] > threshold and n == low + int(np.argmax(rise[low:high])):
                time = offset + (positions[n] + window / 2) / rate
                candidates.append({"approx_seconds": time,
                                   "nearest_picture_frame": int(np.argmin(np.abs(frame_times - time))),
                                   "rms_rise": float(rise[n]), "window_ms": window * 1000 / rate})
        tracks.append({"stream": stream, "measurement_sample_rate": rate, "decoded_sample_frames": len(signal),
                       "video_relative_start_seconds": str(start),
                       "video_relative_end_seconds": str(start + Fraction(len(signal), rate)),
                       "peak_linear": float(peak.max()), "onset_candidates": candidates})
    return tracks


def area_of_change(before, after, width, height):
    difference = np.abs(after.astype(np.int16) - before)
    peaks = difference.max(axis=2)
    rows, cols = np.where(peaks >= 20)
    if not rows.size:
        return float(difference.mean()), 0.0, []
    scale_x, scale_y = width / peaks.shape[1], height / peaks.shape[0]
    x, y = int(cols.min() * scale_x), int(rows.min() * scale_y)
    right, bottom = ceil((cols.max() + 1) * scale_x), ceil((rows.max() + 1) * scale_y)
    return float(difference.mean()), rows.size / peaks.size, [x, y, right - x, bottom - y]


def analyze(path, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    checksum = digest(path)
    clock = video_clock(path)
    times = clock.times
    cuts, holds, contact = [], [], {}
    last_digest, last_thumb, pending = None, None, 0
    preview_width = min(240, clock.width)
    size = (preview_width, max(1, round(preview_width * clock.height / clock.width)))
    contact_frames = set(np.linspace(0, len(times) - 1, num=min(30, len(times)), dtype=int))
    with (out / "timeline.csv").open("w", newline="") as file, video_frames(path, clock) as frames:
        table = csv.writer(file, lineterminator="\n")
        table.writerow(("frame", "pts", "seconds", "duration_pts", "rgb_sha256", "thumb_delta_mae",
                        "thumb_fraction_changed", "approx_changed_x", "y", "width", "height"))
        for index, frame in enumerate(frames):
            stamp = sha256(frame).hexdigest()
            previous_thumb = last_thumb
            thumb = np.asarray(Image.fromarray(frame).resize(size, Image.Resampling.BOX))
            mae, changed, bounds = area_of_change(previous_thumb, thumb, clock.width, clock.height) if index else (0, 0, [])
            if stamp != last_digest:
                if index - pending > 1:
                    holds.append([pending, index - 1])
                pending = index
            if changed >= 0.35 and mae >= 18:
                cuts.append({"frame": index, "thumbnail_mae": mae, "changed_fraction": changed})
                contact.setdefault(index - 1, Image.fromarray(previous_thumb))
                contact[index] = Image.fromarray(thumb)
            if index in contact_frames:
                contact[index] = Image.fromarray(thumb)
            next_pts = clock.pts[index + 1] if index + 1 < len(times) else clock.end_pts
            duration = next_pts - clock.pts[index] if next_pts is not None else ""
            table.writerow((index, clock.pts[index], float(times[index]), duration, stamp, mae, changed,
                            *(bounds or [""] * 4)))
            last_digest, last_thumb = stamp, thumb
    if len(times) - pending > 1:
        holds.append([pending, len(times) - 1])
    tracks = audio_evidence(path, clock, out)
    ordered = sorted(contact.items())
    for offset in range(0, len(ordered), 30):
        items = [(f"#{frame} · {float(times[frame]):.3f}s", img) for frame, img in ordered[offset:offset + 30]]
        collage(out / f"contact-{offset // 30:02d}.jpg", items)
    report = {"schema": 1, "source_name": Path(path).name, "source_sha256": checksum,
              "clock": clock.summary(), "picture_decoded_frames": len(times),
              "exact_pixel_hold_spans": holds, "candidate_cuts_or_fast_changes": cuts,
              "audio_tracks": tracks, "thumbnails": sorted(contact),
              "analysis_parameters": {"motion_preview_size": size, "change_pixel_floor": 20,
                                      "cut_thumbnail_mae": 18, "cut_changed_fraction": 0.35}}
    write_json(out / "analysis.json", report)
    return report


def read_range(text):
    first, sep, last = text.partition(":")
    a, b = int(first), int(last) if sep else int(first)
    if b < a or a < 0:
        raise MediaError(f"Invalid inclusive frame range {text}")
    return a, b


def inspect(path, out, ranges, rect=None, ocr=False, size=300):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    clock = video_clock(path)
    times = clock.times
    if any(end >= len(times) for _, end in ranges):
        raise MediaError(f"Maximum frame index is {len(times) - 1}")
    frames_to_export = {frame for start, end in ranges for frame in range(start, end + 1)}
    if rect is not None:
        x, y, w, h = rect
        if x < 0 or y < 0 or w < 1 or h < 1 or x + w > clock.width or y + h > clock.height:
            raise MediaError("Crop lies outside coded picture")
    text_hits, panels = {}, []
    with video_frames(path, clock) as frames:
        for i, array in enumerate(frames):
            if i not in frames_to_export:
                continue
            if rect:
                array = array[y:y + h, x:x + w]
            image = Image.fromarray(array)
            filename = out / f"frame-{i:06d}.png"
            image.save(filename)
            if ocr:
                result = subprocess.run(["tesseract", str(filename), "stdout", "--psm", "11", "tsv"],
                                        capture_output=True, text=True, check=True)
                filename.with_suffix(".tsv").write_text(result.stdout)
                ocr_rows = list(csv.DictReader(result.stdout.splitlines(), delimiter="\t"))
                text_hits[i] = [row for row in ocr_rows if row.get("text", "").strip()]
            panels.append((f"#{i} · {float(times[i]):.3f}s", image.copy()))
            if len(panels) == 20 or i == max(frames_to_export):
                collage(out / f"inspect-{i:06d}.jpg", panels, width=size)
                panels.clear()
            if i == max(frames_to_export):
                break
    write_json(out / "inspect.json", {"source_sha256": digest(path), "frames": intervals(sorted(frames_to_export)),
                                     "rect": rect, "ocr_crop_relative": text_hits})
