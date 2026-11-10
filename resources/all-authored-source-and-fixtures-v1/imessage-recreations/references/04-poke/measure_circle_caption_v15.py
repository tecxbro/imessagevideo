"""Bounded original circle-phase caption ink, kept separate from artwork rotation."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v14/scene.json').read_text());node=next(l for l in s['layers']if l['id']=='p0015');out=[]
for n in range(40,64):
 t=n/s['fps'];x,y=[at(node,k,t)for k in['x','y']];size=at(node,'fontSize',t);roi=[500,int(y)+6,930,min(1080,int(y+size+45))];boxes=[]
 for file in[p/f'measurements-v8/decoded/{n:06}.png',root/f'outputs/retained-frames/measured-frames-jRBOzF/{n:06}.png']:
  a=np.array(Image.open(file).convert('RGB'));x0,y0,x1,y1=roi;v=a[y0:y1,x0:x1];mask=(v.max(2)<195)&(v.min(2)>65)&(v.max(2)-v.min(2)<14);labels,_=ndimage.label(mask);keep=np.zeros_like(mask)
  for i,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is not None:
    yy,xx=sl
    if yy.stop-yy.start>12 and xx.stop-xx.start>7:keep|=labels==i
  yy,xx=np.where(keep);boxes.append([int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)])
 a,b=boxes;rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1])
 if not(.85<rx<1.15 and .85<ry<1.15):raise ValueError((n,boxes,rx,ry))
 out.append(dict(frame=n,time=t,source=a,candidate=b,x=a[0]-(b[0]-x)*rx,y=a[1]-(b[1]-y)*ry,scaleX=at(node,'scaleX',t)*rx,scaleY=at(node,'scaleY',t)*ry))
(p/'measurements-v8/circle-caption-ink-v15.json').write_text(json.dumps(dict(method='Actual source/native40–63Poke gray caption ink, dynamic text-only ROI excludes blue grain and inbox. Independent native text affine fit; original TextRegular family retained. No unseen6–39fit.',measurements=out),indent=2));print([(r['frame'],r['source'],r['candidate'])for r in out if r['frame']in[40,55,63]])
