from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import sys,json,numpy as np
p=Path(__file__).parent;sys.path.insert(0,str(p/'clean'))
from render import Film,interpolate
s=json.loads((p/'clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=p/'clean-frames'

def fit(f):
 cfg=deepcopy(s)
 ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 old=np.asarray(Image.open(prior/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 keys=['sofiaMeasuredCamera','sofiaKeyboardY','sofiaPlateRegistration']
 v=[interpolate(s['tracks'][name],f) for name in keys]
 opt=deepcopy(s.get('sofiaEarlyOptics',{}).get(str(f),[]))
 orig=[*v[0],v[1][0],*v[2],*opt]
 best=orig[:]
 def rate(x):
    rows=[x[:3],x[3:4],x[4:8]]
    for name,segment in zip(keys,rows,strict=True):
     cfg['tracks'][name]=[[f,*segment]]
    if opt:cfg['sofiaEarlyOptics'][str(f)]=x[8:]
    return float(np.abs(np.asarray(Film(cfg).frame(f),dtype=np.int16)-ref).mean())
 base=score=float(np.abs(old-ref).mean())
 moves={0:(-3,-1.5,0,1.5,3),1:(-12,-7,-3,0,3,7,12),
 2:(-.014,-.007,0,.007,.014),3:(-12,-6,0,6,12),
 4:(-10,-5,0,5,10),5:(-7,-3,0,3,7),
 8:(-4,-2,0,2,4),9:(-7,-3,0,3,7),10:(-.02,-.012,0,.012,.02),
 11:(-.029,-.014,0,.014,.029),12:(-2,-1,0,1,2),13:(-6,-3,0,3,6)}
 dims=[1,2,0,3,4,5] if not opt else [9,11,10,8,3,4,12,13,5]
 for k in dims:
  for step in moves[k]:
   test=best[:];test[k]=orig[k]+step
   if k in (12,13) and test[k]<.05:continue
   r=rate(test)
   if r<score:score=r;best=test
 return [f,base,score,best]
out=[]
with ThreadPoolExecutor(max_workers=4) as e:
 for row in e.map(fit,range(314,329)):
  print(row[0],round(row[1],4),round(row[2],4),flush=True)
  out.append(row)
(p/'sofia-entrance-future.json').write_text(json.dumps(out,indent=2)+'\n')
