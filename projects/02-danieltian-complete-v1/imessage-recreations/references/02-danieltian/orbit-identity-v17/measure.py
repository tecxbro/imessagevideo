from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[3];REF=Path(__file__).resolve().parent;OUT=ROOT/'outputs/02-danieltian/orbit-identity-v17'
def components(a):
 a=a.astype(float);r,g,b=a.transpose(2,0,1);dr=r-g;db=b-g
 m=(dr>35)&(db>30)&(abs(r-b)<.60*np.maximum(dr,db))
 lab,n=ndimage.label(m,np.ones((3,3)));options=[]
 for i,sl in enumerate(ndimage.find_objects(lab)):
  if sl is None:continue
  y,x=sl;count=int((lab[sl]==i+1).sum());w=x.stop-x.start;h=y.stop-y.start
  if count<20:continue
  options.append(dict(bounds=[x.start,y.start,x.stop,y.stop],pixels=count,fill=count/(w*h),touchStage=[x.start==0,x.stop==a.shape[1],y.start==0,y.stop==a.shape[0]]))
 return sorted(options,key=lambda q:q['pixels'],reverse=True)
rows=[]
for n in range(547,599):
 a=np.array(Image.open(REF/f'source/{n:06}.png').convert('RGB'));b=np.array(Image.open(OUT/f'baseline-native16/{n:06}.png').convert('RGB'))
 rows.append(dict(frame=n,source=components(a),native=components(b)))
(REF/'component-ledger.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['frame'],[(x['bounds'],x['pixels']) for x in r['source'][:2]],[(x['bounds'],x['pixels']) for x in r['native'][:2]])
