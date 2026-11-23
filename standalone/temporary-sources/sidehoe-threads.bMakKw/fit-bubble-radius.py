from pathlib import Path
from PIL import Image
import json,numpy as np
p=Path(__file__).parent;source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
s=json.loads((p/'project/scene.json').read_text())
out={}
for mode,arr in s['threadRegistration'].items():
 rows={}
 for f,shape in arr.items():
  im=np.asarray(Image.open(source/f'{int(f):06}.png').convert('RGB')).astype('int16')
  rad=[]
  for i,(box,_) in enumerate(shape['items']):
   a,b,c,d=box
   height=d-b
   ys=np.array([*range(b+2,b+int(height*.37),2),*range(d-int(height*.37),d-2,2)])
   x0=max(a+5,c-int(height*.65))
   z=im[ys,x0:c+5]
   mask=(z[:,:,0]<246)&(z[:,:,0]>=219)&(np.ptp(z,axis=2)<14)
   use=mask.sum(axis=1)>7
   if not use.any():
    rad.append(round(height*(.4 if i==0 else .27),3));continue
   edge=x0+mask.shape[1]-1-np.argmax(mask[:,::-1],axis=1)
   dist=np.minimum(ys-b,d-1-ys)
   radii=np.linspace(height*.16,height*.50,65)
   sweep=np.clip(radii[:,None]-dist[None,:],0,None)
   calc=c-1.0-radii[:,None]+np.sqrt(radii[:,None]**2-sweep**2)
   res=np.median(np.abs(calc[:,use]-edge[None,use]),axis=1)
   radius=float(radii[np.argmin(res)])
   rad.append(round(radius,2))
  rows[f]=rad
  if f in ('342','348','351','672','674','679','688','693'):print(mode,f,rad)
 out[mode]=rows
(p/'bubble-radius.json').write_text(json.dumps(out,indent=2))
