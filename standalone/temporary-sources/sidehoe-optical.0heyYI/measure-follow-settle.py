from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter1d
import numpy as np,json
D=Path('/tmp/sidehoe-optical.0heyYI');t=json.loads((D/'tile-project/scene.json').read_text())['tracks']
old=Path((D/'checked-build-path').read_text().strip())/'frames'
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
rows=np.array(t['followMeasuredCamera'])
out={}
for f in range(628,661):
 x,y,s=[np.interp(f,rows[:,0],rows[:,i]) for i in (1,2,3)]
 stages=[]
 for dd in (src,old):
  a=np.asarray(Image.open(dd/f'{f:06}.png').convert('RGB')).astype('int16')
  l=[]
  for cur,hi,lo in [(x,round(x+35*s),round(x-20)),(x+400*s,round(x+400*s+20),round(x+370*s))]:
   left=len(l)==0
   xx=np.median(a[max(0,round(y+s*125)):min(1000,round(y+s*760)),lo:hi,:],axis=(0,2))
   idx=np.flatnonzero(xx<175)
   l.append(lo+(idx[0] if left else idx[-1]+1))
  center=round(x+s*200)
  vertical=np.median(a[:,center-52:center+52,:],axis=(1,2))
  around=lambda y: list(np.flatnonzero(vertical[max(0,round(y-35)):min(1000,round(y+35))]<171)+max(0,round(y-35)))
  pre,post=around(y),around(y+s*827)
  top=int(min(pre)) if pre and pre[0]>0 else None
  bottom=int(max(post)+1) if post and post[-1]<998 else None
  left,right=[int(i) for i in l]
  ymm=round(y+s*530)
  z=np.median(a[:,center-110:center+110,0],axis=1)
  along=np.flatnonzero((z[ymm-45:ymm+46]>185)&(z[ymm-45:ymm+46]<232))+ymm-45
  start=next((int(q[0]) for q in np.split(along,np.flatnonzero(np.diff(along)>1)+1) if len(q)>7),None)
  stages.append((left,right,top,bottom,start,[int(vertical[k]) if 0<=k<1000 else None for k in (round(y),round(y+s*827-1))]))
 out[f]=stages
 print(f,stages)
(D/'follow-body-landmarks.json').write_text(json.dumps(out,indent=2))
