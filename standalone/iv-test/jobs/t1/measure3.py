from PIL import Image
import numpy as np

def bbox(mask):
    ys, xs = np.where(mask)
    if len(ys)==0: return None
    return (int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1))

def mask(im, color, tol=18):
    return (np.abs(im.astype(int) - np.array(color)).sum(axis=2) <= tol)

# ---- detailed static layer analysis on frame 14 ----
im = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)
print("== frame 14 layer inventory ==")
# scan rows 0-100 for nav elements
for y in range(0, 130):
    row = im[y]
    nonwhite = np.where(np.any(row < 245, axis=1))[0]
    if len(nonwhite):
        print(f"  y={y}: x {nonwhite.min()}-{nonwhite.max()} n={len(nonwhite)}")
