from functools import lru_cache
import json
import os
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont
import numpy as np

root = Path(__file__).parent
baseline = root / "sidehoe-measured-fade"
sys.path.insert(0, str(baseline))
import artwork
import render

copy = {"plum": "🍆", "drops": "💦", "cat": "🐱"}
references = json.loads((root / "sidehoe-glyph-fit.json").read_text())["results"]
fit = {name: {} for name in copy}
font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 96)
old_pictogram = artwork.pictogram

@lru_cache
def ink(name, width, height):
    image = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(image).text((5, 5), copy[name], font=font, embedded_color=True)
    footprint = image.crop(image.getbbox())
    return footprint.resize((width, height), Image.Resampling.LANCZOS)

def pictogram(frame, draw, name, x, y, size):
    if name not in copy:
        return old_pictogram(draw, name, x, y, size)
    points = fit[name]
    rows = sorted(map(int, points))
    dx, dy, width, height = [
        np.interp(frame, rows, [points[str(row)][i] for row in rows]) for i in range(4)
    ]
    draw._image.alpha_composite(ink(name, max(1,round(width * size)), max(1,round(height * size))),
                                (round(x + dx * size), round(y + dy * size)))

film = render.Film(json.loads((baseline / "scene.json").read_text()))
old_calendar = film.calendar
for frame in [426, 435, 450, 470]:
    targets = references[str(frame)]["fit_reference"]
    def measure(draw, name, x, y, size):
        if name in targets:
            left, top, width, height = targets[name]
            fit[name][str(frame)] = [(left/2-x)/size, (top/2-y)/size, width/(2*size), height/(2*size)]
        return old_pictogram(draw, name, x, y, size)
    artwork.pictogram = measure
    try:
        film.frame(frame)
    finally:
        artwork.pictogram = old_pictogram
(root / "sidehoe-glyph-final-ink.json").write_text(json.dumps(fit,indent=2)+"\n")

def calendar(image, frame):
    artwork.pictogram = lambda d, name, x, y, size: pictogram(frame, d, name, x, y, size)
    try:
        old_calendar(image, frame)
    finally:
        artwork.pictogram = old_pictogram

film.calendar = calendar
cache = root / "sidehoe-glyph-final-frames"
cache.mkdir()
for frame in range(778):
    path = cache / f"{frame:06d}.png"
    if 397 <= frame < 482:
        film.frame(frame).save(path, compress_level=1)
    else:
        os.link(root / "sidehoe-revised-frames" / path.name, path)
print("Rendered calibrated editable glyph placement through the complete calendar passage.")
