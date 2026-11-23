#!/usr/bin/env python3
"""Independent re-measurement of the ticket shot in film-v2.mp4 (frames 216-287)."""
import subprocess, sys
import numpy as np

V2 = "/Users/darshan/Documents/video-analysis/iv-test/jobs/t4/film-v2.mp4"
V1 = "/Users/darshan/Documents/video-analysis/iv-test/jobs/t3/film.mp4"
W, H = 720, 480
FPS_N = 288

def decode(path, lo, hi):
    """Decode frames lo..hi inclusive -> list of HxWx3 uint8."""
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path,
         "-vf", f"select='gte(n,{lo})*lte(n,{hi})'",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    n = hi - lo + 1
    arr = np.frombuffer(out, dtype=np.uint8)
    assert arr.size == n * W * H * 3, f"expected {n} frames, got {arr.size/(W*H*3)}"
    return arr.reshape(n, H, W, 3)

def mae(a, b, roi=None):
    if roi:
        x0, y0, x1, y1 = roi
        a, b = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
    return float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())

# ---------- ticket shot: frames 216-287 ----------
frames = decode(V2, 216, 287)
first = frames[0]

# ROIs (x0,y0,x1,y1) — my own boxes chosen from decoded frames
HEAD = (115, 50, 605, 100)   # "Maya" heading band
RAIL = (115, 130, 605, 340)  # card rail band
FOOT = (115, 392, 605, 435)  # detail-line footer

print("== ticket shot, per-frame ROI MAE vs frame 216 ==")
hmax = rmax = fmax = 0.0
rail_by_frame = []
for i, f in enumerate(frames):
    h = mae(f, first, HEAD); r = mae(f, first, RAIL); ft = mae(f, first, FOOT)
    hmax, rmax, fmax = max(hmax, h), max(rmax, r), max(fmax, ft)
    rail_by_frame.append(r)
    if i % 6 == 0 or i == len(frames) - 1:
        print(f"  local {i:2d} (film {216+i}): head={h:7.4f} rail={r:8.4f} foot={ft:7.4f}")
print(f"  MAX head={hmax:.4f}  rail={rmax:.4f}  foot={fmax:.4f}")

print("== consecutive-frame whole-frame MAE (motion onset/offset) ==")
prev = frames[0]
moving = []
for i, f in enumerate(frames[1:], start=1):
    d = mae(f, prev)
    if d > 0.5:
        moving.append((i, round(d, 2)))
    prev = f
print("  local frames with consecutive MAE>0.5:", moving[:30])
print(f"  first moving local={moving[0][0] if moving else None}  last={moving[-1][0] if moving else None}")

# ---------- unchanged region: film-v2 vs t3/film.mp4, frames 72-215 ----------
print("== unchanged shots: per-frame whole-frame MAE v2 vs v1 ==")
a = decode(V2, 72, 215)
b = decode(V1, 72, 215)
diffs = np.abs(a.astype(np.int16) - b.astype(np.int16)).mean(axis=(1, 2, 3))
print(f"  n={len(diffs)}  max={diffs.max():.4f} (film frame {72+int(diffs.argmax())})  mean={diffs.mean():.4f}")
worst = np.argsort(diffs)[-5:][::-1]
print("  worst frames:", [(72 + int(i), round(float(diffs[i]), 3)) for i in worst])

# also compare v2 segments against the reused source previews? report whole-film ask shot too
a2 = decode(V2, 0, 71)
b2 = decode(V1, 0, 71)
d2 = np.abs(a2.astype(np.int16) - b2.astype(np.int16)).mean(axis=(1, 2, 3))
print(f"== ask shot v2 vs v1: max={d2.max():.4f} mean={d2.mean():.4f} ==")
