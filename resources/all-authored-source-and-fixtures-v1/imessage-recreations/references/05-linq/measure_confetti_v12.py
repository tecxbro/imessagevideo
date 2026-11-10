"""Diagnose actual colored particle components against a clean static app plate."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects,map_coordinates
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';O=D/'measurements/confetti-v12';O.mkdir(exist_ok=True);s=json.loads((D/'scene-chess-tap-glow-v12.json').read_text());board=next(q for q in s['layers'] if q['id']=='broad-v5-group-41');xs={round(p['t']*30):p['value'] for p in board['keyframes']['x']};base=np.array(Image.open(F/'000898.png').convert('RGB')).astype(np.float32);yy,xx=np.indices(base.shape[:2]);components={};four=next(q for q in s['layers'] if q['id']=='rich-group-10');fx={round(q['t']*30):q['value'] for q in four['keyframes']['x']}
for f in range(903,947):
 source=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32);dx=xs[f]-xs[898];expected=np.stack([map_coordinates(base[:,:,c],[yy,xx-dx],order=1,mode='constant',cval=255) for c in range(3)],2);delta=source-expected;chroma=delta.max(2)-delta.min(2);r,g,b=source[:,:,0],source[:,:,1],source[:,:,2];palette=((b>r+15)&(g>r+10))|((r>g+25)&(b>g-15)&(r>140))|((r>200)&(g>120)&(b<g-30)&(r>g+8))|((g>r+15)&(g>b+8));mask=(chroma>18)&(np.abs(delta).max(2)>20)&palette
 mask[(yy<100)&(xx>xs[f]+10)&(xx<xs[f]+110)]=False
 # The native badge and dynamic assistant glow are separate app components.
 mask[(yy<150)&(xx>xs[f]+320)&(xx<xs[f]+530)]=False
 mask[(yy>309)&(yy<412)&(xx>xs[f]+101)&(xx<xs[f]+386)]=False
 lab,n=label(mask);rows=[]
 for i,sl in enumerate(find_objects(lab),1):
  if sl is None:continue
  m=lab[sl]==i;area=int(m.sum());h,w=m.shape
  if not (6<=area<=120 and w<=24 and h<=24):continue
  ys0,xs0=np.where(m);color=source[sl][m].mean(0);rows.append(dict(box=[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop],area=area,color=color.tolist(),mask=m.astype(int).tolist()))
 components[f]=rows
 if f in [909,924,939]:
  image=Image.fromarray(np.uint8(source));draw=ImageDraw.Draw(image)
  for r in rows:draw.rectangle(r['box'],outline='red')
  image.save(O/f'{f}-detected.png')
print('counts',[(f,len(r)) for f,r in components.items()]);(D/'confetti-v12-components.json').write_text(json.dumps(components,indent=2))
