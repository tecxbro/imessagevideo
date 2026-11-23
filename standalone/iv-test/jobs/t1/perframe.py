from PIL import Image
import numpy as np, json

GREY = np.array([231,231,233])
out = []
for i in range(1, 136):   # all/001.png = src frame 15
    src = 14 + i
    im = np.array(Image.open(f"all/{i:03d}.png").convert("RGB")).astype(int)
    g = (np.abs(im - GREY).sum(axis=2) < 60)
    m = g[340:520, 20:400]
    ys, xs = np.where(m)
    if not len(ys):
        out.append(dict(f=src, present=False)); continue
    x0,x1,y0,y1 = int(20+xs.min()), int(20+xs.max()+1), int(340+ys.min()), int(340+ys.max()+1)
    sub = im[y0:y1, x0:x1]
    dark = np.all(sub < 150, axis=2)
    t = None
    if dark.any():
        dys,dxs = np.where(dark)
        t = dict(x0=int(x0+dxs.min()), x1=int(x0+dxs.max()+1), y0=int(y0+dys.min()), y1=int(y0+dys.max()+1))
    out.append(dict(f=src, x0=x0, x1=x1, y0=y0, y1=y1, w=x1-x0, h=y1-y0,
                    cx=round((x0+x1)/2,2), text=t))
json.dump(out, open("doors_track.json","w"), indent=0)
for r in out[:100]:
    if r.get('present') is False: print(r['f'], 'ABSENT'); continue
    t=r['text'] or {}
    tw=(t.get('x1') or 0)-(t.get('x0') or 0)
    th=(t.get('y1') or 0)-(t.get('y0') or 0)
    print(f"f{r['f']:3d} y{r['y0']:3d}-{r['y1']:3d} h{r['h']:3d} w{r['w']:3d} cx{r['cx']:.1f} sx={r['w']/251:.3f} sy={r['h']/61:.3f} txtw={tw} txth={th} tx0={t.get('x0')}")
