#!/usr/bin/env python3
"""Measure heading-fixed vs rail-moving on a rendered mp4 (720x480 seed layout).

Usage: measure_replay.py VIDEO FRAMES_DIR OUT_JSON

ROIs match the seed card layout: heading band (110,44,500,54), footer
(110,396,500,40), photo viewport (140,131,440,197). Also tracks the dark
bounding box of the heading text to prove the title does not translate, and
reports whether rail per-frame MAE shows real motion.
"""
import json, sys
from pathlib import Path
from PIL import Image
import numpy as np
import glob

video, frames_dir, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
HEADING = (110, 44, 610, 98)     # full heading band
TITLE_TXT = (135, 55, 400, 85)   # heading glyphs
RAIL = (140, 131, 580, 328)      # photo viewport
FOOTER = (110, 396, 610, 436)    # footer band

def roi(img, box):
    return np.asarray(img.crop(box).convert("RGB"), dtype=np.int16)

def dark_bbox(img, region, thresh=120):
    a = np.asarray(img.crop(region).convert("L"), dtype=np.int16)
    ys, xs = np.where(a < thresh)
    if len(xs) == 0:
        return None
    return [int(xs.min()) + region[0], int(ys.min()) + region[1],
            int(xs.max()) + region[0], int(ys.max()) + region[1]]

files = sorted(glob.glob(str(Path(frames_dir) / "*.png")))
rows, prev, bboxes = [], None, {}
for i, f in enumerate(files):
    img = Image.open(f)
    h, r, ft = roi(img, HEADING), roi(img, RAIL), roi(img, FOOTER)
    bboxes[i] = dark_bbox(img, TITLE_TXT)
    if prev is not None:
        rows.append({
            "frame": i,
            "heading_mae": round(float(np.abs(h - prev[0]).mean()), 4),
            "rail_mae": round(float(np.abs(r - prev[1]).mean()), 4),
            "footer_mae": round(float(np.abs(ft - prev[2]).mean()), 4),
        })
    prev = (h, r, ft)

summ = {}
for k in ("heading", "rail", "footer"):
    vals = [row[f"{k}_mae"] for row in rows]
    summ[k] = {"mean_mae": round(float(np.mean(vals)), 4),
               "max_mae": round(float(np.max(vals)), 4)}
active = [row["frame"] for row in rows if row["rail_mae"] > 1.0]
xs = [b[0] for b in bboxes.values() if b]
result = {
    "video": video,
    "frames": len(files),
    "rois": {"heading_band": HEADING, "rail": RAIL, "footer": FOOTER,
             "title_text_tracking": TITLE_TXT},
    "per_frame": rows,
    "summary": summ,
    "rail_active_frames": [min(active), max(active)] if active else None,
    "title_text_bbox_first": bboxes.get(0),
    "title_text_bbox_last": bboxes.get(len(files) - 1),
    "title_text_left_edge_drift_px": (max(xs) - min(xs)) if xs else None,
    "heading_fixed": summ["heading"]["max_mae"] < 2.0,
    "rail_moved": summ["rail"]["mean_mae"] > 2.0,
}
Path(out_json).write_text(json.dumps(result, indent=2))
print(json.dumps({"summary": summ, "rail_active": result["rail_active_frames"],
                  "title_drift_px": result["title_text_left_edge_drift_px"],
                  "heading_fixed": result["heading_fixed"],
                  "rail_moved": result["rail_moved"]}, indent=1))
