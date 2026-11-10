from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, json
R = Path('/workspace/imessage-recreations')
D = R / 'verification/final/06-gallery/v22'
cap = json.load(open(D / 'check-first/capture.json'))
rows = []
for f in cap['frameIndices']:
    sf = f if f < 1049 else f + 181
    rect = (0,0,1920,1080) if sf < 1230 else (200,300,1720,900)
    src = Image.open(D / (f'source-done/{sf:06d}.png' if sf < 1230 else f'source-late/{sf:06d}.png')).convert('RGB')
    old = Image.open(R / f'outputs/06-gallery/frames-gsap/{f:06d}.png').convert('RGB').crop(rect)
    new = Image.open(D / f'check-first/{f/30:.3f}.png').convert('RGB').crop(rect)
    a = np.array(src).astype(float)
    b = np.array(old).astype(float)
    c = np.array(new).astype(float)
    before = float(np.abs(a-b).mean())
    after = float(np.abs(a-c).mean())
    rows.append(dict(sourceFrame=sf,outputFrame=f,before=before,after=after,delta=after-before,roi=rect))
    if sf < 1230:
        rect2 = (400,630,1300,810) if sf == 208 else (400,430,1520,850)
        src = src.crop(rect2)
        old = old.crop(rect2)
        new = new.crop(rect2)
    canvas = Image.new('RGB',(1500,260),'#ccc')
    draw = ImageDraw.Draw(canvas)
    for x,im,label in [(0,src,'source'),(500,old,'before'),(1000,new,'after')]:
        im.thumbnail((498,230))
        canvas.paste(im,(x,25))
        draw.text((x+5,3),f'{sf}/{f} {label}',fill='black')
    canvas.save(D / f'first-{sf:06d}.jpg',quality=94)
(D/'first-metrics.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
