from pathlib import Path
from PIL import Image, ImageDraw
import json
import numpy as np
D = Path('/workspace/imessage-recreations/verification/final/06-gallery/v23/text-metric-diagnosis')
logs = json.load(open(D / 'actual-font-metrics.json'))
scene = json.load(open(D / 'fixture-scene.json'))
A = np.array(Image.open(D / 'motion-canvas.png').convert('RGB'))
B = np.array(Image.open(D / 'svg.png').convert('RGB'))
rows = []
canvas = Image.new('RGB', (1400, 170 * len(scene['layers'])), '#bbb')
draw = ImageDraw.Draw(canvas)
for j, n in enumerate(scene['layers']):
    x, y = n['x'], n['y']
    h = 190
    if '\n' in n['text']:
        h = 320
    box = (int(x - 10), int(y - 40), int(min(1800, x + 800)), int(min(1600, y + h)))
    bb = {}
    for label, array in [('mc', A), ('svg', B)]:
        crop = array[box[1]:box[3], box[0]:box[2]]
        yy, xx = np.where(crop.mean(2) > 140)
        bb[label] = [int(xx.min() + box[0]), int(yy.min() + box[1]), int(xx.max() + 1 + box[0]), int(yy.max() + 1 + box[1])]
    match = next(z for z in logs if z['id'] == n['id'])
    m = match['transform']
    baseline = m['f'] + m['d'] * match['draw']['y']
    font_top = baseline - m['d'] * match['bottomMetrics']['fontBoundingBoxAscent']
    metric = {
        'id': n['id'], 'text': n['text'], 'fontSize': n['fontSize'],
        'lineHeight': n.get('lineHeight', n['fontSize'] * 1.2),
        'svgInkBox': bb['svg'], 'mcInkBox': bb['mc'],
        'pixelYOffset': bb['mc'][1] - bb['svg'][1],
        'mcFontBoxTopRelInput': font_top - n['y'],
        'rangeTopInParent': match['rangeTopInParent'],
        'rangeTopInLeaf': match['rangeTopInLeaf'],
        'parentHeight': match['parentSize']['y'],
        'leafHeight': match['leafSize']['y'],
        'fontBoundingHeight': match['bottomMetrics']['fontBoundingBoxAscent'] + match['bottomMetrics']['fontBoundingBoxDescent'],
        'emptyFontOffset': match['emptyMetrics']['fontBoundingBoxAscent'],
        'lineHeightCSS': match['lineHeightCSS'],
        'draw': match['draw'], 'ctx': m,
        'bottomMetrics': match['bottomMetrics'],
        'alphabeticMetrics': match['alphabeticMetrics'],
    }
    rows.append(metric)
    for k, (im, label) in enumerate([(Image.fromarray(B), 'SVG'), (Image.fromarray(A), 'MC')]):
        tile = im.crop(box)
        tile.thumbnail((695, 140))
        canvas.paste(tile, (k * 700, j * 170 + 25))
        draw.text((k * 700 + 4, j * 170 + 4), f"{n['id']} {label}", fill='black')
(D / 'measured-summary.json').write_text(json.dumps(rows, indent=2))
canvas.save(D / 'font-top-contact.jpg', quality=95)
print(json.dumps([{k: v for k, v in q.items() if k not in ['ctx', 'bottomMetrics', 'alphabeticMetrics', 'draw']} for q in rows], indent=2))
