import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SPECS = {
    "night-garden": {
        "count": 102,
        "sample": [0, 41, 47, 51, 55, 101],
        "fixed": {
            "headline": [64, 149, 431, 297],
            "card title, subtitle, and controls": [535, 72, 885, 204],
            "card address": [535, 432, 885, 470],
        },
        "moving": [539, 215, 884, 411],
    },
    "field-crew": {
        "count": 114,
        "sample": [0, 39, 55, 73, 92, 113],
        "fixed": {
            "headline": [64, 149, 431, 297],
            "conversation header": [530, 49, 879, 105],
            "message bubble": [532, 125, 880, 182],
            "composer": [532, 451, 880, 483],
        },
        "moving": [534, 196, 864, 391],
    },
}


def command(*args):
    return subprocess.check_output(args)


def write_samples(frames, samples, out_path):
    sheet = Image.new("RGB", (1440, 588), "#181c27")
    draw = ImageDraw.Draw(sheet)
    for slot, frame in enumerate(samples):
        x = slot % 3 * 480
        y = slot // 3 * 294
        thumbnail = Image.fromarray(frames[frame]).resize((480, 270), Image.Resampling.LANCZOS)
        sheet.paste(thumbnail, (x, y))
        draw.text((x + 12, y + 275), f"Frame {frame:03d}    {frame / 30:.2f} s", fill="#e9e9f2")
    sheet.save(out_path)


def all_frame_mae(frames, region):
    left, top, right, bottom = region
    reference = frames[0, top:bottom, left:right].astype(np.int16)
    return max(
        np.abs(frame[top:bottom, left:right].astype(np.int16) - reference).mean()
        for frame in frames
    )


def verify(slug, spec):
    path = ROOT / slug / f"{slug}.mp4"
    metadata = json.loads(command(
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,pix_fmt,avg_frame_rate,nb_frames",
        "-show_entries", "format=duration", "-of", "json", path,
    ))
    raw = command(
        "ffmpeg", "-v", "error", "-xerror", "-i", path, "-map", "0:v:0",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    )
    stream = metadata["streams"][0]
    assert stream["codec_name"] == "h264"
    assert stream["pix_fmt"] == "yuv420p"
    assert (stream["width"], stream["height"], stream["avg_frame_rate"]) == (960, 540, "30/1")
    decoded = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 540, 960, 3)
    assert len(decoded) == int(stream["nb_frames"]) == spec["count"]

    fixed_errors = {
        name: round(all_frame_mae(decoded, region), 4)
        for name, region in spec["fixed"].items()
    }
    moving_error = round(all_frame_mae(decoded, spec["moving"]), 4)
    assert max(fixed_errors.values()) < 1
    assert moving_error > 25
    write_samples(decoded, spec["sample"], ROOT / "frames" / f"{slug}.png")
    return {
        **metadata,
        "sampled_frames": spec["sample"],
        "fixed_crop_max_frame_mae_rgb_of_255": fixed_errors,
        "moving_crop_max_frame_mae_rgb_of_255": moving_error,
    }


print(json.dumps({slug: verify(slug, spec) for slug, spec in SPECS.items()}, indent=2))
