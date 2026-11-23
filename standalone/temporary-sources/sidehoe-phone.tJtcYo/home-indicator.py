from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter1d
import numpy as np,sys,json
p=Path(__file__).parent;sys.path.insert(0,str(p/'project'))
from render import interpolate
sources=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),
  Path('/tmp/sidehoe-portraits.if793d/full-frames'),p/'probe-v1']
j=json.loads((p/'project'/'scene.json').read_text())['tracks']
for f in range(313,331):
 x,y,s=interpolate(j['sofiaMeasuredCamera'],f)
 m=round((x+200*s))
 b=y+s*827
 row=[]
 for r in sources:
  a=r/f'{f:06}.png'
  if not a.is_file():continue
  q=np.array(Image.open(a).convert('L'),float)
  mid=np.median(q[:,m-44:m+46],axis=1)
  side=np.concatenate([q[:,m-112:m-95],q[:,m+95:m+114]],axis=1).mean(axis=1)
  sub=gaussian_filter1d(side-mid,1.5)
  t0=max(0,round(b-80));t1=min(1000,round(b+54))
  by=t0+sub[t0:t1].argmax()
  strong=np.flatnonzero(sub[t0:t1]>(sub[by]*.45))+t0
  # Keep the center width along the isolated home-indicator row.
  v=np.median(q[by-1:by+2,m-125:m+125],axis=0)
  xtrace=np.flatnonzero(v<(v.min()+np.mean(v[:20]))*.50)+m-125
  xpose=(int(xtrace[0]),int(xtrace[-1])) if len(xtrace) else None
  row.append((r.name,by,round(sub[by],1),[int(strong[0]),int(strong[-1])] if len(strong) else [],xpose))
 print(f,row)
