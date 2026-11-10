"""Exact native flat-component bounds, with type/color state classification."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;rows=[]
for n in list(range(132,150))+list(range(264,380))+list(range(695,735)):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int);r={'frame':n,'time':n*1001/30000}
 for name,color in [('gray',[236,236,236]),('selected',[228,228,231]),('blue',[8,166,237])]:
  mask=np.abs(a-color).max(2)<5
  if name=='blue':mask=(a[:,:,2]-a[:,:,0]>60)&(a[:,:,1]-a[:,:,0]>50)
  labels,_=ndimage.label(mask);out=[]
  for i,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is None:continue
   yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start;area=int((labels[sl]==i).sum())
   if w>80 and h>10 and area>500:out.append({'bbox':[xx.start,yy.start,xx.stop,yy.stop],'width':w,'height':h,'area':area})
  r[name]=out
 rows.append(r)
(p/'measurements-v8/bubble-tracks.json').write_text(json.dumps({'measurements':rows},indent=2))
for n in [141,265,280,290,300,303,320,345,360,365,371,710,719,730]:print(next(r for r in rows if r['frame']==n))
