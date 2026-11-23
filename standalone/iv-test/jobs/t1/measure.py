import sys
from PIL import Image
import numpy as np

# file -> source frame mapping
order = [0,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,30,33,36,40,45,50,60,70,80,90,99,100,149]

def analyze(path, label):
    im = np.array(Image.open(path).convert("RGB"))
    h, w, _ = im.shape
    print(f"=== {label} {w}x{h}")
    # unique-ish colors: sample some pixels
    # find rows/cols with non-white content
    nonwhite = np.any(im < 245, axis=2)
    rows = np.where(nonwhite.any(axis=1))[0]
    cols = np.where(nonwhite.any(axis=0))[0]
    print("nonwhite rows", rows.min(), rows.max(), "cols", cols.min(), cols.max())
    # print distinct colors counts (top 12)
    px = im.reshape(-1,3)
    colors, counts = np.unique(px, axis=0, return_counts=True)
    idx = np.argsort(-counts)[:14]
    for i in idx:
        print("  color", tuple(colors[i]), counts[i])

for i, fr in enumerate(order, start=1):
    if fr in (0, 14, 15, 27, 40, 99, 149):
        analyze(f"frames/f{i:02d}.png", f"frame {fr}")
