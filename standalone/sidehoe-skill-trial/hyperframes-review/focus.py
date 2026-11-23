"""Capture matched source, previous and revised frames from encoded MP4s."""
import argparse
import csv
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw, ImageFont


# Rectangles use the source's 2000 × 2000 decoded pixel grid.
FOCUS = {
    22: ("inbox", (230, 365, 1710, 1530)),
    53: ("inbox-scroll", (0, 0, 2000, 2000)),
    106: ("profile", (680, 650, 1320, 1320)),
    111: ("profile-settle", (680, 650, 1320, 1320)),
    137: ("rim-ripple", (0, 450, 2000, 1510)),
    138: ("handset-entrance", (0, 0, 2000, 2000)),
    150: ("handset-hold", (0, 0, 2000, 2000)),
    158: ("handset-exit", (0, 0, 2000, 2000)),
    184: ("heart-entrance", (370, 870, 1630, 1270)),
    191: ("type-and-hearts", (365, 790, 1635, 1180)),
    205: ("heart-exit", (355, 650, 1650, 1060)),
    209: ("title-motion-blur", (370, 470, 1630, 905)),
    355: ("sofia-handoff", (0, 0, 2000, 2000)),
    357: ("sofia-release", (0, 0, 2000, 2000)),
    400: ("calendar-before", (250, 1150, 1690, 2000)),
    401: ("calendar-overlap", (250, 1090, 1720, 1850)),
    402: ("calendar-after", (250, 960, 1720, 1710)),
    610: ("tile-approach", (738, 1040, 1250, 1625)),
    612: ("tile-face", (738, 1090, 1250, 1655)),
    616: ("tile-exit", (738, 1245, 1250, 1830)),
    621: ("tile-tail", (738, 1650, 1250, 2000)),
    622: ("tile-control", (738, 1650, 1250, 2000)),
    625: ("cursor-first-visible", (1700, 95, 1895, 275)),
    643: ("cursor-descent", (1690, 565, 1900, 720)),
    655: ("cursor-turn", (1720, 690, 1930, 875)),
    663: ("cursor-sweep", (1390, 1115, 1640, 1340)),
    670: ("cursor-approach", (715, 915, 1335, 1425)),
    675: ("cursor-contact", (710, 880, 1300, 1400)),
    686: ("cursor-hold", (710, 860, 1290, 1360)),
    694: ("cursor-withdrawal", (720, 875, 1300, 1345)),
    695: ("cursor-tail", (720, 875, 1300, 1345)),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "previous", "revised", "out"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    frames = sorted(FOCUS)
    selector = "+".join(f"eq(n\\,{frame})" for frame in frames)
    font = ImageFont.load_default(size=18)
    results = []
    with TemporaryDirectory(prefix="sidehoe-focus-") as tmp:
        decoded = Path(tmp)
        for name in ("source", "previous", "revised"):
            target = decoded / name
            target.mkdir()
            subprocess.run(
                ["ffmpeg", "-nostdin", "-v", "error", "-i", str(getattr(args, name)),
                 "-vf", f"select={selector}", "-an", "-fps_mode", "passthrough",
                 "-start_number", "0", str(target / "%02d.png")],
                check=True,
            )
            if len(list(target.glob("*.png"))) != len(frames):
                raise ValueError(f"Incomplete decode for {name}")

        for index, frame in enumerate(frames):
            label, box = FOCUS[frame]
            views = []
            for name in ("source", "previous", "revised"):
                with Image.open(decoded / name / f"{index:02}.png") as picture:
                    if picture.size != (2000, 2000):
                        raise ValueError(f"Expected native 2000 × 2000 pixels for {name}")
                    views.append(picture.convert("RGB").crop(box))
            source, previous, revised = map(lambda im: np.array(im, dtype=np.int16), views)
            filename = f"f{frame:03}-{label}.png"
            results.append(
                [frame, f"{frame / 25:.2f}", label, *box,
                 round(float(np.abs(source - previous).mean()), 5),
                 round(float(np.abs(source - revised).mean()), 5), filename],
            )
            for view in views:
                view.thumbnail((480, 600), Image.Resampling.LANCZOS)
            w, h = views[0].size
            panel_width = max(w, 245)
            sheet = Image.new("RGB", (panel_width * 3, h + 34), "#13141a")
            caption = ImageDraw.Draw(sheet)
            for j, (name, view) in enumerate(zip(("Source", "Previous", "Revised"), views)):
                left = j * panel_width
                sheet.paste(view, (left + (panel_width - w) // 2, 34))
                caption.text((left + 10, 6), f"{name} · f{frame} / {frame / 25:.2f} s",
                             fill="white", font=font)
            sheet.save(args.out / filename)
    with (args.out / "metrics.csv").open("w", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["frame", "seconds", "feature", "x0", "y0", "x1", "y1",
                         "previous_mean_abs_rgb", "revised_mean_abs_rgb", "image"])
        writer.writerows(results)


if __name__ == "__main__":
    main()
