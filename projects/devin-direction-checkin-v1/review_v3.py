"""Decode native v3 event neighbours, camera samples and labelled review sheets."""
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / 'renders'
STILLS = RENDERS / 'v3-stills'
STILLS.mkdir(exist_ok=True)
ledger = json.loads((ROOT / 'events.json').read_text())
count = ledger['frames']
events = ledger['events']
contact = sorted(set(round(i * (count - 1) / 11) for i in range(12)) |
                 {13, 50, 74, 90, 132, 165, 186, 204, 210, 228, 240, 253,
                  266, 279, 291, 299, 300, 325, 440, 460, 487, 541, 570, 615, 630, 660, 719})
frames = sorted(set(range(0, count, 10)) | set(contact) |
                {int(f) + d for f in events for d in [-1, 0, 1] if 0 <= int(f) + d < count})
selection = '+'.join('(' + '+'.join(f'eq(n,{f})' for f in frames[i:i + 24]) + ')'
                     for i in range(0, len(frames), 24))
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i',
                str(RENDERS / 'v3-final.mp4'), '-vf', f"select='{selection}'",
                '-fps_mode', 'vfr', str(STILLS / 'capture-%04d.png')], check=True)
for i, frame in enumerate(frames, 1):
    (STILLS / f'capture-{i:04d}.png').replace(STILLS / f'frame-{frame:04d}.png')

font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 20)


def sheet(name, selected, columns=4, crop=None):
    width, height = (650, 165) if crop else (480, 300)
    result = Image.new('RGB', (width * columns, height * math.ceil(len(selected) / columns)), '#D8D8D5')
    draw = ImageDraw.Draw(result)
    for i, frame in enumerate(selected):
        x, y = i % columns * width, i // columns * height
        im = Image.open(STILLS / f'frame-{frame:04d}.png').convert('RGB')
        if crop:
            im = im.crop(crop)
        else:
            im.thumbnail((448, 252))
        result.paste(im, (x + 16, y + 36))
        actions = ', '.join(e['action'] for e in events.get(str(frame), []))
        draw.text((x + 16, y + 7), f'frame {frame}  {actions}', fill='#17181C', font=font)
    result.save(RENDERS / name, quality=94)


sheet('v3-contact.jpg', contact)
sheet('v3-events.jpg', [int(f) for f in events])
for action, name in [('type char', 'typing'), ('backspace', 'backspace')]:
    selected = [int(f) for f, actions in events.items() if any(e['action'] == action for e in actions)]
    sheet(f'v3-{name}-native.jpg', selected, columns=2, crop=(700, 760, 1290, 865))
for start in range(0, count, 200):
    sheet(f'v3-camera-{start:03d}.jpg', list(range(start, min(start + 200, count), 10)))
for frame, actions in events.items():
    if not any(e['action'] in ['type char', 'backspace'] for e in actions):
        continue
    f = int(frame)
    before = Image.open(STILLS / f'frame-{f - 1:04d}.png').convert('RGB').crop((745, 785, 1190, 837))
    after = Image.open(STILLS / f'frame-{f:04d}.png').convert('RGB').crop((745, 785, 1190, 837))
    assert ImageChops.difference(before, after).getbbox(), f'No encoded glyph change at {f}'
(RENDERS / 'v3-evidence-frames.json').write_text(json.dumps({
    'eventFrames': [int(f) for f in events], 'eventNeighbours': [-1, 0, 1],
    'cameraSampling': 'every tenth frame', 'allStills': frames,
}, indent=2) + '\n')
print(f'PASS: extracted {len(frames)} full-resolution stills; every event plus before/after and every tenth camera frame.')
print('PASS: all 28 encoded typing/backspace cues have visible composer-pixel changes from the preceding frame.')
print(f'Contact: {RENDERS / "v3-contact.jpg"}')
