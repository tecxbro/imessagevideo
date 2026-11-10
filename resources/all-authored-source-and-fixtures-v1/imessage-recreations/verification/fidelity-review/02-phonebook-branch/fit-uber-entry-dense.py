from pathlib import Path
import numpy as np,json
from scipy.optimize import minimize
from PIL import Image
P=Path('/workspace/imessage-recreations/verification/fidelity-review/02-phonebook-branch');im=Image.open(P/'uber-480.png').crop((35,69,630,179)).resize((298,55),Image.Resampling.LANCZOS)
found=[]
for f in [477,478,479]:
 target=np.array(Image.open(P/f'uber-{f}.png').resize((340,115),Image.Resampling.LANCZOS)).astype(float)
 def warp(p):
  a,b,e,tx,ty=p;inv=[1/a,-b/a/e,149-tx/a+b*ty/a/e,0,1/e,27.5-ty/e]
  return im.transform((340,115),Image.Transform.AFFINE,inv,Image.Resampling.BILINEAR,fillcolor=(253,253,253))
 def loss(p):
  aa=np.array(warp(p)).astype(float);return np.abs(np.clip(253-aa,0,253)-np.clip(253-target,0,253))[25:90,10:325].mean()
 p0=([.9985,-.1623,.83105,164.988,59.3853] if f==477 else [1,0,1.09 if f==478 else 1.0566,166,62])
 r=minimize(loss,p0,method='Powell',bounds=[(.95,1.05),(-.4,.4),(.7,1.25),(160,172),(52,68)],options={'maxiter':20,'xtol':.0002,'ftol':.0001});a,b,e,tx,ty=r.x
 # Half-resolution source has298 vs297.5 ideal width. Correct source x-axis.
 a*=298/297.5
 params=[a,b,e,tx*2,ty*2];found.append(dict(frame=f,params=params,half_fit_loss=r.fun));print(f,params,r.fun,flush=True)
(P/'uber-entry-affines.json').write_text(json.dumps(found,indent=2))
