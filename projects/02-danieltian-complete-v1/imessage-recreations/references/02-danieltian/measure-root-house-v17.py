"""Fit one authentic house artwork independently of the unfolding text row."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
D = Path(__file__).resolve().parent
OUT = D / 'root-house-v17'
SOURCE = D / 'v17-refinement/reasoning-source'
asset = D.parent.parent / 'outputs/02-danieltian/final-v16/assets/6dd19cc3781e3ef0d57c16546dfb5a9cfadeebdf0e324f32cc8906d2cd96c28e.png'
template = Image.open(asset).convert('RGB')
colors = json.loads((OUT / 'color-measurements.json').read_text())
boxes = {row['frame']: row['sourceColorBox'] for row in colors}
rows = []
previous = None
for frame in range(289, 375):
    source = np.asarray(Image.open(SOURCE / f'source-{frame:04}.png').convert('RGB')).astype(float)
    if frame not in boxes:
        roi = source[480:606, 180:400]
        mask = roi.max(2) - roi.min(2) > 10
        yy, xx = np.where(mask)
        boxes[frame] = [int(xx.min()+180), int(yy.min()+480), int(xx.max()+181), int(yy.max()+481)] if len(xx) else None
    box = boxes[frame]
    if box:
        initial = [box[0], box[1], round(69*(box[2]-box[0])/63), round(68*(box[3]-box[1])/61)]
    elif previous:
        initial = [round(previous['x']+1), previous['y'], previous['width'], previous['height']]
    else:
        raise ValueError('Cannot locate first house')
    x0, y0 = int(initial[0])-8, int(initial[1])-8
    size = 104
    observed = source[y0:y0+size, x0:x0+size]
    if observed.shape != (size, size, 3):
        raise ValueError('Invalid fit window')
    resized = {}
    def evaluate(values):
        x, y, width, height = map(int, values)
        if width < 4 or height < 4:
            return float('inf'), 0.
        key = (width, height)
        if key not in resized:
            resized[key] = np.asarray(template.resize(key, Image.Resampling.BICUBIC)).astype(float)
        local_x, local_y = x-x0, y-y0
        if local_x < 0 or local_y < 0 or local_x+width > size or local_y+height > size:
            return float('inf'), 0.
        delta = np.zeros((size, size, 3), dtype=float)
        delta[local_y:local_y+height, local_x:local_x+width] = resized[key]-253
        denominator = float(np.sum(delta*delta))
        alpha = float(np.clip(np.sum((observed-253)*delta)/denominator, 0, 1)) if denominator else 0.
        error = float(np.mean((observed-(253+alpha*delta))**2))
        return error, alpha
    values = list(map(int, initial))
    score, alpha = evaluate(values)
    for step in [2, 1]:
        for repeat in range(2):
            for parameter in range(4):
                for direction in [-1, 1]:
                    proposal = values.copy()
                    proposal[parameter] += step*direction
                    trial_score, trial_alpha = evaluate(proposal)
                    if trial_score < score:
                        values, score, alpha = proposal, trial_score, trial_alpha
    row = dict(frame=frame, x=values[0], y=values[1], width=values[2], height=values[3], opacity=alpha, fitMSE=score, sourceColorBox=box)
    rows.append(row)
    previous = row
    if frame in [289,290,291,300,320,340,360,361,370,374]:
        print(json.dumps(row), flush=True)
(OUT / 'measured-world-poses.json').write_text(json.dumps({'asset':str(asset), 'background':253, 'firstFrame':289, 'lastFrame':374, 'poses':rows}, indent=2)+'\n')
