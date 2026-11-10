"""Original native98–108 caption ink with explicitly censored side bounds."""
from pathlib import Path
from PIL import Image
import numpy as np,json
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v16/scene.json').read_text());rows=[]
for frame in range(98,109):
 t=frame/s['fps']
 for gid,nid,side in [('p0007','p0006','left'),('p0010','p0009','right')]:
  g=next(l for l in s['layers'] if l['id']==gid);node=next(l for l in g['children'] if l['id']==nid);gx,gy,sx,sy,op=[at(g,k,t)for k in ['x','y','scaleX','scaleY','opacity']];y0=int(gy+145*sy);y1=min(770,int(gy+225*sy));x0,x1=(0,400) if side=='left' else (1060,1440);bounds=[]
  for folder in [p/'measurements-v8/decoded',root/'outputs/04-poke/cache-history/v15/gsap']:
   a=np.array(Image.open(folder/f'{frame:06}.png').convert('RGB')).astype(float)[y0:y1,x0:x1];gray=a.mean(2);mask=(gray<255-(255-133)*op*.5)&(gray>255-(255-133)*op*1.7)&((a.max(2)-a.min(2))<4);yy,xx=np.where(mask);b=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)];bounds.append(b)
  a,b=bounds;rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);censored=(side=='left' and frame<=106) or (side=='right' and frame<=107)
  if censored:rx=ry
  nx=gx+node['x']*sx;ny=gy+node['y']*sy
  if side=='left' and censored:newx=a[2]-(b[2]-nx)*rx
  else:newx=a[0]-(b[0]-nx)*rx
  newy=a[1]-(b[1]-ny)*ry
  rows.append(dict(frame=frame,time=t,parent=gid,id=nid,source_ink=a,candidate_ink=b,side_censored=censored,x=(newx-gx)/sx,y=(newy-gy)/sy,scaleX=rx,scaleY=ry))
report=dict(method='Exact original/native candidate gray glyph cores. Parent camera kept separate. Native source side-censoring is declared; visible width is never treated as complete scale. For a clipped caption, source full glyph height gives an initial uniform font-scale proposal and surviving inner text edge providesX; actual browser proof required. TextRegular retained.',measurements=rows);(p/'measurements-v8/caption-ink-98-108-v17.json').write_text(json.dumps(report,indent=2));print([(r['frame'],r['id'],r['source_ink'],r['candidate_ink'],r['side_censored'])for r in rows])
