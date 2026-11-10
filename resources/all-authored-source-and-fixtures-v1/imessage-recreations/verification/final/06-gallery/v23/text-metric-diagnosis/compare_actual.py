from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw
import numpy as np

D = Path(__file__).resolve().parent
ROOT = Path('/workspace/imessage-recreations')
rows = []
contact = Image.new('RGB', (1500, 1200), '#aaa')
draw = ImageDraw.Draw(contact)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for index, frame in enumerate([1067, 1106, 552]):
    paths = {
        'gsap': ROOT / f'outputs/06-gallery/frames-gsap/{frame:06d}.png',
        'actualMC': ROOT / f'outputs/06-gallery/cache/motion-canvas/{frame:06d}.png',
        'before': D / f'actual/{frame}-off.png',
        'prototype': D / f'actual/{frame}-formula.png',
    }
    arrays = {key: np.asarray(Image.open(path).convert('RGB')) for key, path in paths.items()}
    row = {'frame': frame, 'files': {key: {'path': str(path), 'sha256': digest(path)} for key, path in paths.items()}, 'comparisons': {}, 'whiteGlyphBoxes': {}}
    for left, right in [('before', 'actualMC'), ('prototype', 'before'), ('before', 'gsap'), ('prototype', 'gsap')]:
        difference = np.abs(arrays[left].astype(float) - arrays[right].astype(float))
        row['comparisons'][f'{left}Vs{right}'] = {
            'mae': float(difference.mean()), 'max': int(difference.max()),
            'changedPixels': int(np.any(difference, axis=2).sum()),
        }
    for key, array in arrays.items():
        if frame == 552:
            continue
        mask = (array.mean(axis=2) > 180)[430:650]
        active = np.where(mask.any(axis=0))[0]
        runs = np.split(active, np.where(np.diff(active) > 12)[0] + 1)
        boxes = []
        for run in runs:
            if not len(run):
                continue
            xx0, xx1 = int(run[0]), int(run[-1]) + 1
            yy = np.where(mask[:, xx0:xx1].any(axis=1))[0]
            boxes.append([xx0, int(yy[0]) + 430, xx1, int(yy[-1]) + 431])
        row['whiteGlyphBoxes'][key] = boxes
    for col, key in enumerate(['gsap', 'before', 'prototype']):
        image = Image.fromarray(arrays[key])
        if frame != 552:
            image = image.crop((280, 450, 1650, 635))
        image.thumbnail((495, 350))
        contact.paste(image, (col * 500, index * 400 + 35))
        draw.text((col * 500 + 5, index * 400 + 5), f'{frame} {key}', fill='black')
    rows.append(row)
(D / 'actual-comparison.json').write_text(json.dumps(rows, indent=2))
contact.save(D / 'actual-comparison.jpg', quality=95)
print(json.dumps(rows, indent=2))
