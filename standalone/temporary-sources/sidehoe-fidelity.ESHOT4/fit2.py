from PIL import Image
import numpy as np
from pathlib import Path
import json
p=Path(__file__).parent
yy,xx=np.mgrid[.02:.983:26j,.02:.983:26j]
def fit(f):
 a=np.asarray(Image.open(p/'source'/f'{f:06d}.png')).astype(float)
 iy,ix=(yy*500).astype(int),(xx*500).astype(int)
 target=np.array([[np.median(a[y-5:y+6,x-5:x+6,k]) for k in range(3)] for y,x in zip(iy.ravel(),ix.ravel())])
 # Foreground windows omitted. Channel maxima below 225 indicate unrelated artwork.
 if f < 213:
  mask=((xx<.21)|(xx>.79)|(yy<.26)|(yy>.665))
 else:
  mask=((xx<.24)|(xx>.76)|(yy<.27)|(yy>.73))
 if f>=210 and f<=212:
  mask &= (yy<.78)|(xx<.27)|(xx>.62)
 valid=mask.ravel() & (target.max(1)>225)
 x,y=xx.ravel()[valid],yy.ravel()[valid]
 data=253-target[valid]
 def mat(q):
  return np.stack([np.exp(-((x-cx+k*(y-cy))/sx)**2-((y-cy)/sy)**2) for cx,cy,sx,sy,k in q],axis=1)
 def evaluate(q):
  basis=mat(q)
  amp=np.clip(np.linalg.lstsq(basis,data,rcond=None)[0],-50,250)
  err=((basis@amp-data)**2).mean()
  return err,amp
 q=np.array([[1.05,.86,.55,.36,.25],[.18,1.12,.50,.32,-.83]])
 score,amp=evaluate(q)
 for step in [.15,.075,.038,.019,.009]:
  for _ in range(8):
   for j in range(2):
    for i in range(5):
     for direction in [-1,1]:
      v=q.copy();v[j,i]+=step*direction
      if np.min(v[:,2:4])<.1: continue
      err,new=evaluate(v)
      if err < score:q,score,amp=v,err,new
 # sort broad lobe on right first for interpolation
 order=np.argsort(q[:,0])[::-1]
 fields=np.column_stack([q[order],amp[order]]).ravel()
 print(f, round(score**.5,2), np.round(q[order],2),np.round(amp[order],1))
 return [f]+np.round(fields,4).tolist()
data={"title": [fit(f) for f in (162,168,183,187,196,201,205,209,212)],
      "closing":[fit(f) for f in (708,715,724,732,741,752,761,765)]}
(p/'wash-fits.json').write_text(json.dumps(data))
