#!/usr/bin/env python3
"""Measure ticket-shot motion (fixed heading vs moving rail) and unchanged-segment drift."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

JOB = Path("/Users/darshan/Documents/video-analysis/iv-test/jobs/t4")
FILM_V2 = JOB / "film-v2.mp4"
FILM_V1 = Path("/Users/darshan/Documents/video-analysis/iv-test/jobs/t3/film.mp4")
W, H, N = 720, 480, 288


def decode(path):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(path),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W, 3)
    assert arr.shape[0] == N, f"{path}: {arr.shape[0]} frames != {N}"
    return arr.astype(np.int16)


def mae(a, b):
    return float(np.abs(a - b).mean())


v2 = decode(FILM_V2)
v1 = decode(FILM_V1)

# --- Ticket segment motion: frames 216..287 (local 0..71) ---
# ROIs measured off the decoded frames (720x480 card layout):
HEAD = (110, 45, 500, 60)    # x, y, w, h -> "Maya" header band
RAIL = (110, 125, 500, 215)  # photo rail / ticket cards
FOOT = (110, 390, 500, 50)   # detail footer band (also expected static)


def roi(frame, r):
    x, y, w, h = r
    return frame[y:y + h, x:x + w]


seg = v2[216:288]
ref = seg[0]
rows = []
for i, fr in enumerate(seg):
    rows.append({
        "film_frame": 216 + i,
        "heading_mae": round(mae(roi(fr, HEAD), roi(ref, HEAD)), 4),
        "rail_mae": round(mae(roi(fr, RAIL), roi(ref, RAIL)), 4),
        "footer_mae": round(mae(roi(fr, FOOT), roi(ref, FOOT)), 4),
    })

head_vals = [r["heading_mae"] for r in rows]
rail_vals = [r["rail_mae"] for r in rows]
foot_vals = [r["footer_mae"] for r in rows]

# Consecutive-frame MAE on the rail pinpoints the moving interval.
rail_step = [0.0] + [round(mae(roi(seg[i], RAIL), roi(seg[i - 1], RAIL)), 4)
                     for i in range(1, len(seg))]

motion_check = {
    "segment": "ticket (film frames 216-287, 72 frames)",
    "method": "per-frame MAE of ROI pixels vs segment first frame (int16 RGB, 0-255 scale)",
    "rois": {"heading": HEAD, "rail": RAIL, "footer": FOOT},
    "heading_roi": {"max_mae": max(head_vals), "mean_mae": round(sum(head_vals) / len(head_vals), 4),
                    "expected": "static"},
    "footer_roi": {"max_mae": max(foot_vals), "mean_mae": round(sum(foot_vals) / len(foot_vals), 4),
                   "expected": "static"},
    "rail_roi": {"max_mae": max(rail_vals), "mean_mae": round(sum(rail_vals) / len(rail_vals), 4),
                 "expected": "moves then settles"},
    "rail_consecutive_mae": rail_step,
    "rail_moving_frames": [216 + i for i, v in enumerate(rail_step) if v > 1.0],
    "per_frame": rows,
}

# --- Unchanged segments vs previous export ---
unchanged = {}
for name, lo, hi in [("browse", 72, 143), ("celebrate", 144, 215)]:
    diffs = [mae(v2[i], v1[i]) for i in range(lo, hi + 1)]
    unchanged[name] = {
        "film_frames": [lo, hi],
        "max_mae": round(max(diffs), 4),
        "mean_mae": round(sum(diffs) / len(diffs), 4),
        "worst_frame": lo + int(np.argmax(diffs)),
    }

# --- Unchanged segments vs their own preview renders (should be ~identical) ---
prev = {"browse": JOB / "baseline-final-shots/browse/preview.mp4",
        "celebrate": JOB / "baseline-final-shots/celebrate/preview.mp4"}
for name, (lo, hi) in [("browse", (72, 143)), ("celebrate", (144, 215))]:
    src = decode_prev = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(prev[name]),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    src = np.frombuffer(src, dtype=np.uint8).reshape(-1, H, W, 3).astype(np.int16)
    diffs = [float(np.abs(v2[lo + j] - src[j]).mean()) for j in range(72)]
    unchanged[name]["vs_source_preview_max_mae"] = round(max(diffs), 4)
    unchanged[name]["vs_source_preview_mean_mae"] = round(sum(diffs) / len(diffs), 4)

# --- Changed segments sanity: ask(0-71) and ticket(216-287) should differ from v1 ---
for name, lo, hi in [("ask", 0, 71), ("ticket", 216, 287)]:
    diffs = [mae(v2[i], v1[i]) for i in range(lo, hi + 1)]
    unchanged[name + "_vs_v1"] = {
        "film_frames": [lo, hi],
        "max_mae": round(max(diffs), 4),
        "mean_mae": round(sum(diffs) / len(diffs), 4),
        "note": "expected nonzero - shot changed",
    }

out = {"film": str(FILM_V2), "baseline": str(FILM_V1),
       "note": "film-v2.mp4 assembled with ffmpeg concat -c copy (no re-encode)",
       "ticket_motion": motion_check, "segments_vs_t3_film": unchanged}
(JOB / "ticket-motion-check.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "ticket_motion"}, indent=2))
print("heading max/mean:", motion_check["heading_roi"])
print("rail max/mean:", motion_check["rail_roi"])
print("rail moving frames:", motion_check["rail_moving_frames"])
