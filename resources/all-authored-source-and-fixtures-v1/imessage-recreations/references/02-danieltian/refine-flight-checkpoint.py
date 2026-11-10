"""The pre-phone flight has different text/color and capsule proportions; do not stretch the phone bubble to stand in for it."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/root-early-end-measure';P=R/'early-end-refinement.json';p=json.loads(P.read_text());ledger=[]
def ar(n):return np.array(Image.open(M/f'frame-{n:04d}.png').convert('RGB')).astype(float)
def bbox(n):
 a=ar(n);mask=(a[:,:,2]-a[:,:,0]>10)&(a[:,:,1]>85)&(a[:,:,2]>175);lab,c=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());choices=[]
 for li,s in enumerate(ndimage.find_objects(lab),1):
  if not s:continue
  y,x=s;w=x.stop-x.start;h=y.stop-y.start
  if w>400 and h>40:choices.append((areas[li],[x.start,y.start,x.stop,y.stop]))
 return max(choices,key=lambda z:z[0])[1] if choices else None
can=bbox(177);a=ar(177);l,t,r,b=can;roi=a[t:b,l:r];bodypixels=roi[(roi[:,:,2]-roi[:,:,0]>10)&(roi.max(2)>220)];bg=np.median(bodypixels,0);dark=(roi.max(2)<205)&(roi.max(2)-roi.min(2)<70);inks=roi[dark];ink=np.median(inks[inks.mean(1)<np.quantile(inks.mean(1),.35)],0);alpha=np.clip((bg.mean()-roi.mean(2))/(bg.mean()-ink.mean()),0,1);alpha[roi.max(2)>210]=0;gd,gs=trace_alpha(alpha);shape=np.clip((253-roi[:,:,0])/(253-bg[0]),0,1);shape[ndimage.binary_fill_holes(shape>.35)]=1;bd,bs=trace_alpha(shape);ms=[];fills=[];textfills=[]
for n in range(175,180):
 box=bbox(n)
 if box is None:continue
 ll,tt,rr,bb=box;sx=(rr-ll)/(r-l);sy=sx;y=tt if tt>1 else bb-(b-t)*sx;aa=ar(n);reg=aa[max(0,tt):bb,ll:rr];bodypix=reg[(reg[:,:,2]-reg[:,:,0]>10)&(reg.max(2)>220)];bgc=np.median(bodypix,0).astype(int);glyphs=reg[(reg.max(2)<205)&(reg.max(2)-reg.min(2)<70)];ic=np.median(glyphs[glyphs.mean(1)<np.quantile(glyphs.mean(1),.35)],0).astype(int);ms.append(dict(t=n/30,x=ll,y=y,scaleX=sx,scaleY=sy));fills.append(dict(t=n/30,value='#'+''.join(f'{v:02x}' for v in bgc)));textfills.append(dict(t=n/30,value='#'+''.join(f'{v:02x}' for v in ic)))
layer=next(l for l in p['new_layers'] if l['id']=='early-sent-message-flight');layer.update(children=[dict(id='early-flight-body',type='path',d=bd,fill='#'+''.join(f'{int(v):02x}' for v in bg),keyframes={'fill':fills}),dict(id='early-flight-glyphs',type='path',d=gd,fill='#'+''.join(f'{int(v):02x}' for v in ink),keyframes={'fill':textfills},semanticText='muse, my boss wants a team offsite\ntmr. can u help?',sourceFrame=177)],start=ms[0]['t'],end=6.,keyframes={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']});p['provenance'].append(dict(kind='native pre-phone flight checkpoint',sourceFrame=177,sourceBounds=can,measurements=ms,diagnosis='The flight is not the phone capsule enlarged: source text stays gray and the capsule height/tail differ. Reconstruct that bounded graphic from its own native source glyph/body contours.',glyphStats=gs,bodyStats=bs));P.write_text(json.dumps(p,indent=2));print('Native pre-phone flight reconstructed from its own source pose')
