"""Compare every decoded frame outside the nominated replacement and read the edited message."""
import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

from linq_swipe import choose_motion, measure_motion, write
from direction_and_edit import SKILL

sys.path.insert(0, str(SKILL / "scripts"))
from frames import inspect


def hashes(path):
    text = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-an",
        "-fps_mode", "passthrough", "-f", "framemd5", "pipe:1",
    ], text=True)
    return [row.rsplit(",", 1)[-1].strip() for row in text.splitlines() if not row.startswith("#") and row]


def still(movie, frame, path):
    subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(movie), "-vf", f"select=eq(n\\,{frame})",
        "-frames:v", "1", str(path),
    ], check=True)


def all_layers(layers):
    for layer in layers:
        yield layer
        yield from all_layers(layer.get("children", []))


def verify(project, donor, output):
    before, after = [project / name for name in ("concert-tickets.mp4", "meet-at-the-doors.mp4")]
    plan = json.loads((project / "plan-edit-approved.json").read_text())["plan"]
    intervals = [shot["frames"] for shot in plan["shots"]]
    first, end = intervals[0], sum(intervals[:2])
    _, a_pts, a_end = inspect(before)
    _, b_pts, b_end = inspect(after)
    assert a_pts == b_pts and len(a_pts) == sum(intervals) and a_end == b_end
    pair = list(zip(hashes(before), hashes(after), strict=True))
    assert len(pair) == len(a_pts)
    with (output / "decoded-frame-hashes.csv").open("w", newline="") as report:
        writer = csv.writer(report)
        writer.writerow(("frame", "pts", "before_md5", "after_md5", "identical"))
        writer.writerows((i, str(a_pts[i]), a, b, a == b) for i, (a, b) in enumerate(pair))
    outside = [(a, b) for i, (a, b) in enumerate(pair) if not first <= i < end]
    assert all(a == b for a, b in outside)
    assert all(pair[i][0] != pair[i][1] for i in (first, end - 1))

    detail = project / "proof-donor-edit"
    scene = json.loads((detail / "scene.json").read_text())
    exact = next(layer["text"] for layer in all_layers(scene["layers"]) if layer["id"] == "pinned-message-copy")
    assert exact == "Meet at the doors"
    comparison = measure_motion(donor, detail / "preview.mp4", choose_motion(scene),
                                output / "donor-motion-comparison.json", message=True)
    assert comparison["passes"], comparison

    indices = [first - 1, first, first + 1, end - 2, end - 1, end]
    sheet = Image.new("RGB", (360 * len(indices), 524), "#172337")
    drawing = ImageDraw.Draw(sheet)
    for col, index in enumerate(indices):
        for row, movie in enumerate((before, after)):
            file = output / f"{'before' if row == 0 else 'after'}-{index:03d}.png"
            still(movie, index, file)
            with Image.open(file) as image:
                sheet.paste(image.resize((360, 240), Image.Resampling.LANCZOS), (col * 360, row * 262 + 22))
            drawing.text((col * 360 + 8, row * 262 + 5),
                         f"{'Previous' if row == 0 else 'Edited'} · frame {index}", fill="white")
    sheet.save(output / "edit-boundaries.jpg", quality=94)
    if shutil.which("tesseract"):
        image = Image.open(output / f"after-{first:03d}.png")
        crop = image.crop((145, 355, 384, 391)).resize((956, 144))
        crop.save(output / "message-ocr-input.png")
        ocr = subprocess.check_output([
            "tesseract", str(output / "message-ocr-input.png"), "stdout", "--psm", "7",
        ], text=True).strip()
        assert ocr == exact, ocr
    else:
        ocr = None
    write(output / "edit-comparison.json", {
        "decoded_total_frames": len(pair), "unchanged_decoded_frames": len(outside),
        "replaced_window": [first, end], "first_and_last_inside_changed": True,
        "same_clock_and_exclusive_end": True, "exact_editable_text": exact,
        "decoded_picture_ocr": ocr, "boundary_frame_indices": indices,
        "donor_motion": comparison,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("donor", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    verify(args.project.resolve(), args.donor.resolve(), args.output.resolve())
