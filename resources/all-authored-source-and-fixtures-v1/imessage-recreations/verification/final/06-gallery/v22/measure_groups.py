from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
D = Path('verification/final/06-gallery/v22')
for label, fs in [('black-detail', range(1294, 1303)), ('brand-detail', range(1436, 1446)), ('cta-detail', range(1507, 1519))]:
    c = Image.new('RGB', (760, 170 * len(fs)), '#ccc')
    dr = ImageDraw.Draw(c)
    for i, f in enumerate(fs):
        im = Image.open(D / f'source-late/{f:06d}.png').convert('RGB')
        im.thumbnail((760, 145))
        c.paste(im, (0, i * 170 + 22))
        dr.text((5, i * 170 + 3), str(f), fill='black')
    c.save(D / (label + '.jpg'), quality=94)
for typ, fs, th, gap in [('provider', range(1357, 1367), 140, 20), ('CTA', range(1507, 1519), 252, 18), ('black', range(1294, 1303), 30, 18)]:
    print(typ)
    for f in fs:
        a = np.asarray(Image.open(D / f'source-late/{f:06d}.png').convert('RGB')).mean(2)
        m = (a > th) if typ == 'black' else (a < th)
        xs = np.where(m.any(0))[0]
        gg = []
        for x in xs:
            if not gg or x - gg[-1][-1] > gap:
                gg.append([x])
            else:
                gg[-1].append(x)
        rows = []
        for g in gg:
            ys, xs2 = np.where(m[:, g[0]:g[-1] + 1])
            if len(ys) < 100:
                continue
            vals = a[ys, xs2 + g[0]]
            pct = 95 if typ == 'black' else 5
            rows.append([int(g[0] + 200), int(g[-1] + 201), int(ys.min() + 300), int(ys.max() + 301), round(float(np.percentile(vals, pct)))])
        print(f, rows)
