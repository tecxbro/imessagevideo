from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).parent
yy,xx=np.mgrid[0.04:0.99:22j,0.04:0.99:22j]
def fit(f,kind):
 a=np.asarray(Image.open(p/'source'/f'{f:06d}.png')).astype(float)
 iy,ix=(yy*500).astype(int),(xx*500).astype(int)
 target=np.array([[np.median(a[y-4:y+4,x-4:x+4,k]) for k in range(3)] for y,x in zip(iy.ravel(),ix.ravel())])
 valid=((xx<.19)|(xx>.81)|(yy<.25)|(yy>.73)).ravel()
 x,y=xx.ravel()[valid],yy.ravel()[valid]
 data=253-target[valid]
 def evaluate(q):
  cx,cy,sx,sy,k=q
  field=np.exp(-((x-cx+k*(y-cy))/sx)**2-((y-cy)/sy)**2)
  amp=np.clip(np.linalg.lstsq(field[:,None],data,rcond=None)[0][0],0,250)
  return ((field[:,None]*amp-data)**2).mean(),amp
 q=np.array([.94,.97,.5,.33,.0] if kind!='apps' else [.47,.55,.35,.35,.0])
 score,amp=evaluate(q)
 for step in [.10,.05,.025,.0125,.00625]:
  for _ in range(9):
   for i in range(len(q)):
    for direction in [-1,1]:
     v=q.copy();v[i]+=step*direction
     if min(v[2:4])<.10: continue
     err,new=evaluate(v)
     if err < score:q,score,amp=v,err,new
 print(f,*np.round(q,3),*np.round(amp,1),'rmse',round(score**.5,2))
for f,k in [(162,'title'),(183,'title'),(201,'title'),(212,'title'),(496,'apps'),(715,'closing'),(724,'closing'),(732,'closing'),(752,'closing'),(765,'closing')]:fit(f,k)
