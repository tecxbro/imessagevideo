from pathlib import Path
from PIL import Image
from scipy.ndimage import shift
import numpy as np, json, sys
R = Path('/workspace/imessage-recreations')
sys.path.insert(0, str(R / 'engines'))
import render_pillow as rp
D = R / 'verification/final/06-gallery/v22'
s = json.load(open(R / 'outputs/06-gallery/final-v21/scene.json'))
nodes = {}
def walk(ns):
    for q in ns:
        nodes[q['id']] = q
        walk(q.get('children', []))
walk(s['layers'])
rows = []
for f in range(204, 213):
    src = np.array(Image.open(D / f'source-done/{f:06d}.png').convert('RGB')).mean(2)
    cand = np.array(Image.open(R / f'outputs/06-gallery/frames-gsap/{f:06d}.png').convert('RGB')).mean(2)
    st = rp.state(nodes['rene-final11-group-37'], f / 30)
    sy = rp.state(nodes['rene-final11-group-38'], f / 30)['y']
    y = round(1235 + sy + st['y'])
    y0, y1 = max(0, y + 14), min(755, y + 91)
    if y1 - y0 < 10 or st['opacity'] == 0:
        rows.append({'frame':f, 'opacityBefore':st['opacity'], 'note':'actor hidden below composer/font support'})
        continue
    S = 255 - src[y0:y1, 580:1110]
    C = (255 - cand[y0:y1, 580:1110]) / st['opacity']
    best = None
    for dy in np.arange(-6, 6.01, .5):
        v = shift(C, (dy, 0), order=1, mode='constant')
        mask = v > 40
        if mask.sum() < 50:
            continue
        alpha = np.clip((S[mask] * v[mask]).sum() / (v[mask] ** 2).sum(), 0, 1)
        err = np.mean((S[mask] - v[mask] * alpha) ** 2)
        if best is None or err < best['mse']:
            best = {'opacity':float(alpha), 'dy':float(dy), 'mse':float(err), 'pixels':int(mask.sum())}
    rows.append({'frame':f, 'opacityBefore':st['opacity'], 'bodyTop':y, 'fit':best})
(D / 'done-fit.json').write_text(json.dumps(rows, indent=2))
print(json.dumps(rows, indent=2))
