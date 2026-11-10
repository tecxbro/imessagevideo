"""Original/native-caption ink fit, excluding the independently bouncing badge."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v12/scene.json').read_text());text=next(n for n in s['layers']if n['id']=='p0015');badge=next(n for n in s['layers']if n['id']=='p0016');bb={r['frame']:r['observed']['bbox']for r in json.loads((p/'measurements-v8/verified-badge-v13.json').read_text())['measurements']if r['observed']};rows=[]
def ink(file,remove):
 a=np.array(Image.open(file).convert('RGB'));mask=(a.max(2)<195)&(a.min(2)>65)&(a.max(2)-a.min(2)<14);mask[:450]=False;mask[850:]=False;mask[:,:500]=False;mask[:,930:]=False
 if remove:
  x,y,z,w=remove;mask[max(0,int(y)-3):min(1080,int(w)+4),max(0,int(x)-3):min(1440,int(z)+4)]=False
 labels,_=ndimage.label(mask);keep=np.zeros_like(mask)
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl
  if yy.stop-yy.start>12 and xx.stop-xx.start>7:keep|=labels==i
 yy,xx=np.where(keep)
 return[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
for n in range(64,109):
 t=n/s['fps'];cx,cy,csx,csy=[at(badge,k,t)for k in['x','y','scaleX','scaleY']];cb=[cx,cy,cx+57*csx,cy+58*csy]if n>=75 else None;a=ink(p/f'measurements-v8/decoded/{n:06}.png',bb.get(n));b=ink(root/f'outputs/retained-frames/measured-frames-jRBOzF/{n:06}.png',cb);x,y=[at(text,k,t)for k in['x','y']];rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1])
 if not(.85<rx<1.15 and .85<ry<1.15):raise ValueError((n,a,b,rx,ry))
 rows.append(dict(frame=n,time=t,source=a,candidate=b,x=a[0]-(b[0]-x)*rx,y=a[1]-(b[1]-y)*ry,scaleX=rx,scaleY=ry))
(p/'measurements-v8/poke-caption-ink-v13.json').write_text(json.dumps(dict(method='Source gray original caption ink versus actual nativeV12PNG, separate source/candidate badge boxes excluded. Native affine ink fit retains current optical font/copy. Source64–108 only.',measurements=rows),indent=2));print([(r['frame'],r['source'],r['candidate'])for r in rows if r['frame']in[64,71,72,74,80,98,108]])
