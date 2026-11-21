"""Verify the Linq motion from decoded pixels and exercise changed content."""
import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np

from direction_and_edit import SKILL, decide, run, write


IDS = ["01-photonhq", "02-danieltian", "03-photon-mini", "04-poke", "05-linq", "06-gallery"]


def decoded(path, width, height, start=None, end=None):
    command = ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0"]
    if start is not None:
        command += ["-vf", f"trim=start_frame={start}:end_frame={end}"]
    command += ["-fps_mode", "passthrough", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
    return np.frombuffer(subprocess.check_output(command), np.uint8).reshape(-1, height, width)


def trajectory(frames, x, stop, y, bottom, search):
    rail = frames[:, y:bottom:6, :].astype(np.int16)
    moves = [0]
    errors = [0.0]
    for prev, current in zip(rail[:-1], rail[1:]):
        shifts = range(-3, search + 1)
        scores = [float(np.abs(prev[:, x + dx:stop + dx] - current[:, x:stop]).mean())
                  for dx in shifts]
        best = min(shifts, key=lambda dx: (scores[dx + 3], abs(dx)))
        moves.append(best)
        errors.append(scores[best + 3])
    return np.cumsum(moves), errors


def fixed_peak(frames, x0, y0, x1, y1):
    crops = frames[:, y0:y1, x0:x1].astype(np.int16)
    return float(np.max(np.abs(crops[1:] - crops[0]).mean(axis=(1, 2))))


def heading_displacement(frames):
    # Match the dark glyph edges. Brightness drift around the title is not positional motion.
    x0, y0, x1, y1 = 195, 20, 407, 55
    original = frames[0, y0:y1, x0:x1] < 140
    translations = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5)]
    matches = []
    for frame in frames:
        def loss(shift):
            dx, dy = shift
            changed = (frame[y0 + dy:y1 + dy, x0 + dx:x1 + dx] < 140) != original
            return (int(changed.sum()), abs(dx) + abs(dy))
        matches.append(min(translations, key=loss))
    return max(max(abs(x), abs(y)) for x, y in matches)


def measure_motion(donor, output, first, destination, *, message=False):
    source = decoded(donor, 960, 720)
    replay = decoded(output, 720, 480)
    left, source_error = trajectory(source, 215, 535, 340, 595, 172)
    right, replay_error = trajectory(replay, 151, 401, 147, 306, 170)
    source_heading = fixed_peak(source, 191, 16, 414, 57)
    source_displacement = heading_displacement(source)
    replay_heading = fixed_peak(replay, 131, 51, 580, 94)
    replay_message = fixed_peak(replay, 145, 360, 558, 387) if message else None
    if first < 0 or first + len(left) > len(right):
        raise ValueError("Replay lacks the full source motion and ending")
    moving = right[first:first + len(left)] - right[first]
    norm_error = None
    if left[-1] > 0 and moving[-1] > 0:
        norm_error = np.abs(left / left[-1] - moving / moving[-1])
    report = {
        "source_frames": len(left), "replay_frames": len(right), "replay_first_frame": first,
        "source_rail_left_pixels": int(left[-1]), "replay_rail_left_pixels": int(moving[-1]),
        "source_heading_peak_mae": source_heading, "replay_heading_peak_mae": replay_heading,
        "source_heading_max_displacement_px": source_displacement,
        "replay_message_peak_mae": replay_message,
        "max_normalized_trajectory_error": None if norm_error is None else float(norm_error.max()),
        "mean_normalized_trajectory_error": None if norm_error is None else float(norm_error.mean()),
    }
    report["passes"] = bool(left[-1] > 1000 and moving[-1] > 100 and norm_error is not None
                            and norm_error.max() <= 0.045 and source_displacement <= 1 and replay_heading <= 1.5
                            and (replay_message is None or replay_message <= 1.5))
    write(destination, report)
    with destination.with_suffix(".csv").open("w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(("source_frame", "replay_frame", "source_left_px", "replay_left_px",
                         "source_matching_mae", "replay_matching_mae"))
        writer.writerows((i, first + i, left[i], moving[i], source_error[i], replay_error[first + i])
                         for i in range(len(left)))
    return report


def choose_motion(scene):
    stage = next(layer for layer in scene["layers"] if layer["id"] == "stage")
    viewport = next(layer for layer in stage["children"] if layer["id"] == "photo-viewport")
    rail = next(layer for layer in viewport["children"] if layer["id"] == "photo-rail")
    return round(rail["keyframes"]["x"][0]["t"] * 30)


def exercise(inputs, root, library):
    donor = inputs / "linq-fixed-swipe.mp4"
    request = decide(root / "learn-request.json", library, "Learn this swipe.", "--video", donor)
    assert request["intent"] == "learn" and request["scope"] == "motion"
    full = decide(root / "learn-motion-choice.json", library, "Learn this swipe.",
                  "--video", inputs / "05-linq.mp4", "--motion", "photos-under-fixed-heading")
    assert full["motion_choices"]["seed"][0]["id"] == "photos-under-fixed-heading"
    recognitions = {}
    for name in [*IDS, "linq-excerpt-480x360"]:
        receipt = json.loads(run("sources.py", "identify", inputs / (name + ".mp4"), "--library", library))
        expected = "05-linq" if name.startswith("linq-") else name
        assert receipt["status"] == ("candidate" if name.startswith("linq-") else "known")
        assert [x["id"] for x in receipt["matches"]] == [expected]
        recognitions[name] = receipt
    write(root / "recognition.json", recognitions)

    photo_root = root / "photos"
    shutil.copytree(inputs / "transfer-photos", photo_root)
    photos = ["bear-lake", "wildflowers", "snowy-slopes", "forest-canyon"]
    content = write(root / "different-place.json", {
        "heading": "Cedar Pass Lodge", "detail": "Rocky Mountain National Park",
        "photos": [f"photos/{name}.jpg" for name in photos],
    })
    video = root / "different-place.mp4"
    run("recipes.py", "render", "photos-under-fixed-heading", "--content", content, "--out", video)
    scene = json.loads(video.with_suffix(".scene.json").read_text())
    first = choose_motion(scene)
    positive = measure_motion(donor, video, first, root / "rail-comparison.json")
    negative = root / "moves-heading.mp4"
    bad = json.loads(content.read_text())
    bad["photos"] = bad["photos"][:2]
    control = write(root / "wrong-motion-content.json", bad)
    run("recipes.py", "render", "heading-over-fixed-photos", "--content", control, "--out", negative)
    rejected = measure_motion(donor, negative, first, root / "wrong-motion-control.json")
    if not positive["passes"] or rejected["passes"]:
        raise ValueError(f"Linq transfer comparison failed. positive={positive}, negative={rejected}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("library", type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    exercise(args.inputs.resolve(), root, args.library.resolve())
