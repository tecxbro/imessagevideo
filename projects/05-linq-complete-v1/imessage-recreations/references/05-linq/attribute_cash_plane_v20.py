"""Read-only regional attribution of the parent's native opacity candidate."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
frame = 820
scene = json.load(open('outputs/05-linq/final-v19/scene.json'))
root = next(q for q in scene['layers'] if q['id'] == 'linq-measured-v6-group-36')
panel = next(q for q in root['children'] if q['id'] == 'v10-cash-panel')
py = next(q['value'] for q in panel['keyframes']['y'] if abs(q['t'] * 30 - frame) < 1e-5)
def rgb(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(float)
reference = rgb(f'references/05-linq/measurements/composer-v19/native/source-{frame:06}.png')
old = rgb(f'outputs/05-linq/frames-gsap/{frame:06}.png')
new = rgb(f'outputs/05-linq/root-cash-plane-v20/checkpoints/{frame / 30:.3f}.png')
error_change = np.abs(reference - new).mean(2) - np.abs(reference - old).mean(2)
yy, xx = np.mgrid[:720, :960]
world_y = yy - py
panel_mask = (xx >= 182) & (xx < 778) & (world_y >= 230) & (world_y < 701)
regions = {}
taken = np.zeros(panel_mask.shape, bool)
boxes = [
    ('amount', [285, 340, 610, 455]),
    ('plus', [610, 345, 714, 455]),
    ('footerButtons', [230, 555, 730, 680]),
    ('showKeypad', [370, 465, 590, 535]),
]
for name, (x0, y0, x1, y1) in boxes:
    mask = panel_mask & (xx >= x0) & (xx < x1) & (world_y >= y0) & (world_y < y1)
    taken |= mask
    regions[name] = mask
regions['remainingPanel'] = panel_mask & ~taken
regions['outsidePanel'] = ~panel_mask
report = {'frame': frame, 'panelY': py, 'globalDelta': float(error_change.mean()), 'regions': {}}
for name, mask in regions.items():
    report['regions'][name] = {
        'pixels': int(mask.sum()),
        'contributionToGlobalDelta': float(error_change[mask].sum() / error_change.size),
        'meanLocalErrorChange': float(error_change[mask].mean()) if mask.any() else 0,
    }
Path('verification/05-cash-plane820-attribution.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
