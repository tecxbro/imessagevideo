"""Extract all published measured Motion source windows by decoded frame index."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import file_digest
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageOps


def capture(args):
    return subprocess.check_output(args)


def read_window(input_file, first, last, thumbnail=(160, 100)):
    stream = json.loads(capture(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_frames", "-show_streams", "-show_entries",
        "stream=width,height,time_base,r_frame_rate:frame=best_effort_timestamp",
        "-of", "json", str(input_file)]))
    attributes = stream["streams"][0]
    pts = [int(frame["best_effort_timestamp"]) for frame in stream["frames"]]
    w, h = thumbnail
    ratio = Fraction(attributes["width"], attributes["height"])
    width = min(w, round(h * ratio)) & ~1
    height = min(h, round(w / ratio)) & ~1
    filters = f"select=between(n\\,{first}\\,{last}),scale={width}:{height},pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    raw = capture(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-threads", "1",
        "-i", str(input_file), "-map", "0:v:0", "-an", "-vf", filters, "-fps_mode", "passthrough",
        "-pix_fmt", "rgb24", "-threads", "1", "-f", "rawvideo", "-"])
    stride = w * h * 3
    if len(raw) != (last - first + 1) * stride:
        raise ValueError(f"Missing decoded frame(s) in {input_file}")
    images = [Image.frombytes("RGB", thumbnail, raw[i:i+stride]) for i in range(0, len(raw), stride)]
    return attributes, pts[first:last+1], pts[last+1] if last+1 < len(pts) else None, images


def grab_asset(source, source_root, supplemental):
    file = source.get("picture", source["ref"]).rsplit("/", 1)[-1]
    if source["ref"].startswith("projects/"):
        return source_root / source["ref"]
    if file == "locked.mp4":
        names = [supplemental / file, supplemental / "current-locked.mp4"]
        return max((candidate for candidate in names if candidate.is_file()), key=lambda p: p.stat().st_size)
    return supplemental / file


def review(row, source_root, supplemental, out):
    id = row["id"]
    provenance = row["source"]
    source = grab_asset(provenance, source_root, supplemental)
    with source.open("rb") as media:
        sha256 = file_digest(media, "sha256").hexdigest()
    evidence = {"id": id, "source": provenance["ref"], "picture": provenance.get("picture"), "sha256": sha256,
                "catalog_window_seconds": provenance["range"]}
    if source.suffix == ".png":
        with Image.open(source) as still:
            evidence["source_size"] = still.size
            ImageOps.contain(still.convert("RGB"), (720, 560)).save(out / f"{id}.jpg")
        return evidence
    first, last = provenance.get("framesInclusive", provenance.get("frames"))
    stream, pts, exclusive_end, images = read_window(source, first, last)
    seconds = Fraction(stream["time_base"])
    expected = provenance["range"]
    actual = [float(pts[0]*seconds), float(exclusive_end*seconds) if exclusive_end is not None else None]
    evidence.update({"frame_window_inclusive": [first, last], "timebase": str(seconds),
                     "native_pts": pts, "first_excluded_pts": exclusive_end,
                     "decoded_picture": stream, "decoded_half_open_seconds": actual,
                     "approximate_catalog_error_seconds": [None if got is None else got-want
                                                            for got, want in zip(actual, expected)]})
    thumb_w, thumb_h = images[0].size
    cols = 7
    sheet = Image.new("RGB", (cols * (thumb_w + 5), ((len(images)+cols-1)//cols) * (thumb_h+25)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (image, tick) in enumerate(zip(images, pts)):
        x, y = (i % cols)*(thumb_w+5), (i//cols)*(thumb_h+25)
        sheet.paste(image, (x, y))
        draw.text((x+3, y+thumb_h+2), f"{first+i}  {float(tick*seconds):.6f}", fill="#182737")
    sheet.save(out / f"{id}.jpg", quality=84, optimize=True)
    return evidence


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--supplemental", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    entries = json.loads(args.catalog.read_text())["entries"]
    included = {"measured-adaptation", "observed-pose-adaptation", "direction-authored-adaptation"}
    evidence = [review(row, args.source_root, args.supplemental, args.out)
                for row in entries if row["source"]["kind"] in included]
    (args.out / "source-windows.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Extracted {len(evidence)} source windows, including one still.")


if __name__ == "__main__":
    main()
