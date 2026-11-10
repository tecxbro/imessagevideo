"""Observed typing states and native font registration for the frosted preview."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

p = Path(__file__).parent
poses = {row['frame']: row.get('poke_pose') for row in json.loads(
    (p / 'measurements-v8/intro-pose-fit.json').read_text())['measurements']}
text = 'sarah wants to\ngrab dinner tmrw'
# Visible glyph states read from exact native source frames in the saved contact
# sheet. Trailing spaces are unobservable and need not create extra states.
counts = {109: 2, 110: 4, 111: 5, 112: 7, 113: 9, 114: 11, 115: 11,
          116: 14, 117: 17, 118: 19, 119: 19, 120: 22, 121: 24,
          122: 26, 123: 26, 124: 29, 125: 31}
font = ImageFont.truetype(str(p.parent.parent / 'shared/fonts/SF-Pro-Text-Regular.otf'), 132)
origin = np.array([153.5, 56.0])
rows = []
for frame in range(109, 142):
    pose = poses.get(min(frame, 131))
    if not pose:
        continue
    source = np.array(Image.open(p / f'measurements-v8/decoded/{frame:06}.png').convert('RGB'))
    width = 476 * pose['scale']
    roi = (max(0, round(pose['x'] - .8 * width)),
           max(0, round(pose['y'] - .8 * width)),
           min(1440, round(pose['x'] + .8 * width)),
           min(1080, round(pose['y'] - 17 if frame >= 111 else pose['y'] + .3 * width)))
    x, y, x2, y2 = roi
    crop = source[y:y2, x:x2].astype(float)
    gray = crop.mean(axis=2)
    mask = (crop.max(axis=2) - crop.min(axis=2) < 20) & (crop.max(axis=2) < 100)
    yy, xx = np.where(mask)
    if len(xx) < 10:
        continue
    bbox = [int(xx.min() + x), int(yy.min() + y),
            int(xx.max() + x + 1), int(yy.max() + y + 1)]
    alpha = np.where(mask, (255 - gray) / 255, 0)
    alpha = alpha[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
    count = counts.get(frame, 31)
    prefix = text[:count]
    canvas = Image.new('L', (1600, 720))
    draw = ImageDraw.Draw(canvas)
    for line, value in enumerate(prefix.split('\n')):
        draw.text(((43 if line == 0 else 25) * 4, (18 + 37 * line) * 4), value, font=font, fill=255)
    canvas = canvas.resize((400, 180), Image.Resampling.LANCZOS)
    choices = []
    for angle in np.arange(-10, 3.01, .5):
        rotated = canvas.rotate(-angle, center=tuple(origin), resample=Image.Resampling.BICUBIC)
        ink_box = rotated.getbbox()
        tw, th = ink_box[2] - ink_box[0], ink_box[3] - ink_box[1]
        sx, sy = alpha.shape[1] / tw, alpha.shape[0] / th
        if not (.65 < sx < 1.35 and .65 < sy < 1.35 and .8 < sx / sy < 1.25):
            continue
        candidate = np.array(rotated.crop(ink_box).resize(
            (alpha.shape[1], alpha.shape[0]), Image.Resampling.LANCZOS)) / 255
        opacity = float(np.clip((candidate * alpha).sum() / max(1e-9, (candidate * candidate).sum()), 0, 1.1))
        score = float(np.mean((alpha - candidate * opacity)**2))
        choices.append((score, float(angle), (sx + sy) / 2, ink_box, opacity))
    if not choices:
        rows.append({'frame': frame, 'time': frame * 1001 / 30000,
                     'text': prefix, 'source_ink_bbox': bbox, 'registration_failed': True})
        continue
    score, angle, scale, ink_box, opacity = min(choices)
    offset = origin + scale * (np.array(ink_box[:2]) - origin)
    rows.append({'frame': frame, 'time': frame * 1001 / 30000,
                 'text': prefix, 'source_ink_bbox': bbox,
                 'x': bbox[0] - float(offset[0]), 'y': bbox[1] - float(offset[1]),
                 'rotation': angle, 'scaleX': scale, 'scaleY': scale,
                 'text_alpha_fit': opacity, 'glyph_alpha_mse': score})
(p / 'measurements-v8/preview-typing-fit.json').write_text(json.dumps({
    'method': 'Exact visible typing states from native frame contact sheet; official TextRegular33 font rendered at4x then registered to native gray glyph masks. Parent rotation/scale measured separately from favorites.',
    'origin': origin.tolist(), 'line_height': 37,
    'reference_contact_sheet': 'outputs/04-poke/preview-typing-source.jpg',
    'measurements': rows}, indent=2))
for row in rows[::4]:
    print(row)
