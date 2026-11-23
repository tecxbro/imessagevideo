import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


FIRST, LAST = 623, 652
WIDTH, HEIGHT = 1440, 1080


def selected_frames(path):
    probe = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
         "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(path)]
    ))
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0",
         "-vf", f"select=between(n\\,{FIRST}\\,{LAST})", "-fps_mode", "passthrough",
         "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    )
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(LAST - FIRST + 1, HEIGHT, WIDTH, 3)
    return probe["frames"], frames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    inputs = {"source": args.source, "archived GSAP": args.archive}
    if args.candidate:
        inputs["candidate"] = args.candidate
    paths = {}
    for label, path in inputs.items():
        timing, frames = selected_frames(path)
        state = []
        for offset, pixels in enumerate(frames):
            roi = pixels[469:540, 1074:1158].astype(np.int16)
            blue = (roi[:, :, 2] - roi[:, :, 0] > 70) & (roi[:, :, 0] < 150)
            frame = FIRST + offset
            state.append({
                "frame": frame,
                "seconds": timing[frame]["best_effort_timestamp_time"],
                "blue_pixels": int(blue.sum()),
                "selected": bool(blue.sum() >= 120),
            })
        with path.open("rb") as media:
            digest = hashlib.file_digest(media, "sha256").hexdigest()
        paths[label] = (frames, {"file": str(path), "sha256": digest,
                                 "decoded_frame_times": len(timing), "row_state": state,
                                 "first_selected_in_window": next(
                                     (entry for entry in state if entry["selected"]), None)})
    evidence = {label: details for label, (_, details) in paths.items()}
    evidence["frame_mae_source_vs_archive"] = {
        str(frame): float(np.abs(paths["source"][0][frame - FIRST].astype(np.int16) -
                                 paths["archived GSAP"][0][frame - FIRST]).mean())
        for frame in range(632, 647)
    }
    print(json.dumps(evidence, indent=2))
    per_row, panel_width, panel_height = 5, 236, 62
    shown = list(range(631, 650))
    stack_height = panel_height * len(inputs)
    sheet = Image.new("RGB", (per_row * panel_width,
                              ((len(shown) + per_row - 1) // per_row) * (stack_height + 21)), "#202336")
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(shown):
        left = (index % per_row) * panel_width
        top = (index // per_row) * (stack_height + 21)
        draw.text((left + 4, top + 3), str(frame), fill="white")
        for order, (label, (frames, _)) in enumerate(paths.items()):
            view = Image.fromarray(frames[frame - FIRST][430:577, 285:1170]).resize((232, 39))
            offset = top + 21 + order * panel_height
            draw.text((left + 4, offset), label, fill="white")
            sheet.paste(view, (left + 2, offset + 16))
    sheet.save(args.directory / "poke-consecutive-row.png")


if __name__ == "__main__":
    main()
