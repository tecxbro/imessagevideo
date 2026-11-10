"""Original source prompt spring, excluding each independent badge outline."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v13/scene.json').read_text());g=next(n for n in s['layers']if n['id']=='p0259');node=next(n for n in g['children']if n['id']=='p0258');rows=[]
def box(file,gy):
 a=np.array(Image.open(file).convert('RGB'));bg=float(a[10,10].mean());core=bg*146/255;y0=max(0,int(gy)-20);y1=min(1080,int(gy)+100);c=a[y0:y1,100:1110];mask=(c.max(2)<(bg+core)/2)&(c.min(2)>core-30)&(c.max(2)-c.min(2)<12);linked=ndimage.binary_dilation(mask,iterations=1);lab,_=ndimage.label(linked);removed=[]
 for i,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
  if w>70 and h>55 and xx.start<220:
   mask[max(0,yy.start-2):min(mask.shape[0],yy.stop+2),max(0,xx.start-2):min(mask.shape[1],xx.stop+2)]=False;removed.append([xx.start+100,yy.start+y0,xx.stop+100,yy.stop+y0])
 mask[:,:190]=False;yy,xx=np.where(mask);b=[int(xx.min()+100),int(yy.min()+y0),int(xx.max()+101),int(yy.max()+y0+1)]
 if not(400<b[2]-b[0]<550 and 25<b[3]-b[1]<50 and b[0]>=300):raise ValueError((str(file),b,removed))
 return b,removed
for n in range(664,710):
 t=n/s['fps'];gx,gy,sx,sy=[at(g,k,t)for k in['x','y','scaleX','scaleY']];a,am=box(p/f'measurements-v8/decoded/{n:06}.png',gy);b,bm=box(root/f'outputs/04-poke/cache-history/v12/gsap/{n:06}.png',gy);nx=gx+at(node,'x',t)*sx;ny=gy+at(node,'y',t)*sy;rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);rows.append(dict(frame=n,time=t,source_ink=a,candidate_ink=b,source_badge_removed=am,candidate_badge_removed=bm,x=(a[0]-(b[0]-nx)*rx-gx)/sx,y=(a[1]-(b[1]-ny)*ry-gy)/sy,scaleX=at(node,'scaleX',t)*rx,scaleY=at(node,'scaleY',t)*ry))
(p/'measurements-v8/prompt-spring-ink-v14.json').write_text(json.dumps(dict(method='Native original and currentPNG gray glyph cores normalized by measured scrim background. Distinct h>55 capsule-outline component excluded before glyph bounds. Actual original664–709prompt width/position spring, static proven DisplayMedium face retained.',measurements=rows),indent=2));print([(r['frame'],r['source_ink'],r['candidate_ink'])for r in rows if r['frame']in[664,665,667,674,685,686]])
