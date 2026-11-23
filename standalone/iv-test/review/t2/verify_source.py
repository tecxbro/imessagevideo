#!/usr/bin/env python3
"""Independent reviewer measurement of 05-linq.mp4 frames 1070-1145.
Own implementation; ROIs chosen by reviewer from rendered frames."""
import os, json
import numpy as np
from PIL import Image

D = "/Users/darshan/Documents/video-analysis/iv-test/review/t2/src-frames"

def load(n):
    return np.asarray(Image.open(os.path.join(D, f"f{n:04d}.png")).convert("RGB"), dtype=np.float64)

# Reviewer-chosen ROIs (x0,y0,x1,y1):
HEAD = (195, 15, 660, 110)     # title + rating row + buttons band top
RAIL = (195, 300, 775, 640)    # photo rail band
# Also a tighter title-only box for the dark-pixel bbox check
TITLE = (195, 15, 560, 60)

frames = list(range(1070, 1146))
imgs = {n: load(n) for n in frames if os.path.exists(os.path.join(D, f"f{n:04d}.png"))}
have = sorted(imgs)

per = []
for a, b in zip(have[:-1], have[1:]):
    if b != a + 1:
        continue
    ia, ib = imgs[a], imgs[b]
    h = np.abs(ia[HEAD[1]:HEAD[3], HEAD[0]:HEAD[2]] - ib[HEAD[1]:HEAD[3], HEAD[0]:HEAD[2]]).mean()
    r = np.abs(ia[RAIL[1]:RAIL[3], RAIL[0]:RAIL[2]] - ib[RAIL[1]:RAIL[3], RAIL[0]:RAIL[2]]).mean()
    per.append({"pair": [a, b], "heading_mae": round(float(h), 4), "rail_mae": round(float(r), 4)})

# Title dark-pixel bbox at sample frames (threshold luminance<80 within TITLE box)
bboxes = {}
for n in [1078, 1080, 1091, 1100, 1111, 1120, 1130, 1135, 1140]:
    if n not in imgs: continue
    crop = imgs[n][TITLE[1]:TITLE[3], TITLE[0]:TITLE[2]]
    lum = crop.mean(axis=2)
    ys, xs = np.where(lum < 80)
    if len(xs):
        bboxes[n] = [int(xs.min()) + TITLE[0], int(ys.min()) + TITLE[1],
                     int(xs.max()) + TITLE[0], int(ys.max()) + TITLE[1]]

# Reviewer's own rail-translation measure: column-profile normalized cross-correlation.
# Method: grayscale column profile of the rail band, find integer shift in [-200,200]
# minimizing SAD over the overlapping region between consecutive frames.
PROF = (195, 310, 775, 630)  # (x0,y0,x1,y1)

def profile(n):
    img = imgs[n][PROF[1]:PROF[3], PROF[0]:PROF[2]]
    return img.mean(axis=(0, 2))  # one value per column

def best_shift(pa, pb, lo=-220, hi=220):
    best_s, best_e = 0, float("inf")
    for s in range(lo, hi + 1):
        if s >= 0:
            xa, xb = pa[:len(pa) - s] if s else pa, pb[s:]
        else:
            xa, xb = pa[-s:], pb[:len(pb) + s]
        if min(len(xa), len(xb)) < 80:
            continue
        e = np.abs(xa - xb).mean()
        if e < best_e:
            best_e, best_s = float(e), s
    return best_s, best_e

# positive shift of content to the LEFT means pb col x == pa col x+shift => pb[s:] vs pa[:-s]
# our convention: shift s>0 => b is a shifted-left-by-s copy of a
shifts = []
cum = 0
for n in range(1090, 1113):
    if n in imgs and n + 1 in imgs:
        s, e = best_shift(profile(n), profile(n + 1))
        cum += s
        shifts.append({"pair": [n, n + 1], "shift_left_px": s, "err": round(e, 3), "cum": cum})

# find rail motion span: consecutive-frame rail MAE > 1.0
moving = [p["pair"][1] for p in per if p["rail_mae"] > 1.0]
span = [min(moving) - 1, max(moving)] if moving else None

# catalog window summary
win = [p for p in per if 1091 <= p["pair"][0] <= 1110 or (p["pair"][0] == 1111)]
win = [p for p in per if 1091 <= p["pair"][1] <= 1112]
summ = {
    "heading_mean": round(float(np.mean([p["heading_mae"] for p in win])), 4),
    "heading_max": round(float(max(p["heading_mae"] for p in win)), 4),
    "rail_mean": round(float(np.mean([p["rail_mae"] for p in win])), 4),
    "rail_max": round(float(max(p["rail_mae"] for p in win)), 4),
}

out = {
    "rois": {"heading": HEAD, "rail": RAIL, "title_bbox_box": TITLE, "profile_band": PROF},
    "rail_motion_span_frames": span,
    "title_dark_bbox": bboxes,
    "catalog_window_summary": summ,
    "per_frame_mae": per,
    "rail_translation": shifts,
}
with open("/Users/darshan/Documents/video-analysis/iv-test/review/t2/source-check.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps({"span": span, "summary": summ, "bboxes": bboxes}, indent=1))
print("shifts:", [(p["pair"], p["shift_left_px"]) for p in shifts])
