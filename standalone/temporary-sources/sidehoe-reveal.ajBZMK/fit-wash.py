from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter, minimum_filter
from scipy.optimize import minimize
d=Path(__file__).parent
s=json.loads((d/'project/scene.json').read_text())['tracks']
pos={f:(x,y,w) for f,x,y,w in s['assistantMeasuredPosition']}
pin=np.array(s['assistantPinPose'])
Y,X=np.mgrid[0:1000:3,0:1000:3]; xx=X/999;yy=Y/999
out=[]
for f,*control in s['assistantLighting']:
 a=np.asarray(Image.open(d/'source'/f'{f-133:03}.png'),dtype=float)[::3,::3]
 b=np.asarray(Image.open(d/'probe'/f'{f:06}.png'),dtype=float)[::3,::3]
 tint=np.zeros((*X.shape,3)); parts=[]
 for cx,cy,sx,sy,shear,r,g,v in [control[:8],control[8:]]:
  z=np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
  parts.append(z*g/175)
  tint+=z[:,:,None]*[r,g,v]
 alpha=np.clip(sum(parts),0,.94)
 source=np.clip((b+tint-253*alpha[:,:,None])/np.maximum(1-alpha[:,:,None],.04),0,255)
 x,y,w=pos[f]
 py=np.interp(f,pin[:,0],pin[:,2])
 px=np.interp(f,pin[:,0],pin[:,1])*w/900+x
 r=np.interp(f,pin[:,0],pin[:,3])*.492
 ring=((X-px)**2+(Y-y-py)**2<(.80*r)**2)&((X-px)**2+(Y-y-py)**2>(.65*r)**2)
 roi=(Y>y+30)&(X>x+30)&(X<x+w-30)
 texture=(maximum_filter(b.mean(axis=-1),size=3)-minimum_filter(b.mean(axis=-1),size=3))<18
 good=roi&texture&((np.mean(source,axis=2)<167)|ring)
 good &= (np.abs(b[:,:,0]-a[:,:,0])<72)
 if np.count_nonzero(good)<40: continue
 parts2=[part[good] for part in parts]; source2=source[good]; tint2=tint[good]; a2=a[good]
 def loss(p):
  mix=np.clip(p[0]*parts2[0]+p[1]*parts2[1],0,.94)[:,None]
  trial=source2*(1-mix)+253*mix-tint2
  delta=trial-a2
  return float(np.log1p(np.abs(delta)/4).mean())+.016*((p[0]-1)**2+(p[1]-1)**2)
 sol=minimize(loss,[1,1],method='Powell',bounds=[(.6,2.8),(.6,2.8)])
 print(f,len(a2),np.round(sol.x,3),round(loss([1,1]),3),round(sol.fun,3))
 out.append([f,*[round(float(x),3) for x in sol.x]])
(d/'wash-fit.json').write_text(json.dumps(out,indent=2))
