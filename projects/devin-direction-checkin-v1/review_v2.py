"""Extract numbered full-resolution evidence and separated review sheets."""
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / 'renders'
STILLS = RENDERS / 'v2-stills'
STILLS.mkdir(exist_ok=True)
ledger = json.loads((ROOT / 'events.json').read_text())['events']
frames = sorted(set(range(0, 840, 10)) | {int(f) for f in ledger} |
                {15, 60, 265, 300, 419, 424, 432, 444, 560, 575, 579, 580,
                 607, 661, 690, 700, 705, 728, 735, 749, 750, 780, 810, 839})
selection = '+'.join('(' + '+'.join(f'eq(n,{f})' for f in frames[i:i + 24]) + ')'
                     for i in range(0, len(frames), 24))
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i',
                str(RENDERS / 'v2-revised.mp4'), '-vf', f"select='{selection}'",
                '-fps_mode', 'vfr', str(STILLS / 'capture-%04d.png')], check=True)
for i, frame in enumerate(frames, 1):
    (STILLS / f'capture-{i:04d}.png').replace(STILLS / f'frame-{frame:04d}.png')

font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 20)


def sheet(name, selected, columns=4, detail=False):
    width, height = (650, 150) if detail else (480, 300)
    result = Image.new('RGB', (width * columns, height * math.ceil(len(selected) / columns)), '#D8D8D5')
    draw = ImageDraw.Draw(result)
    for i, frame in enumerate(selected):
        x, y = i % columns * width, i // columns * height
        im = Image.open(STILLS / f'frame-{frame:04d}.png').convert('RGB')
        if detail:
            im = im.crop((700, 760, 1290, 865))
        else:
            im.thumbnail((448, 252))
        result.paste(im, (x + 16, y + 36))
        actions = ', '.join(e['action'] for e in ledger.get(str(frame), []))
        draw.text((x + 16, y + 7), f'frame {frame}  {actions}', fill='#17181C', font=font)
    result.save(RENDERS / name, quality=94)


contact = sorted({round(i * 839 / 11) for i in range(12)} |
                 {15, 60, 90, 132, 165, 204, 265, 300, 390, 420, 445, 504, 560,
                  575, 580, 607, 608, 638, 661, 690, 700, 705, 735, 750, 780, 810, 839})
# Ensure every overview frame is among the decoded evidence frames.
missing = set(contact) - set(frames)
if missing:
    for frame in sorted(missing):
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i',
                        str(RENDERS / 'v2-revised.mp4'), '-vf', f'select=eq(n\\,{frame})',
                        '-frames:v', '1', str(STILLS / f'frame-{frame:04d}.png')], check=True)
sheet('v2-contact.jpg', contact)
for action, name in [('type char', 'typing'), ('backspace', 'backspace')]:
    selected = [int(f) for f, events in ledger.items() if any(e['action'] == action for e in events)]
    sheet(f'v2-{name}-native.jpg', selected, columns=2, detail=True)
for start in range(0, 840, 200):
    selected = [f for f in range(start, min(start + 200, 840), 10)]
    sheet(f'v2-camera-{start:03d}.jpg', selected)
(RENDERS / 'v2-evidence-frames.json').write_text(json.dumps({
    'eventFrames': [int(f) for f in ledger],
    'cameraSampling': 'every 10th frame, 0 through 830',
    'specialFrames': [15, 60, 300, 700],
    'allStills': sorted(set(frames) | set(contact)),
}, indent=2) + '\n')
print(f'Extracted {len(set(frames) | set(contact))} full-resolution stills, including every event and every 10th frame.')
print(f'Contact: {RENDERS / "v2-contact.jpg"}')
print('Typing/backspace details are native-resolution crops, not downsampled.')
