from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.optimize import differential_evolution
import numpy as np,sys,json
p=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
cfg=p/'project/scene.json';j=json.loads(cfg.read_text())
states=j['clusterDiskContours']
palette=np.array(j['clusterDiskColors'])
X,Y=np.meshgrid(np.arange(1.5,1000,4),np.arange(1.5,1000,4))
ys,xs=np.floor(Y).astype(int),np.floor(X).astype(int)
data={}
for f in [218,219,221,224,226,228,234,241,248,253]:
 a=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),float)
 b=a[ys,xs]
 disk=np.zeros(X.shape)
 bounds=[]
 for cx,cy,w,h,op,_ in states[str(f)]:
    fx,fy=X-cx,Y-cy
    disk=np.maximum(disk,np.hypot(fx/(w*.5+3),fy/(h*.5+3))<=1)
    bounds.append((fx,fy,w/2,h/2))
 r,g,z=np.moveaxis(b,2,0)
 band=(disk<.5)&(r>216)&(r<247)&(g>205)&(g<244)&(z>235)&(z<255)&(z-g>10)&(r>g+1)
 if np.sum(band)<55: raise RuntimeError(f'No halo group at {f}')
 shell=np.median(b[band],axis=0)
 color=(253-shell)
 raw=np.clip(np.sum((253-b)*color,axis=2)/np.dot(color,color),0,1.05)
 # Out-of-gamut samples near moving masks belong to an adjacent disk, not the shell.
 colors=(253-raw[...,None]*color)
 rel=np.max(np.abs(colors-b),axis=2)
 known=(disk<.5)&(rel<13)
 crop=raw[known]
 def loss(v):
   extra,blur,threshold,ramp,ellipse_bias=v
   em=np.maximum.reduce([np.hypot(fx/(w*ellipse_bias+extra),fy/(h*ellipse_bias+extra))<=1
                         for fx,fy,w,h in bounds])
   p=np.clip((gaussian_filter(em.astype(float),blur/4)-threshold)/ramp,0,1)
   return np.abs(p[known]-crop).sum()/max(1,crop.sum())+.035*np.abs(ramp-.58)
 fit=differential_evolution(loss,[(1,26),(5,38),(.06,.47),(.17,1),(.96,1.25)],seed=310+f,popsize=4,maxiter=13,polish=False)
 print(f,np.round(shell,2),np.round(fit.x,3),round(fit.fun,3),flush=True)
 data[f]=[f,*np.round(fit.x,4).tolist(),*np.round(shell,2).tolist()]
j['tracks']['clusterHaloRegistration']=list(data.values())
cfg.write_text(json.dumps(j,indent=2)+'\n')
