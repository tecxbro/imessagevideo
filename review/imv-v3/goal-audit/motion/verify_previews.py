"""Verify catalog preview bytes, native cadence, frame changes and cue windows."""
from argparse import ArgumentParser
import concurrent.futures
from fractions import Fraction
from hashlib import file_digest, sha256
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw
import numpy as np


def file_hash(path):
    with path.open("rb") as file:
        return file_digest(file, "sha256").hexdigest()


def command(args):
    return subprocess.check_output(args)


def cut_video(path, count, event_frames):
    """Keep representative event, change and held frames in their native index order."""
    w, h = 192, 128
    rgb = command(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-threads", "1",
                   "-i", str(path), "-map", "0:v:0", "-an", "-vf", f"scale={w}:{h}",
                   "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-threads", "1",
                   "-f", "rawvideo", "-"])
    pictures = np.frombuffer(rgb, dtype=np.uint8).reshape(-1, h, w, 3)
    if len(pictures) != count:
        raise ValueError(f"{path}: preview decode yielded {len(pictures)} frames, expected {count}")
    diffs = np.abs(np.diff(pictures.astype(np.int16), axis=0)).mean(axis=(1, 2, 3))
    peak = int(np.argmax(diffs)) + 1 if len(diffs) else 0
    change = next((i for i, delta in enumerate(diffs, 1) if delta > .01), 0)
    event_frames = [number for number in event_frames if 0 < number < count - 1]
    first_event = event_frames[0] if event_frames else change
    middle_event = event_frames[len(event_frames) // 2] if event_frames else (count - 1) // 2
    picked = set((0, first_event, middle_event, peak, count - 1))
    for frame in (change, first_event - 1, first_event + 1, count // 2, count * 2 // 3):
        if len(picked) < 5 and 0 < frame < count - 1:
            picked.add(frame)
    distinct_thumbs = len({sha256(image.tobytes()).digest() for image in pictures})
    return [(frame, Image.fromarray(pictures[frame])) for frame in sorted(picked)], distinct_thumbs


def timeline_evidence(timeline):
    return {
        "picture": timeline["picture"],
        "events": [{key: event[key] for key in ("id", "frame", "kind")} for event in timeline["events"]],
    }


def decode_clock(path):
    probe = json.loads(command(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_frames", "-show_streams", "-show_entries",
        "stream=codec_name,width,height,avg_frame_rate,time_base:frame=best_effort_timestamp",
        "-of", "json", str(path)]))
    stream = probe["streams"][0]
    base = Fraction(stream["time_base"])
    ticks = [int(frame["best_effort_timestamp"]) * base for frame in probe["frames"]]
    decoded = command(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-threads", "1",
                       "-i", str(path), "-map", "0:v:0", "-an", "-fps_mode", "passthrough",
                       "-f", "framemd5", "-"]).decode()
    checksums = [line.split(",")[-1].strip() for line in decoded.splitlines()
                 if not line.startswith("#")]
    return stream, ticks, checksums


def conforms(stream, ticks, clock, count):
    return (Fraction(stream["avg_frame_rate"]) == clock and len(ticks) == count
            and all(presentation == i / clock for i, presentation in enumerate(ticks)))


def inspect(job, snapshot, fresh):
    row, is_ui = job
    evidence = row["ui"] if is_ui else row
    stem = f"ui.{row['id']}" if is_ui else row["id"]
    path = snapshot / evidence["preview"]
    expected = evidence["picture"]
    clock = Fraction(expected["fpsNum"], expected["fpsDen"])
    count = expected["frameCount"]
    clip_metadata, ticks, checksums = decode_clock(path)
    digest = file_hash(path)
    event_data = json.loads((snapshot / evidence["eventMap"]).read_text())
    overview, thumbnails = cut_video(path, count, [event["frame"] for event in evidence["events"]])
    proof = {
        "id": row["id"], "ui": is_ui, "preview": evidence["preview"],
        "sha256": digest, "hash_matches": digest == evidence["sha256"],
        "picture": expected, "presentation_clock_matches": conforms(clip_metadata, ticks, clock, count)
                                 and len(checksums) == count,
        "resolution": [clip_metadata["width"], clip_metadata["height"]],
        "source_matches_catalog": timeline_evidence(event_data) == {"picture": expected, "events": evidence["events"]},
        "distinct_full_frames": len(set(checksums)), "distinct_thumbnail_frames": thumbnails,
        "sampled_frames": [frame for frame, _ in overview],
    }
    if fresh:
        rerender = fresh / f"{stem}.mp4"
        fresh_map = fresh / f"{stem}.events.json"
        proof["fresh"] = {"present": rerender.is_file(), "event_map_present": fresh_map.is_file()}
        if rerender.is_file() and fresh_map.is_file():
            fresh_timeline = json.loads(fresh_map.read_text())
            fresh_digest = file_hash(rerender)
            fresh_stream, fresh_ticks, fresh_checksums = decode_clock(rerender)
            proof["fresh"].update({
                "sha256": fresh_digest,
                "byte_matches": fresh_digest == digest,
                "frame_pixels_match": fresh_checksums == checksums,
                "presentation_clock_matches": conforms(fresh_stream, fresh_ticks, clock, count)
                                              and len(fresh_checksums) == count,
                "resolution_matches": (fresh_stream["width"], fresh_stream["height"])
                                      == tuple(proof["resolution"]),
                "event_map_matches": timeline_evidence(fresh_timeline) == timeline_evidence(event_data),
            })
    return proof, overview


def render_sheets(results, output):
    """Make role-review sheets, in catalog order and separate from numeric results."""
    width = 1010
    sheet_size = 7
    for offset in range(0, len(results), sheet_size):
        section = results[offset: offset + sheet_size]
        sheet = Image.new("RGB", (width, len(section) * 169), "white")
        draw = ImageDraw.Draw(sheet)
        for row_number, (proof, pictures) in enumerate(section):
            y = row_number * 169
            suffix = "  (Messages adapter)" if proof["ui"] else ""
            draw.text((10, y + 2), "  ".join((str(offset + row_number + 1), proof["id"] + suffix)),
                      fill="#182737")
            for column, (frame, image) in enumerate(pictures):
                x = 10 + column * 200
                sheet.paste(image, (x, y + 20))
                draw.text((x, y + 150), f"Frame {frame}", fill="#364158")
        sheet.save(output / f"sheet-{offset // sheet_size + 1:02d}.jpg", quality=84, optimize=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--fresh", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    entries = json.loads(args.catalog.read_text())["entries"]
    jobs = [(row, False) for row in entries] + [(row, True) for row in entries if "ui" in row]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda job: inspect(job, args.snapshot, args.fresh), jobs))
    proofs = [proof for proof, _ in results]
    render_sheets(results, args.out)
    (args.out / "previews.json").write_text(json.dumps(proofs, indent=2) + "\n")
    total = len(proofs)
    perfect = sum(row["hash_matches"] and row["presentation_clock_matches"]
                  and row["source_matches_catalog"] for row in proofs)
    print(f"{perfect}/{total} previews match hash, cadence and event map.")


if __name__ == "__main__":
    main()
