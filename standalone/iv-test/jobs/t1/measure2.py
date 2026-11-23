from PIL import Image
import numpy as np

order = [0,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,30,33,36,40,45,50,60,70,80,90,99,100,149]

def bbox(mask):
    ys, xs = np.where(mask)
    if len(ys)==0: return None
    return (xs.min(), ys.min(), xs.max()+1, ys.max()+1)  # l,t,r,b exclusive

def regions(im, color, tol=6):
    diff = np.abs(im.astype(int) - np.array(color)).sum(axis=2)
    return diff <= tol*3

print("== frame 14 (static base) ==")
im = np.array(Image.open("frames/f02.png").convert("RGB"))
# blue bubble
for name, c in [("blue",(8,131,252)), ("grey",(231,231,233)), ("darkgrey",(196,196,196)), ("navbg-ish",(208,208,211))]:
    m = regions(im,c)
    print(name, bbox(m), "count", m.sum())

# find grey connected components roughly: label scan of grey mask rows
grey = regions(im,(231,231,233))
for y0 in range(0, 720, 10):
    pass
# profile grey by row
rowsum = grey.sum(axis=1)
cur = None
for y,v in enumerate(rowsum):
    if v>0 and cur is None: cur=y
    if v==0 and cur is not None:
        print("grey rows", cur, y, "maxcount", rowsum[cur:y].max())
        cur=None
if cur is not None: print("grey rows", cur, 720)

# per-column extents for each grey band
def band_detail(mask, y0, y1):
    sub = mask[y0:y1]
    print("  band", y0, y1, "bbox", bbox(sub))
    # left/right profile
    return bbox(sub)

print()
print("== scan all frames: blue bbox + grey bands ==")
for i, fr in enumerate(order, start=1):
    im = np.array(Image.open(f"frames/f{i:02d}.png").convert("RGB"))
    blue = regions(im,(8,131,252))
    grey = regions(im,(231,231,233))
    bb = bbox(blue)
    # grey components via row profile
    rowsum = grey.sum(axis=1)
    bands=[]; cur=None
    for y,v in enumerate(rowsum):
        if v>0 and cur is None: cur=y
        if v==0 and cur is not None:
            bands.append((cur,y)); cur=None
    if cur is not None: bands.append((cur,720))
    gb = [bbox(grey[y0:y1]) and (y0, bbox(grey[y0:y1])) for (y0,y1) in bands]
    print(f"f{fr:3d} blue={bb} greybands={[(y0, b) for y0,b in gb]}")
