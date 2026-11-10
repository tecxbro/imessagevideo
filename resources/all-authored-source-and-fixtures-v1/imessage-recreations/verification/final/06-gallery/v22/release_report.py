from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, json, hashlib
R = Path('/workspace/imessage-recreations')
D = R/'verification/final/06-gallery/v22'
cap = json.load(open(D/'check-exact/capture.json'))
scope = json.load(open(D/'scope-exact-boundary.json'))
changed = {n for a,b in scope['exactChangedRanges'] for n in range(a,b+1)}
rows = []
triptychs = []
for f in cap['frameIndices']:
    sf = f if f < 1049 else f+181
    srcpath = D/(f'source-done/{sf:06d}.png' if sf < 1230 else f'source-full/{sf:06d}.png')
    src = Image.open(srcpath).convert('RGB')
    old = Image.open(R/f'outputs/06-gallery/frames-gsap/{f:06d}.png').convert('RGB')
    newpath = D/f'check-exact/{f/30:.3f}.png'
    new = Image.open(newpath).convert('RGB')
    a,b,c = [np.asarray(im).astype(float) for im in [src,old,new]]
    before,after = [float(np.abs(a-x).mean()) for x in [b,c]]
    delta = float(np.abs(b-c).mean())
    row = dict(sourceFrame=sf,outputFrame=f,changed=f in changed,beforeMAE=before,afterMAE=after,deltaMAE=after-before,nativePixelDelta=delta,sourceSHA256=hashlib.sha256(srcpath.read_bytes()).hexdigest())
    rows.append(row)
    crop = (400,430,1520,850) if sf < 1230 else (200,300,1720,900)
    canvas = Image.new('RGB',(1500,250),'#ddd')
    draw = ImageDraw.Draw(canvas)
    for x,im,label in [(0,src,'source'),(500,old,'native21'),(1000,new,'native22')]:
        im = im.crop(crop)
        im.thumbnail((498,225))
        canvas.paste(im,(x,23))
        draw.text((x+4,4),f'{sf}/{f} {label}',fill='black')
    dest = D/f'release-{sf:06d}.jpg'
    canvas.save(dest,quality=94)
    triptychs.append(dest.name)
selected = [r for r in rows if r['changed']]
controls = [r for r in rows if not r['changed']]
report = dict(sceneSHA256=cap['sceneSHA256'],sourceSelection='fresh exact integer source-frame decode; source/output181frame removal map',checkedNative=len(rows),changedNative=len(selected),changedNativeCovered=sorted(r['outputFrame'] for r in selected)==sorted(changed),meanBefore=float(np.mean([r['beforeMAE'] for r in selected])),meanAfter=float(np.mean([r['afterMAE'] for r in selected])),maxAfter=max(r['afterMAE'] for r in selected),allChangedImprove=all(r['afterMAE']<r['beforeMAE'] for r in selected),allControlsPixelIdentical=all(r['nativePixelDelta']==0 for r in controls),rows=rows,limitations='Quantitative/source-native review closes demonstrated semantic words/reveal/lifecycle defects. Remaining AA, blur/shutter, bitmap UI and photographed-material differences are not a100% identity certification.')
(D/'native-release.json').write_text(json.dumps(report,indent=2))
html = '<!doctype html><meta charset="utf-8"><title>Source06 native22 late transition gate</title><style>body{font-family:system-ui;margin:24px;background:#eee}img{max-width:100%;display:block;margin:12px 0}</style><h1>Source06 native22 late transition gate</h1><pre>'+json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2)+'</pre>'+''.join('<img src="'+x+'">' for x in triptychs)
(D/'index.html').write_text(html)
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if not report['changedNativeCovered'] or not report['allChangedImprove'] or not report['allControlsPixelIdentical']:
    raise SystemExit('Native gate failed; inspect actual row before retry')
