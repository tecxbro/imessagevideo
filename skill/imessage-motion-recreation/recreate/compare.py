"""Compare all decoded pictures and explicitly gate the clock and local interaction windows."""
from contextlib import ExitStack
from fractions import Fraction
from itertools import zip_longest
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from media import MediaError, audio_samples, audio_streams, digest, video_clock, video_frames, write_json


def intervals(indices):
    spans = []
    for frame in indices:
        if spans and spans[-1][1] + 1 == frame:
            spans[-1][1] = frame
        else:
            spans.append([frame, frame])
    return spans


def load_checks(path, clock):
    data = json.loads(Path(path).read_text()) if path else {}
    unknown = data.keys() - {"global_mae", "pixel_floor", "regions", "clock_tolerance_seconds", "audio", "audio_checks", "tile"}
    if unknown:
        raise MediaError(f"Unknown check keys: {', '.join(sorted(unknown))}")
    global_limit = data.get("global_mae", 2)
    default_floor = data.get("pixel_floor", 20)
    clock_tolerance = Fraction(str(data.get("clock_tolerance_seconds", 0)))
    audio = data.get("audio", "observe")
    if not 0 <= global_limit <= 255 or not 0 < default_floor <= 255 or clock_tolerance < 0:
        raise MediaError("Invalid global_mae, pixel_floor or clock tolerance")
    if audio not in ("observe", "silent", "present"):
        raise MediaError("audio must be observe, silent or present")
    regions = []
    seen = set()
    for region in data.get("regions", []):
        unknown = region.keys() - {"id", "start", "end", "rect", "rects", "mae", "pixel_floor", "changed_pixels"}
        if unknown:
            raise MediaError(f"Unknown region keys: {', '.join(sorted(unknown))}")
        name, start, end = region["id"], region["start"], region["end"]
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise MediaError(f"Missing or duplicate region id {name!r}")
        if not (type(start) is int and type(end) is int and 0 <= start <= end < len(clock.pts)):
            raise MediaError(f"{name}: window must be an inclusive span of reference frames")
        if ("rect" in region) == ("rects" in region):
            raise MediaError(f"{name}: specify rect or frame-by-frame rects")
        rects = region.get("rects", [region.get("rect")] * (end - start + 1))
        if len(rects) != end - start + 1:
            raise MediaError(f"{name}: rects must cover every frame in the window")
        slices = []
        for rect in rects:
            if len(rect) != 4 or any(type(value) is not int for value in rect):
                raise MediaError(f"{name}: expected integer [x,y,width,height] in coded pixels")
            x, y, width, height = rect
            if min(x, y) < 0 or min(width, height) < 1 or x + width > clock.width or y + height > clock.height:
                raise MediaError(f"{name}: rectangle {rect} is outside the native raster")
            slices.append((slice(y, y + height), slice(x, x + width)))
        mae, floor, pixels = region.get("mae"), region.get("pixel_floor", default_floor), region.get("changed_pixels")
        if mae is None and pixels is None:
            raise MediaError(f"{name}: specify mae, changed_pixels or both")
        if ((mae is not None and not 0 <= mae <= 255) or not 0 < floor <= 255
                or (pixels is not None and (type(pixels) is not int or pixels < 0
                    or any(pixels >= rect[2] * rect[3] for rect in rects)))):
            raise MediaError(f"{name}: invalid regional threshold")
        regions.append((name, start, end, rects, slices, mae, floor, pixels))
        seen.add(name)
    tile = data.get("tile")
    if tile is not None:
        if (set(tile) != {"size", "mae"} or type(tile["size"]) is not int
                or tile["size"] < 2 or not 0 <= tile["mae"] <= 255):
            raise MediaError("tile requires integer size >= 2 and mae from 0 to 255")
    return global_limit, default_floor, clock_tolerance, audio, regions, tile, data.get("audio_checks")


