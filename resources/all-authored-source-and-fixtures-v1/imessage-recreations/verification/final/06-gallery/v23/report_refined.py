from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/workspace/imessage-recreations');D=R/'verification/final/06-gallery/v23';cap=json.load(open(D/'check-refined/capture.json'));scope=json.load(open(D/'scope-refined.json'));changed={n for a,b in scope['exactChangedRanges'] for n in range(a,b+1)};rows=[]
for f in cap['frameIndices']:
 a=Image.open(D/f'source-full/{f-679:06d}.png').convert('RGB');b=Image.open(R/f'outputs/06-gallery/frames-gsap/{f:06d}.png').convert('RGB');c=Image.open(D/f'check-refined/{f/30:.3f}.png').convert('RGB');A,B,C=[np.array(im).astype(float) for im in [a,b,c]];old=float(np.abs(A-B).mean());new=float(np.abs(A-C).mean());pd=float(np.abs(B-C).mean());rows.append(dict(frame=f,changed=f in changed,before=old,after=new,delta=new-old,pixelDelta=pd))
 if f in [714,715,720,726,734,735,740,745,746,747,754,765,769,770,771,776,780,781,782,790,794]:
  q=Image.new('RGB',(1500,550),'#ddd');draw=ImageDraw.Draw(q)
  for x,im,label in [(0,a,'source'),(500,b,'native22'),(1000,c,'native23')]:
   im=im.crop((630,315,1280,1000));im.thumbnail((498,520));q.paste(im,(x,25));draw.text((x+4,4),f'{f} {label}',fill='black')
  q.save(D/f'refined-{f:06d}.jpg',quality=94)
(D/'refined-metrics.json').write_text(json.dumps(rows,indent=2));z=[x for x in rows if x['changed']];print('changed',len(z),'mean',np.mean([x['before'] for x in z]),np.mean([x['after'] for x in z]));print('regressions',[(x['frame'],round(x['delta'],5)) for x in z if x['delta']>=0]);print('controls',[(x['frame'],x['pixelDelta']) for x in rows if not x['changed']])
