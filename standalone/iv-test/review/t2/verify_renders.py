#!/usr/bin/env python3
"""Reviewer measurement of replay-new.mp4, generic-slide.mp4, seed preview."""
import os, json
import numpy as np
from PIL import Image

BASE = "/Users/darshan/Documents/video-analysis/iv-test/review/t2"

def measure(folder, head, rail, foot):
    files = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
    imgs = {int(f[1:4]): np.asarray(Image.open(os.path.join(folder, f)).convert("RGB"), dtype=np.float64) for f in files}
    ks = sorted(imgs)
    per = []
    for a, b in zip(ks[:-1], ks[1:]):
        ia, ib = imgs[a], imgs[b]
        h = np.abs(ia[head[1]:head[3], head[0]:head[2]] - ib[head[1]:head[3], head[0]:head[2]]).mean()
        r = np.abs(ia[rail[1]:rail[3], rail[0]:rail[2]] - ib[rail[1]:rail[3], rail[0]:rail[2]]).mean()
        ft = np.abs(ia[foot[1]:foot[3], foot[0]:foot[2]] - ib[foot[1]:foot[3], foot[0]:foot[2]]).mean()
        per.append({"pair": [a, b], "head": round(float(h), 4), "rail": round(float(r), 4), "foot": round(float(ft), 4)})
    # heading stability vs first frame + dark-pixel bbox of title per frame
    first = imgs[ks[0]]
    drift, bboxes = [], {}
    for k in ks:
        c = imgs[k]
        drift.append(float(np.abs(c[head[1]:head[3], head[0]:head[2]] - first[head[1]:head[3], head[0]:head[2]]).mean()))
        crop = c[head[1]:head[3], head[0]:head[2]]
        lum = crop.mean(axis=2)
        ys, xs = np.where(lum < 100)
        bboxes[k] = [int(xs.min()) + head[0], int(xs.max()) + head[0]] if len(xs) else None
    rail_active = [p["pair"] for p in per if p["rail"] > 1.0]
    return {
        "n_frames": len(ks),
        "head_perframe_mean": round(float(np.mean([p["head"] for p in per])), 4),
        "head_perframe_max": round(float(max(p["head"] for p in per)), 4),
        "head_vs_first_max": round(float(max(drift)), 4),
        "rail_perframe_mean": round(float(np.mean([p["rail"] for p in per])), 4),
        "rail_perframe_max": round(float(max(p["rail"] for p in per)), 4),
        "foot_perframe_max": round(float(max(p["foot"] for p in per)), 4),
        "foot_vs_first_max": None,
        "rail_active_pairs": rail_active[:6] + (["..."] if len(rail_active) > 6 else []) + rail_active[-3:],
        "title_x_range_by_frame_sample": {k: bboxes[k] for k in ks[::12]},
        "title_left_edge_minmax": [min(b[0] for b in bboxes.values() if b), max(b[0] for b in bboxes.values() if b)],
        "title_present_frames": sum(1 for b in bboxes.values() if b),
        "per_frame": per,
        "_bboxes_all": {k: v for k, v in bboxes.items()},
    }

# ROIs on the 720x480 seed-card layout (card ~x110-610, title ~y58-90, photos ~y128-330, footer ~y400-425)
HEAD = (110, 50, 610, 100)
RAIL = (110, 125, 610, 335)
FOOT = (110, 395, 610, 430)

out = {}
for name, folder in [("replay-new", "replay-frames"), ("generic-slide", "generic-frames"), ("seed-preview", "prev-frames")]:
    m = measure(os.path.join(BASE, folder), HEAD, RAIL, FOOT)
    # foot drift vs first
    files = sorted(os.listdir(os.path.join(BASE, folder)))
    imgs0 = np.asarray(Image.open(os.path.join(BASE, folder, files[0])).convert("RGB"), dtype=np.float64)
    drifts = []
    for f in files:
        c = np.asarray(Image.open(os.path.join(BASE, folder, f)).convert("RGB"), dtype=np.float64)
        drifts.append(float(np.abs(c[FOOT[1]:FOOT[3], FOOT[0]:FOOT[2]] - imgs0[FOOT[1]:FOOT[3], FOOT[0]:FOOT[2]]).mean()))
    m["foot_vs_first_max"] = round(max(drifts), 4)
    out[name] = m

with open(os.path.join(BASE, "render-check.json"), "w") as f:
    json.dump(out, f, indent=1)
for k, v in out.items():
    vv = {a: b for a, b in v.items() if a not in ("per_frame", "_bboxes_all")}
    print(k, json.dumps(vv, indent=1))
