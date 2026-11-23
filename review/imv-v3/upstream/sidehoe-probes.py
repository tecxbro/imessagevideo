"""Repaint selected Sidehoe windows from editable inputs, then compare native crops."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def rows(path):
    with path.open() as file:
        return {int(row["frame"]): row for row in csv.DictReader(file)}


def revised_artwork(artwork):
    original_glyph = artwork.pictogram
    original_tile = artwork.app_icon

    def glyph(draw, name, x, y, size):
        if name == "plum":
            # Independently drawn curved fruit, green calyx, and highlight.
            patch = Image.new("RGBA", (96, 96))
            pen = ImageDraw.Draw(patch)
            pen.ellipse((27, 25, 71, 88), fill="#603476")
            pen.ellipse((30, 26, 65, 80), fill="#834da4")
            pen.ellipse((34, 33, 43, 70), fill="#ad79bb")
            pen.polygon([(30, 35), (42, 20), (45, 13), (55, 19), (61, 36), (49, 28), (40, 42)], fill="#73a746")
            art = patch.rotate(43, resample=Image.Resampling.BICUBIC)
            # ImageDraw's underlying image is the editable render surface.
            asset = art.resize((max(1, round(size)),) * 2, Image.Resampling.LANCZOS)
            draw._image.paste(asset, (round(x-size/2), round(y-size/2)), asset)
        elif name == "drops":
            for dx, dy, scale in [(-.17, -.17, .32), (.15, -.08, .34), (-.03, .22, .27)]:
                a, b, r = x+dx*size, y+dy*size, scale*size
                draw.polygon([(a-r*.5, b+r*.3), (a+r*.62, b-r*.78), (a+r*.54, b+r*.32)], fill="#55b9e6")
                draw.ellipse((a-r*.56, b-r*.06, a+r*.52, b+r*.75), fill="#55b9e6")
                draw.ellipse((a-r*.27, b+r*.12, a-r*.02, b+r*.43), fill="#d9f8ff")
        else:
            original_glyph(draw, name, x, y, size)

    def icon(key):
        if key != "blue":
            return original_tile(key)
        face = artwork.rounded_gradient(256, 256, "#78bdf9", "#4285e7", 39)
        mask = Image.new("L", (256, 256))
        ImageDraw.Draw(mask).rounded_rectangle((3, 5, 252, 250), 42, fill=255)
        light = Image.new("RGBA", (256, 256))
        ImageDraw.Draw(light).line([(22, 35), (43, 17), (90, 10), (171, 10), (216, 18), (236, 35)],
                                   fill=(190, 248, 255, 210), width=10)
        face.alpha_composite(light.filter(ImageFilter.GaussianBlur(6)))
        artwork.text(ImageDraw.Draw(face), 128, 59, "31", 160, "#f9fcff", 450, "center")
        face.putalpha(mask)
        # A pinched face is independent of the position and exposure tracks.
        result = Image.new("RGBA", face.size)
        for y in range(256):
            width = round(256 - 18 * (1 - abs(y-128)/128)**2)
            strip = face.crop((0, y, 256, y+1)).resize((width, 1), Image.Resampling.BICUBIC)
            result.paste(strip, ((256-width)//2, y))
        return result

    return glyph, icon


def frame_hash(frame):
    return sha256(frame.tobytes()).hexdigest()


def extract(source, start, end, folder):
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(source),
        "-vf", f"select=between(n\\,{start}\\,{end})", "-fps_mode", "passthrough",
        "-frames:v", str(end-start+1), "-start_number", str(start), str(folder / "%06d.png"),
    ], check=True)


def report_frame(image, reference, rect):
    source = np.asarray(reference.crop(rect), dtype=np.int16)
    candidate = np.asarray(image.crop(rect), dtype=np.int16)
    return round(float(np.abs(source-candidate).mean()), 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "reference", "audit", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    sys.path.insert(0, str(args.project.resolve()))
    import artwork
    import render

    scene = json.loads((args.project / "scene.json").read_text())
    baseline = render.Film(scene)
    sofia = rows(args.audit / "sofia-rim.csv")
    follow = rows(args.audit / "follow-rim.csv")
    pointer = rows(args.audit / "follow-pointer.csv")
    crops = json.loads((args.audit / "targeted-crops.json").read_text())
    windows = {
        "calendar": (433, 437, crops["calendar-emoji"]["crop_xyxy"]),
        "tile": (614, 619, crops["app-31"]["crop_xyxy"]),
        "sofia-handset": (321, 333, (500, 50, 1505, 1790)),
        "follow-handset": (639, 650, (500, 50, 1505, 1790)),
        "pointer": (675, 695, (340, 900, 1260, 1420)),
    }
    glyph, icon = revised_artwork(artwork)
    original_glyph, original_icon = artwork.pictogram, render.app_icon
    original_cursor = render.cursor

    class Probe(render.Film):
        def frame(self, frame):
            self.probe_frame = frame
            return super().frame(frame)

        def track(self, name, frame):
            values = super().track(name, frame)
            rim = (sofia if name == "sofiaMeasuredCamera" and 323 <= frame <= 331
                   else follow if name == "followMeasuredCamera" and 641 <= frame <= 649 else None)
            if rim is not None:
                _, y, scale = values
                center = float(rim[frame]["source_center_x"]) / 2
                return center - 200*scale, y, scale
            return values

    changed = Probe(scene)

    def cursor(image, x, y, rotation, opacity, size):
        f = changed.probe_frame
        measured = pointer.get(f, {})
        if 687 <= f <= 695 and measured.get("source_tip_x") and measured.get("source_tip_y"):
            x = float(pointer[f]["source_tip_x"])/2
            y = float(pointer[f]["source_tip_y"])/2
        original_cursor(image, x, y, rotation, opacity, size)

    metrics = {}
    for name, (start, end, rect) in windows.items():
        run = args.output / name
        for folder in ("reference", "baseline", "revised", "baseline-encoded", "revised-encoded"):
            (run / folder).mkdir(parents=True, exist_ok=True)
        extract(args.reference, start, end, run / "reference")
        for frame in range(start, end+1):
            artwork.pictogram, render.app_icon, render.cursor = original_glyph, original_icon, original_cursor
            baseline.frame(frame).save(run / "baseline" / f"{frame:06d}.png")
            artwork.pictogram, render.app_icon, render.cursor = glyph, icon, cursor
            changed.frame(frame).save(run / "revised" / f"{frame:06d}.png")
        for revision in ("baseline", "revised"):
            movie = run / f"{revision}.mp4"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-framerate", "25", "-start_number", str(start),
                "-i", str(run / revision / "%06d.png"), "-frames:v", str(end-start+1), "-an",
                "-vf", "scale=2000:2000:flags=lanczos,setsar=1",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                "-video_track_timescale", "60000", str(movie),
            ], check=True)
            extract(movie, 0, end-start, run / f"{revision}-encoded")
        metrics[name] = []
        for frame in range(start, end+1):
            with Image.open(run / "reference" / f"{frame:06d}.png") as source:
                row = {"frame": frame}
                hashes = []
                for revision in ("baseline", "revised"):
                    with Image.open(run / revision / f"{frame:06d}.png") as lossless:
                        hashes.append(frame_hash(lossless))
                        row[f"{revision}_lossless_mae"] = report_frame(
                            lossless.resize(source.size, Image.Resampling.LANCZOS), source, rect
                        )
                    with Image.open(run / f"{revision}-encoded" / f"{frame-start:06d}.png") as decoded:
                        row[f"{revision}_encoded_mae"] = report_frame(decoded, source, rect)
                row["authored_unchanged"] = hashes[0] == hashes[1]
                metrics[name].append(row)
    capture = json.dumps(metrics, indent=2) + "\n"
    (args.output / "probes.json").write_text(capture)
    for name, measurements in metrics.items():
        baseline_mae = np.mean([row["baseline_encoded_mae"] for row in measurements])
        revised_mae = np.mean([row["revised_encoded_mae"] for row in measurements])
        print(f"{name}: mean native crop RGB {baseline_mae:.3f} -> {revised_mae:.3f}")


if __name__ == "__main__":
    main()
