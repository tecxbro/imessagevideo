"""Restaurant exit bar and independent compact physical rail measurements."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v10/scene.json').read_text());by={g['id']:g for g in s['layers']};fps=s['fps'];exitrows=[];hardware=[]
for n in range(664,676):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int);c=a[500:,600:850];m=(c.min(2)>174)&(c.max(2)<205)&(c.max(2)-c.min(2)<8);l,_=ndimage.label(m);parts=[]
 for i,sl in enumerate(ndimage.find_objects(l),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if 65<w<100 and 5<h<20:parts.append([xx.start+600,yy.start+500,xx.stop+600,yy.stop+500])
 row=dict(frame=n,time=n/fps,scrim_opacity=1-float(np.median(np.r_[a[:,:20].ravel(),a[:,-20:].ravel()]))/255)
 if parts:
  b=parts[0];row.update(grab_bbox=b,sheet_y=b[1]-10)
 exitrows.append(row)
for n in range(728,800):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));g=by['p0292'];time=n/fps;gx=at(g,'x',time);sx=at(g,'scaleX',time);expected=[gx+36*sx,gx+964*sx];row=a[600].max(1);runs=[]
 for x in np.where(row<80)[0]:
  if runs and x==runs[-1][-1]+1:runs[-1].append(int(x))
  else:runs.append([int(x)])
 left=[r for r in runs if 5<len(r)<30 and abs(r[-1]+1-expected[0])<25];right=[r for r in runs if 5<len(r)<30 and abs(r[0]-expected[1])<25]
 if not left or not right:continue
 lo=min(left,key=lambda r:abs(r[-1]+1-expected[0]))[-1]+1;hi=min(right,key=lambda r:abs(r[0]-expected[1]))[0];scale=(hi-lo)/928;hardware.append(dict(frame=n,time=time,x=lo-36*scale,scaleX=scale,source_inner_edges=[lo,hi]))
# Source/candidate750caption is uncensored before the map reaches its line.
g=by['p0298'];node=next(l for l in g['children']if l['id']=='p0297');t=750/fps;gx,gy,sx,sy=[at(g,k,t)for k in['x','y','scaleX','scaleY']]
def ink(path):
 a=np.array(Image.open(path).convert('RGB'));c=a[310:370,650:850];m=c.max(2)<100;yy,xx=np.where(m);return [int(xx.min()+650),int(yy.min()+310),int(xx.max()+651),int(yy.max()+311)]
a=ink(p/'measurements-v8/decoded/000750.png');b=ink(root/'outputs/retained-frames/measured-frames-jRBOzF/000750.png');rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);nx=gx+node['x']*sx;ny=gy+node['y']*sy;fit=dict(source_ink=a,candidate_ink=b,x=(a[0]-(b[0]-nx)*rx-gx)/sx,y=(a[1]-(b[1]-ny)*ry-gy)/sy,scaleX=rx,scaleY=ry)
(p/'measurements-v8/exit-hardware-v11.json').write_text(json.dumps(dict(method='Restaurant exit uses isolated actual gray86pxgrabbar, not an eased offscreen endpoint. Compact hardware uses independent inner rails at source row600, excluding map/text by bounded original camera. Uncensored750Poke caption ink controls separate UI font fit.',restaurant_exit=exitrows,hardware=hardware,caption_fit=fit),indent=2));print(json.dumps(dict(exit=exitrows,hardware_samples=hardware[::15],caption=fit),indent=2))
