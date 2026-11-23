from pathlib import Path
from PIL import Image
import numpy as np
d=Path(__file__).parent
for f in [134,135,136,137,138]:
 p=np.asarray(Image.open(d/'source'/f'{f-133:03}.png')).astype(float)
 print('FRAME',f)
 y0=[240,300,310,336,360][f-134]; y1=y0+103
 for left,right in zip([165,210,250,290,335,380,425,465,500,535,575,620,665,705,745,790],
                       [210,250,290,335,380,425,465,500,535,575,620,665,705,745,790,835]):
  a=p[y0:y1,left:right]
  r,g,b=np.moveaxis(a,2,0)
  rec=[]
  for prof,fn in [('r',r-np.minimum(g,b)),('g',g-np.maximum(r,b)*.78),('b',b-np.minimum(g,r))]:
   pix=fn*(np.ptp(a,axis=2)>25)
   grade=np.clip(pix-35,0,255)
   if grade.sum()>450:
    yy=np.arange(y0,y1)[:,None]
    xx=np.arange(left,right)[None,:]
    rec.append((prof,round(float((xx*grade).sum()/grade.sum()),1),round(float((yy*grade).sum()/grade.sum()),1),round(float(np.quantile(pix[pix>35],.8)),0)))
  if rec:print(left,right,rec)
