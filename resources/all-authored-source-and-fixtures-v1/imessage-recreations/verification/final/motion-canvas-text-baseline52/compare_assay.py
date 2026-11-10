from pathlib import Path
import json
import numpy as np
from PIL import Image

R = Path('/workspace/imessage-recreations')
D = Path(__file__).resolve().parent
B = D / 'geometry-assay'
A = D / 'rms-native-assay'
def pixels(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(float)
def frame_file(reference, method, frame):
    meta = json.loads((R / f'outputs/{reference}/{method}.mp4.render.json').read_text())
    folder = Path(meta['frameDirectory'])
    for name in [f'{frame:06d}.png', f'frame{frame:06d}.png']:
        path = folder / name
        if path.exists():
            return path
    raise FileNotFoundError(f'{folder}, frame{frame}')

rows = []
for f in sorted(A.glob('*.svg.png')):
    key = f.name[:-8]
    candidate = pixels(A / (key + '.png'))
    svg = pixels(f)
    beforepath = B / (key + '.png')
    before = pixels(beforepath) if beforepath.exists() else None
    row = {
        'id': key, 'candidateVsPrivateSVG': float(np.abs(candidate - svg).mean()),
        'beforeVsPrivateSVG': float(np.abs(before - svg).mean()) if before is not None else None,
    }
    if key != 'synthetic-rot-blur':
        reference, frame = key.rsplit('-', 1)
        g = pixels(frame_file(reference, 'gsap', int(frame)))
        old = pixels(frame_file(reference, 'motion-canvas', int(frame)))
        row.update(candidateVsRetainedG=float(np.abs(candidate - g).mean()), beforeVsRetainedG=float(np.abs(before - g).mean()), beforeVsCanonicalMC=float(np.abs(before - old).mean()))
    logs = json.loads((A / (key + '.json')).read_text())['geometry']
    row.update(draws=len(logs), rmsRange=[min((x['rms'] for x in logs), default=1), max((x['rms'] for x in logs), default=1)], maxFontTopError=max((abs(x.get('fontTopPreservationError', 0)) for x in logs), default=0))
    rows.append(row)
(A / 'comparison.json').write_text(json.dumps(rows, indent=2))
print(json.dumps(rows, indent=2))
