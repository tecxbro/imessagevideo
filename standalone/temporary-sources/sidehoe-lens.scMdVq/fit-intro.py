from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import numpy as np,json,sys
p=Path(__file__).parent
sys.path.insert(0,str(p/'clean'))
from render import Film,interpolate
scene=json.loads((p/'clean/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=p/'clean-frames'

def fit(f):
    local=deepcopy(scene)
    ref=np.asarray(Image.open(src/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    prior=np.asarray(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    keys=('inboxIntroHeader','inboxY','inboxScale',*(f'inboxIntroPin{i}' for i in range(3)))
    initial=[interpolate(scene['tracks'][key],f) for key in keys]
    chosen=deepcopy(initial)
    score=lambda x:float(np.abs(ref-np.asarray(x,dtype=np.int16)).mean())
    start=best=score(prior)
    steps=[((-.19,-.11,-.05,0),(-2,-.8,0,.9,1.8),(-7,-3,0,3,7)),((-15,-8,-4,0,3,6,12),),((-.039,-.024,-.012,0,.012,.024,.039),)]
    pin=((-8,-4,0,4,8),(-9,-4,0,4,9),(-10,-5,0,5,10),(-.2,-.11,0,.07,.12))
    for i,opts in enumerate([*steps,pin,pin,pin]):
      if f<scene['tracks'][keys[i]][0][0] and i>=3:
       continue
      for j,move in enumerate(opts):
       for delta in move:
        q=deepcopy(chosen)
        val=initial[i][j]+delta
        if (i in (0,) and j==0) or (i>=3 and j==3):
         val=min(1,max(0,val))
        if i==0 and j==1:
         val=max(0,val)
        q[i][j]=round(val,5)
        for key,row in zip(keys,q,strict=True):
         if f>=scene['tracks'][key][0][0] or key in ('inboxIntroHeader','inboxY','inboxScale'):
          local['tracks'][key]=[[f,*row]]
        v=score(Film(local).frame(f))
        if v<best:
         best,chosen=v,q
    return f,start,best,dict(zip(keys,chosen,strict=True))
measure=[]
with ThreadPoolExecutor(max_workers=4) as e:
 for row in e.map(fit,range(1,10)):
  print(row[0],*[round(v,5) for v in row[1:3]],flush=True)
  measure.append(row)
(p/'intro-future-fit.json').write_text(json.dumps(measure,indent=2)+'\n')
