from pathlib import Path
import json
from PIL import Image, ImageDraw
import numpy as np

D = Path(__file__).resolve().parent
scene = json.loads((D / 'fixture-scene.json').read_text())
arrays = {key: np.asarray(Image.open(D / file).convert('RGB')) for key, file in {
    'svg': 'svg.png', 'before': 'motion-canvas.png',
    'dom': 'corrected-motion-canvas.png', 'formula': 'formula-motion-canvas.png',
}.items()}
logs = {key: json.loads((D / file).read_text()) for key, file in {
    'before': 'actual-font-metrics.json', 'dom': 'corrected-actual-font-metrics.json',
    'formula': 'formula-actual-font-metrics.json',
}.items()}
rows = []
contact = Image.new('RGB', (1600, len(scene['layers']) * 180), '#aaa')
draw = ImageDraw.Draw(contact)
for index, node in enumerate(scene['layers']):
    x, y = node['x'], node['y']
    height = 320 if '\n' in node['text'] else 190
    box = [max(0, int(x - 10)), max(0, int(y - 35)), min(scene['width'], int(x + 800)), min(scene['height'], int(y + height))]
    crops = {key: value[box[1]:box[3], box[0]:box[2]] for key, value in arrays.items()}
    row = {'id': node['id'], 'text': node['text'], 'box': box, 'modes': {}}
    for col, key in enumerate(['svg', 'before', 'dom', 'formula']):
        crop = crops[key]
        mask = crop.mean(axis=2) > 140
        yy, xx = np.where(mask)
        ink = [int(xx.min()) + box[0], int(yy.min()) + box[1], int(xx.max()) + box[0] + 1, int(yy.max()) + box[1] + 1]
        delta = np.abs(crop.astype(float) - crops['svg'].astype(float))
        row['modes'][key] = {'inkBox': ink, 'maeVsSVG': float(delta.mean()), 'changedPixelsVsSVG': int(np.any(delta, axis=2).sum())}
        tile = Image.fromarray(crop)
        tile.thumbnail((395, 145))
        contact.paste(tile, (col * 400, index * 180 + 30))
        draw.text((col * 400 + 5, index * 180 + 4), f"{node['id']} {key}", fill='black')
    log = next(item for item in logs['formula'] if item['id'] == node['id'])
    row['metrics'] = {key: log[key] for key in ['configuredLineHeight', 'naturalFontBoxHeight', 'rangeTopInParent', 'formulaCorrection', 'formulaMinusDOMCorrection']}
    rows.append(row)
(D / 'correction-measurements.json').write_text(json.dumps(rows, indent=2))
contact.save(D / 'correction-contact.jpg', quality=94)
print(json.dumps(rows, indent=2))
