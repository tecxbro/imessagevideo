from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json,sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'clean'))
from render import Film,interpolate
scene=json.loads((root/'clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=root/'clean-frames'

def fit(f):
    local=deepcopy(scene)
    def bounds(k):
        return interpolate(scene['tracks'][k],f)
    raw=[*bounds('assistantLighting'),*bounds('assistantWashResponse')]
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    prior=np.asarray(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    def replace(key,controls):
        local['tracks'][key]=[[f,*controls]]
    def score(x):
        replace('assistantLighting',x[:16])
        replace('assistantWashResponse',x[16:])
        img=np.asarray(Film(local).frame(f),dtype=np.int16)
        error=np.abs(img-ref)
        return float(error.mean())
    initial=float(np.abs(prior-ref).mean())
    best=initial
    values=raw[:]
    moves=[(0,(-.045,-.02,0,.02,.045)),(1,(-.08,-.04,0,.02,.04)),
           (3,(-.07,-.04,0,.02,.04)),(10,(-.10,-.055,0,.055,.085)),
           (11,(-.10,-.05,0,.055,.085)),(12,(-.36,-.2,0,.20,.35)),
           (5,(-9,-4,0,4,8)),(6,(-60,-35,-18,0,10,22)),(7,(-12,-6,0,6,12)),
           (13,(-6,-2,0,4,8)),(14,(-40,-20,-9,0,10,25)),(15,(-5,0,5,12)),
           (16,(-.9,-.53,-.30,0,.24,.55)),(17,(-.75,-.43,-.18,0,.27,.47))]
    for round_i in range(2):
        for k,options in moves:
            for delta in options:
                q=values[:]
                q[k]=raw[k]+delta
                if (k in (5,6,7,13,14,15,16,17)) and q[k]<0:
                    continue
                e=score(q)
                if e<best:
                    best=e
                    values=q
    return f,initial,best,[round(q,5) for q in values]
out=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for row in ex.map(fit,range(155,162)):
  print(row,flush=True)
  out.append(row)
(root/'veil-fit.json').write_text(json.dumps(out,indent=2)+'\n')