def strip(path, pairs, label, crop=None, width=220):
    """Each row is reference, candidate, and magnified absolute RGB difference."""
    images = []
    for index, reference, candidate in pairs:
        if crop:
            reference, candidate = reference[crop], candidate[crop]
        delta = np.abs(reference.astype(np.int16) - candidate)
        panels = [Image.fromarray(item) for item in
                  (reference, candidate, np.minimum(delta * 4, 255).astype(np.uint8))]
        scale = min(width / panels[0].width, 320 / panels[0].height)
        panel_size = (max(1, round(scale * panels[0].width)), max(1, round(scale * panels[0].height)))
        resampling = Image.Resampling.NEAREST if crop else Image.Resampling.LANCZOS
        images.append((index, panel_size[1], [panel.resize(panel_size, resampling) for panel in panels]))
    if not images:
        return
    canvas = Image.new("RGB", (width * 3, 25 + sum(height + 20 for _, height, _ in images)), "#171717")
    draw = ImageDraw.Draw(canvas)
    draw.text((5, 5), label, fill="white")
    y = 25
    for index, height, panels in images:
        draw.text((5, y), f"Frame {index}   reference / candidate / difference ×4", fill="white")
        for column, panel in enumerate(panels):
            canvas.paste(panel, (width * column + (width - panel.width) // 2, y + 20))
        y += height + 20
    canvas.save(path)



def audio_checks_for(config, reference, ref_clock, ref_streams, candidate, enc_clock, enc_streams):
    """Check decoded start alignment and soundtrack energy around authored picture events."""
    if config is None:
        return [], None
    if set(config) - {"max_start_delta_seconds", "cues"}:
        raise MediaError("Only max_start_delta_seconds and cues are supported in audio_checks")
    if not enc_streams:
        return [{"check": "audio_missing_for_checks"}], None
    rate = 48000
    origin, samples = audio_samples(candidate, enc_streams[0], rate)
    enc_start = origin - enc_clock.origin
    failures, observations = [], {"candidate_start_seconds": str(enc_start), "cues": []}
    if "max_start_delta_seconds" in config:
        tolerance = Fraction(str(config["max_start_delta_seconds"]))
        if tolerance < 0 or not ref_streams:
            raise MediaError("Audio start comparison needs a nonnegative tolerance and reference audio")
        ref_origin, _ = audio_samples(reference, ref_streams[0], rate)
        ref_start = ref_origin - ref_clock.origin
        observations["reference_start_seconds"] = str(ref_start)
        if abs(ref_start - enc_start) > tolerance:
            failures.append({"check": "audio_relative_start", "delta_seconds": str(enc_start - ref_start)})
    enc_times = enc_clock.times
    for cue in config.get("cues", []):
        if set(cue) != {"id", "frame", "offset_ms", "window_ms", "min_peak"}:
            raise MediaError("Audio cue needs id, frame, offset_ms, window_ms and min_peak")
        frame, offset, window, peak_limit = cue["frame"], cue["offset_ms"], cue["window_ms"], cue["min_peak"]
        if type(frame) is not int or not 0 <= frame < len(ref_clock.pts) or window <= 0 or not 0 < peak_limit <= 8:
            raise MediaError(f"Invalid audio cue {cue['id']}")
        peak = None
        if frame < len(enc_times):
            center = (enc_times[frame] - enc_start) * rate + Fraction(str(offset)) * rate / 1000
            half = Fraction(str(window)) * rate / 2000
            lo, hi = max(0, round(center - half)), min(len(samples), round(center + half) + 1)
            if hi > lo:
                peak = float(np.max(np.abs(samples[lo:hi])))
        observations["cues"].append({**cue, "observed_peak": peak})
        if peak is None or peak < peak_limit:
            failures.append({"check": "audio_cue", "id": cue["id"], "frame": frame, "observed_peak": peak})
    return failures, observations


def worst_tile(delta, size):
    """Rectangular overlapping tiles. Integral image evaluates each native pixel-aligned lattice position."""
    height, width = delta.shape[:2]
    w, h = min(size, width), min(size, height)
    stride = max(1, size // 2)
    xs = np.r_[np.arange(0, width - w, stride), width - w]
    ys = np.r_[np.arange(0, height - h, stride), height - h]
    summed = np.pad(delta.sum(axis=2, dtype=np.int64).cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)))
    totals = (summed[np.ix_(ys + h, xs + w)] - summed[np.ix_(ys, xs + w)]
              - summed[np.ix_(ys + h, xs)] + summed[np.ix_(ys, xs)])
    row, col = np.unravel_index(np.argmax(totals), totals.shape)
    return float(totals[row, col] / (3 * w * h)), [int(xs[col]), int(ys[row]), w, h]

def compare(reference, candidate, out, checks=None, sheets=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ref, enc = video_clock(reference), video_clock(candidate)
    global_limit, pixel_floor, tolerance, audio_rule, regions, tile, audio_config = load_checks(checks, ref)
    ref_times, enc_times = ref.times, enc.times
    clock_mismatch = [i for i, (a, b) in enumerate(zip(ref_times, enc_times)) if abs(a - b) > tolerance]
    missing = list(range(len(enc.pts), len(ref.pts)))
    extra = list(range(len(ref.pts), len(enc.pts)))
    dimensions_match = (ref.width, ref.height) == (enc.width, enc.height)
    display_match = (dimensions_match and ref.sar == enc.sar and ref.orientation == enc.orientation
                     and ref.display_matrix == enc.display_matrix and ref.crop == enc.crop)
    failures = []
    if ref.has_alpha or enc.has_alpha:
        failures.append({"check": "unsupported_alpha_comparison",
                         "reference_alpha": ref.has_alpha, "candidate_alpha": enc.has_alpha})
    if missing:
        failures.append({"check": "missing_candidate_frames", "spans": intervals(missing)})
    if extra:
        failures.append({"check": "extra_candidate_frames", "spans": intervals(extra)})
    if not display_match:
        failures.append({"check": "display_geometry"})
    color_tags = ("color_transfer", "color_primaries")
    unspecified = (None, "unknown", "unspecified")
    color_differences = {
        tag: {"reference": ref.stream.get(tag), "candidate": enc.stream.get(tag)}
        for tag in color_tags
        if ref.stream.get(tag) != enc.stream.get(tag)
        and (ref.stream.get("color_transfer") in ("smpte2084", "arib-std-b67")
             or enc.stream.get("color_transfer") in ("smpte2084", "arib-std-b67")
             or (ref.stream.get(tag) not in unspecified and enc.stream.get(tag) not in unspecified))
    }
    if color_differences:
        failures.append({"check": "display_color", "tags": color_differences})
    if clock_mismatch:
        failures.append({"check": "presentation_clock", "spans": intervals(clock_mismatch)})
    if ref.end is None or enc.end is None:
        failures.append({"check": "unmeasured_final_hold"})
    elif abs(ref.end - enc.end) > tolerance:
        failures.append({"check": "final_hold", "frame": len(ref.pts) - 1,
                         "reference_end_seconds_rational": str(ref.end), "candidate_end_seconds_rational": str(enc.end)})
    ref_audio = audio_streams(reference)
    enc_audio = audio_streams(candidate)
    if (audio_rule == "silent" and enc_audio) or (audio_rule == "present" and not enc_audio):
        failures.append({"check": f"audio_{audio_rule}", "candidate_audio_streams": len(enc_audio)})

    audio_failures, audio_result = audio_checks_for(audio_config, reference, ref, ref_audio, candidate, enc, enc_audio)
    failures.extend(audio_failures)

    bad_global, bad_tiles = [], []
    worst_local_tile = None
    region_stats = {region[0]: {"expected_frames": region[2] - region[1] + 1, "scanned_frames": 0,
                               "worst_mae": 0, "worst_changed_pixels": 0, "bad": [],
                               "mae_limit": region[5], "pixel_floor": region[6], "changed_pixels_limit": region[7]}
                    for region in regions}
    timeline_fields = ("frame", "reference_pts", "candidate_pts", "reference_seconds", "candidate_seconds",
                       "clock_delta_ms", "mean_abs_rgb", "pixels_above_floor", "max_abs_rgb", "tile_mae", "tile_rect", "status")
    local_fields = ("id", "frame", "x", "y", "width", "height", "mean_abs_rgb", "pixels_above_floor", "status")
    count, sum_mae, worst = 0, 0.0, None
    final_pair = None
    max_pair = None
    with ExitStack() as stack:
        ref_frames = stack.enter_context(video_frames(reference, ref))
        enc_frames = stack.enter_context(video_frames(candidate, enc))
        table = csv.writer(stack.enter_context((out / "frames.csv").open("w", newline="")), lineterminator="\n")
        local = csv.writer(stack.enter_context((out / "regions.csv").open("w", newline="")), lineterminator="\n")
        table.writerow(timeline_fields)
        local.writerow(local_fields)
        for i, (a, b) in enumerate(zip_longest(ref_frames, enc_frames)):
            a_time = ref_times[i] if a is not None else None
            b_time = enc_times[i] if b is not None else None
            row = [
                i, ref.pts[i] if a is not None else "", enc.pts[i] if b is not None else "",
                float(a_time) if a_time is not None else "", float(b_time) if b_time is not None else "",
            ]
            if a is None or b is None:
                table.writerow([*row, "", "", "", "", "", "", "extra" if a is None else "missing"])
                continue
            clock_ms = float((b_time - a_time) * 1000)
            if not display_match:
                table.writerow([*row, clock_ms, "", "", "", "", "", "display_geometry"])
                continue
            delta = np.maximum(a, b) - np.minimum(a, b)
            peak_by_pixel = np.maximum(np.maximum(delta[:, :, 0], delta[:, :, 1]), delta[:, :, 2])
            mae = float(delta.mean())
            count += 1
            sum_mae += mae
            if worst is None or mae > worst["mean_abs_rgb"]:
                worst = {"frame": i, "mean_abs_rgb": mae}
                if sheets:
                    max_pair = (i, a, b)
            if sheets:
                final_pair = (i, a, b)
            clock_bad = abs(a_time - b_time) > tolerance
            if mae > global_limit:
                bad_global.append(i)
            tile_mae, tile_rect = worst_tile(delta, tile["size"]) if tile else ("", [])
            tile_bad = tile is not None and tile_mae > tile["mae"]
            if tile_bad:
                bad_tiles.append(i)
            if tile and (worst_local_tile is None or tile_mae > worst_local_tile["mae"]):
                worst_local_tile = {"frame": i, "rect": tile_rect, "mae": tile_mae}
            table.writerow([*row, clock_ms, mae, int(np.count_nonzero(peak_by_pixel >= pixel_floor)),
                            int(peak_by_pixel.max()), tile_mae, " ".join(map(str, tile_rect)),
                            "fail" if clock_bad or mae > global_limit or tile_bad else "pass"])
            for region_i, (name, start, end, rects, slices, mae_limit, floor, pixel_limit) in enumerate(regions):
                if not start <= i <= end:
                    continue
                region_slice = slices[i - start]
                area = delta[region_slice]
                local_mae = float(area.mean())
                peaks = peak_by_pixel[region_slice]
                changed = int(np.count_nonzero(peaks >= floor))
                failed = ((mae_limit is not None and local_mae > mae_limit) or
                          (pixel_limit is not None and changed > pixel_limit))
                stats = region_stats[name]
                stats["scanned_frames"] += 1
                stats["worst_mae"] = max(stats["worst_mae"], local_mae)
                stats["worst_changed_pixels"] = max(stats["worst_changed_pixels"], changed)
                if failed:
                    stats["bad"].append(i)
                local.writerow([name, i, *rects[i - start], local_mae, changed, "fail" if failed else "pass"])
                if sheets:
                    cases = stats.setdefault("image_cases", [])
                    cases.append((i, a[region_slice].copy(), b[region_slice].copy()))
                    if len(cases) == 12 or i == end:
                        strip(out / f"region-{region_i:02d}-{(i - start) // 12:02d}.png", cases, name)
                        cases.clear()

    if bad_tiles:
        failures.append({"check": "local_tile_mae", "spans": intervals(bad_tiles)})
    if bad_global:
        failures.append({"check": "whole_frame_mae", "spans": intervals(bad_global)})
    for region_i, (name, stats) in enumerate(region_stats.items()):
        bad = stats.pop("bad")
        stats["failed_spans"] = intervals(bad)
        if bad:
            failures.append({"check": "region", "id": name, "spans": stats["failed_spans"]})
        if stats["scanned_frames"] != stats["expected_frames"]:
            failures.append({"check": "incomplete_region", "id": name})
        captures = stats.pop("image_cases", [])
        if captures:
            offset = (stats["scanned_frames"] - 1) // 12
            strip(out / f"region-{region_i:02d}-{offset:02d}.png", captures, name)
    if sheets and max_pair is not None:
        key_frames = {item[0]: item for item in (max_pair, final_pair)}
        strip(out / "whole-frame.png", list(key_frames.values()), "Peak error and last comparable picture")
    report = {
        "schema": 1, "verdict": "FAIL" if failures else "PASS", "failures": failures,
        "reference": {"name": Path(reference).name, "sha256": digest(reference), "clock": ref.summary(), "audio": ref_audio},
        "candidate": {"name": Path(candidate).name, "sha256": digest(candidate), "clock": enc.summary(), "audio": enc_audio},
        "compared_frames": count, "mean_abs_rgb": sum_mae / count if count else None, "worst_frame": worst,
        "whole_frame_mae_limit": global_limit, "pixel_floor": pixel_floor,
        "clock_tolerance_seconds": str(tolerance), "alignment": "display-order index with independent exact PTS gate",
        "audio_rule": audio_rule, "audio_checks": audio_result, "regions": region_stats,
        "tile": {"limits": tile, "worst": worst_local_tile} if tile else None,
        "regional_coverage": "explicit windows" if regions else "picture-level checks only; no interaction windows supplied",
        "decode_completed": True,
    }
    write_json(out / "report.json", report)
    return report
