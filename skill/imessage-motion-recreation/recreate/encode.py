"""Encode an authored, frame-indexed PNG cache on a measured variable picture clock."""
import csv
from fractions import Fraction
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from media import MediaError, video_clock, write_json


def timestamp_expression(ticks, first=0):
    """Use a balanced expression with a linear fast path for constant-delta spans."""
    if len(ticks) == 1:
        return str(ticks[0])
    step = ticks[1] - ticks[0]
    if all(tick == ticks[0] + n * step for n, tick in enumerate(ticks)):
        return f"{ticks[0]}+(N-{first})*{step}"
    half = len(ticks) // 2
    boundary = first + half
    left = timestamp_expression(ticks[:half], first)
    right = timestamp_expression(ticks[half:], boundary)
    return f"if(lt(N,{boundary}),{left},{right})"


def encode_measured_clock(frames, measurements, output):
    frames, measurements, output = Path(frames), Path(measurements), Path(output).resolve()
    if output.suffix.lower() != ".mp4":
        raise MediaError("Clock encoding currently writes opaque H.264 MP4")
    analysis = json.loads((measurements / "analysis.json").read_text())
    clock = analysis["clock"]
    base = Fraction(clock["time_base"])
    with (measurements / "timeline.csv").open(newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != clock["frames"] or not rows:
        raise MediaError("Clock CSV does not match measurement frame count")
    origin = int(rows[0]["pts"])
    ticks = [(int(row["pts"]) - origin) * base.numerator for row in rows]
    duration = int(rows[-1]["duration_pts"]) * base.numerator
    if (origin != clock["start_pts"] or duration <= 0 or
            ticks[-1] + duration != (clock["end_pts_exclusive"] - origin) * base.numerator):
        raise MediaError("Clock CSV disagrees with measured picture origin or final sample")
    if any(int(row["frame"]) != n for n, row in enumerate(rows)):
        raise MediaError("Clock CSV must cover every frame index in order")
    if any(a >= b for a, b in zip(ticks, ticks[1:])):
        raise MediaError("Clock CSV must contain strictly increasing PTS")
    if clock.get("alpha_present") or clock["color_transfer"] in ("smpte2084", "arib-std-b67"):
        raise MediaError("This encoder requires opaque SDR inputs")
    expected_names = [f"{n:06d}.png" for n in range(len(rows))]
    if sorted(path.name for path in frames.glob("*.png")) != expected_names:
        raise MediaError("Supply exactly one authored PNG per index, from 000000.png")
    expected_geometry = (clock["width"], clock["height"])
    if expected_geometry[0] % 2 or expected_geometry[1] % 2:
        raise MediaError("H.264 yuv420p delivery requires even input dimensions")
    if clock["rotation_degrees"] or clock["sample_aspect_ratio"] != "1":
        raise MediaError("Clock encoder expects a square-pixel source without display transforms")
    if any(clock.get("container_crop_top_bottom_left_right", [])):
        raise MediaError("Clock encoder expects an uncropped source")
    if clock.get("display_matrix", [65536, 0, 0, 0, 65536, 0, 0, 0, 1073741824]) != [
        65536, 0, 0, 0, 65536, 0, 0, 0, 1073741824
    ]:
        raise MediaError("Clock encoder expects an identity display matrix")
    # The indexed source is RGB artwork; encode with a declared SDR BT.709 matrix.
    # Disable B-frames so MP4 infers every interior duration directly from consecutive DTS.
    primaries = clock["color_primaries"] or "bt709"
    transfer = clock["color_transfer"] or "bt709"
    if any(not re.fullmatch(r"[a-z0-9_-]+", tag) for tag in (primaries, transfer)):
        raise MediaError("Invalid measured SDR color tags")
    expression = (
        f"settb=1/{base.denominator},setpts='{timestamp_expression(ticks)}',"
        "scale=out_color_matrix=bt709:out_range=tv,"
        f"setparams=range=limited:colorspace=bt709:color_primaries={primaries}:color_trc={transfer}"
    )
    tail = f"setts=duration='if(eq(N,{len(ticks) - 1}),{duration},DURATION)'"
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as directory:
        filter_path = Path(directory) / "clock.filter"
        filter_path.write_text(expression)
        generated = Path(directory) / "picture.mp4"
        command = [
            "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-filter_threads", "2",
            "-f", "image2", "-start_number", "0", "-framerate", "30", "-i",
            str(frames.resolve() / "%06d.png"), "-an",
            "-filter_script:v", str(filter_path), "-fps_mode", "passthrough", "-enc_time_base",
            f"1/{base.denominator}", "-c:v", "libx264", "-threads:v", "2", "-bf", "0", "-crf", "17",
            "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709",
            "-color_primaries", primaries, "-color_trc", transfer,
            "-bsf:v", tail, "-video_track_timescale", str(base.denominator),
            "-movflags", "+faststart", str(generated),
        ]
        encoded = subprocess.run(command, capture_output=True, text=True)
        if encoded.returncode or encoded.stderr:
            raise MediaError(f"FFmpeg clock encode failed: {encoded.stderr.strip()}")
        result = video_clock(generated)
        target_pts = [Fraction(tick, base.denominator) for tick in ticks]
        target_end = Fraction(ticks[-1] + duration, base.denominator)
        if result.times != target_pts or result.end != target_end:
            raise MediaError(f"Encoder did not preserve every PTS and end {target_end}; measured end {result.end}")
        if (result.width, result.height) != expected_geometry:
            raise MediaError(f"Encoded PNG dimensions differ from source {expected_geometry}")
        if (result.stream.get("color_primaries"), result.stream.get("color_transfer")) != (primaries, transfer):
            raise MediaError("Generated output did not retain the requested SDR color tags")
        generated.replace(output)
    report = {"source_sha256": analysis["source_sha256"], "matched_presentation_timestamps": len(ticks),
              "matched_end_seconds": str(target_end), "clock": result.summary()}
    write_json(output.with_suffix(".clock.json"), report)
    return report
