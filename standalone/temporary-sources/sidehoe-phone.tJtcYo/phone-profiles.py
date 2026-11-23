from pathlib import Path
from PIL import Image
import numpy as np,sys,json
from scipy.ndimage import gaussian_filter1d
p=Path(__file__).parent;sys.path.insert(0,str(p/'project'))
from render import interpolate
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-portraits.if793d/full-frames')
j=json.loads((p/'project/scene.json').read_text())['tracks']
for f in range(313,337):
 x,y,s=interpolate(j['sofiaMeasuredCamera'],f)
 bottom=y+827*s
 print('\n',f, 'input',np.round([x,y,s,bottom],2),end=' ')
 for path in [source,prior]:
  q=np.array(Image.open(path/f'{f:06}.png').convert('RGB'),dtype=np.int16)
  start=max(70,round(y+100*s))
  end=min(428, round(bottom-115*s))
  xx=np.median(q[start:end],axis=(0,2))
  left=max(0,round(x-18));right=min(1000,round(x+400*s+19))
  boundaries=[]
  for low,high in ((left,min(round(x+65),500)),(max(500,round(x+400*s-65)),right)):
   seq=np.flatnonzero(xx[low:high]<150)+low
   if len(seq):
    lo,hi=seq[0],seq[-1]
    mid=np.argmax(np.array([xx[z] for z in seq[2:7]])) if len(seq)>7 else 0
    points=np.interp(np.linspace(lo,hi,8),np.arange(len(xx)),xx).astype(int)
    boundaries.append((int(lo),int(hi),points.tolist()))
  y0,y1=round(bottom-60),min(1000,round(bottom+98))
  ycurve=np.median(q[y0:y1,494:548],axis=(1,2))
  depth=min(ycurve)
  plausible=np.flatnonzero(ycurve<(depth+253)*.54)
  blue=f>=314
  print(path.name,boundaries,'floor',list((plausible+y0)[[0,-1]]) if len(plausible) else [],round(depth),end=' ')
