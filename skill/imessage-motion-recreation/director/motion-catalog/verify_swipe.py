"""Compare every exported photo-strip frame with the corresponding native pixels."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

CATALOG = Path(__file__).resolve().parent
RECORD = json.loads((CATALOG / 'registry.json').read_text())['entries'][0]
SOURCE = RECORD['source']
VIEW = RECORD['measurement']['viewport']


def decode(path, filters, width, height):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path), '-an', '-vf', filters,
           '-fps_mode', 'passthrough', '-pix_fmt', 'gray', '-f', 'rawvideo', '-']
    return np.frombuffer(subprocess.check_output(cmd), np.uint8).reshape(-1, height, width)


def register(reference, rendered):
    # Ignore exterior/rounded edges, but retain gutters and texture inside each photo.
    height, width = reference.shape
    ys = np.arange(12, height - 12, 4)
    xs = np.arange(12, width - 12, 4)
    target = reference[np.ix_(ys, xs)].astype(float)
    def score(dx, dy):
        sample = rendered[np.ix_(ys + dy, xs + dx)].astype(float)
        return float(np.mean(np.abs(target - sample)))
    err, dx, dy = min((score(dx, dy), dx, dy) for dx in range(-5, 6) for dy in range(-3, 4))
    aligned = rendered[np.ix_(ys + dy, xs + dx)]
    correlation = np.corrcoef(target.ravel(), aligned.ravel())[0, 1]
    return dict(dx=dx, dy=dy, mae=round(err, 3), correlation=round(float(correlation), 5))


def verify():
    source = CATALOG / SOURCE['sourcePath']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE['sourceSha256']
    w,h,x,y = (VIEW[k] for k in ('width','height','x','y'))
    native = decode(source, 'trim=start_frame=1090:end_frame=1113', 960, 720)
    source_strips = native[:, y:y+h, x:x+w]
    previews = {k: CATALOG / v for k,v in RECORD['previews'].items()}
    controls = decode(previews['controls'], 'null', w, h)
    isolated = decode(previews['isolated'], 'null', w, h)
    context = decode(previews['context'], 'null', 960, 720)
    assert len(native) == len(controls) == 23 and len(isolated) == len(context) == 21
    rows = []
    for i, ref in enumerate(source_strips):
        row = dict(sourceFrame=1090+i, controls=register(ref, controls[i]))
        if 0 < i < 22:
            row['isolated'] = register(ref, isolated[i-1])
            row['context'] = register(ref, context[i-1,y:y+h,x:x+w])
            # Integer registration in fixed title / action regions detects a moving document.
            for key, region in [('title', (15,65,195,420)), ('actions', (115,181,195,550))]:
                a,b,c,d = region
                row[key+'Native'] = register(native[0,a:b,c:d],native[i,a:b,c:d])
                row[key+'Render'] = register(context[0,a:b,c:d],context[i-1,a:b,c:d])
        rows.append(row)
    return rows


if __name__ == '__main__':
    rows = verify()
    print(json.dumps(rows, indent=2))
    for row in rows:
        for name, sample in row.items():
            if name == 'sourceFrame':
                continue
            limit = 2 if name in ('controls','isolated','context') else 0
            if abs(sample['dx']) > limit or abs(sample['dy']) > limit or sample['correlation'] < .94:
                sys.exit(f'Registration failed on {row["sourceFrame"]} {name}: {sample}')
