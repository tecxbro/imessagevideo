import json
from functools import lru_cache
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

root = Path(__file__).parent
project = root / "sidehoe-measured-fade"
sys.path.insert(0, str(project))
import artwork
import render

font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 96)
glyphs = {"plum": "🍆", "drops": "💦", "cat": "🐱"}
panels = {
    426: ((687, 740, 808, 814), (707, 947, 830, 1028)),
    435: ((655, 739, 803, 808), (700, 832, 803, 930)),
    440: ((649, 729, 788, 807), (692, 796, 777, 876)),
    450: ((643, 733, 780, 815), (690, 787, 774, 868)),
    470: ((648, 945, 791, 1039), (690, 783, 781, 880)),
}
film = render.Film(json.loads((project / "scene.json").read_text()))
old = artwork.pictogram

@lru_cache
def emoji(name, width, height):
    rgba = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(rgba).text((5, 5), glyphs[name], font=font, embedded_color=True)
    ink = rgba.crop(rgba.getbbox())
    return ink.resize((width, height), Image.Resampling.LANCZOS)

def observe(draw, name, x, y, size):
    if name in glyphs:
        places[name] = (x, y, size)
    else:
        old(draw, name, x, y, size)

def put(canvas, name, left, top, width, height):
    canvas.alpha_composite(emoji(name, width, height), (left, top))

def mean(source, candidate):
    return round(float(np.abs(np.asarray(source, dtype="float32") - np.asarray(candidate, dtype="float32")).mean()), 4)

def measure(source, without, name, box, width_values, height_values):
    expected = source.crop(box)
    backdrop = without.crop(box).convert("RGBA")
    sample = np.array(expected, dtype=np.int16)
    no_glyph = np.array(backdrop.convert("RGB"), dtype=np.int16)
    # Weight the local channel contrast so a backdrop misalignment does not choose the scale.
    mask = np.max(abs(sample - no_glyph), axis=2) >= 27
    score, best = float("inf"), None
    for width in width_values:
        for height in height_values:
            icon = emoji(name, width, height)
            for x in range(-4, backdrop.width - width + 4):
                for y in range(-4, backdrop.height - height + 4):
                    patch = backdrop.copy()
                    patch.alpha_composite(icon, (x, y))
                    current = np.array(patch.convert("RGB"), dtype=np.int16)
                    error = abs(current - sample)
                    weighted = error[mask].sum() + 0.95 * error[~mask].sum()
                    if weighted < score:
                        best, score = (box[0] + x, box[1] + y, width, height), weighted
    return best

def resize(frame):
    return frame.resize((2000, 2000), Image.Resampling.LANCZOS)

cases = {}
for i, (n, boxes) in enumerate(panels.items(), 1):
    places = {}
    source = Image.open(root / "sidehoe-seam-source" / f"glyph-{i:02d}.png").convert("RGB")
    base = resize(film.frame(n))
    artwork.pictogram = observe
    no_emoji = resize(film.frame(n))
    artwork.pictogram = old
    x0, y0, x1, y1 = boxes[0]
    border = {426:750,435:730,440:724,450:718,470:724}[n]
    crop_plum = (x0 + 4, y0, border + 4, y1)
    crop_drops = (border, y0, x1, y1)
    fit = {
        "plum": measure(source, no_emoji, "plum", crop_plum, range(45, 56, 2), range(44, 55, 2)),
        "drops": measure(source, no_emoji, "drops", crop_drops, range(43, 54, 2), range(40, 51, 2)),
    }
    if n in (435, 440, 450):
        fit["cat"] = measure(source, no_emoji, "cat", boxes[1], range(38, 49, 2), range(42, 55, 2))
    cases[n] = {"fit": fit, "places": places, "expected": source, "base": base}
    print(n, fit, flush=True)

# Measure on f426, f435, f450 and f470 only. Interpolate offsets and ink dimensions
# in the authored local scale, and use f440 as an independent held-out state.
fit_frames = [426, 435, 450, 470]
offsets = {}
for name in glyphs:
    values = {}
    for n in fit_frames:
        case = cases[n]
        if name not in case["fit"]:
            continue
        x, y, size = case["places"][name]
        left, top, width, height = case["fit"][name]
        values[n] = [(left / 2 - x) / size, (top / 2 - y) / size, width / (2 * size), height / (2 * size)]
    offsets[name] = values

results = {}
for n, case in cases.items():
    def composite(draw, name, x, y, size):
        if name not in glyphs:
            return old(draw, name, x, y, size)
        keys = sorted(offsets[name])
        dx, dy, width, height = [np.interp(n, keys, [offsets[name][k][p] for k in keys]) for p in range(4)]
        put(draw._image, name, round(x + dx * size), round(y + dy * size),
            round(width * size), round(height * size))

    artwork.pictogram = composite
    candidate = resize(film.frame(n))
    artwork.pictogram = old
    source, base = case["expected"], case["base"]
    boxes = panels[n][:2 if n in (435, 440, 450) else 1]
    results[n] = {"held_out": n == 440, "fit_reference": case["fit"], "regions": [{
        "box": box,
        "baseline": mean(source.crop(box), base.crop(box)),
        "candidate": mean(source.crop(box), candidate.crop(box)),
    } for box in boxes]}
    for suffix, picture in [("source",source), ("before",base), ("after",candidate)]:
        x0 = min(box[0] for box in boxes) - 20
        y0 = min(box[1] for box in boxes) - 6
        x1 = max(box[2] for box in boxes) + 12
        y1 = max(box[3] for box in boxes) + 6
        picture.crop((x0,y0,x1,y1)).save(root / f"glyph-{n}-{suffix}.png")
    print(n, results[n], flush=True)

(root / "sidehoe-glyph-fit.json").write_text(json.dumps({"relative_ink": offsets, "results": results},indent=2) + "\n")
