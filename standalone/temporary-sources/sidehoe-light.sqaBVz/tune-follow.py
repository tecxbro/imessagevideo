from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json,sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film,interpolate
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
stage=root/'probe-b'

def fit(f):
    local=deepcopy(scene)
    p=local['followEntryOptics'][str(f)]
    origin=p[:]
    reg=local['followSettledRegistration'].get(str(f))
    cam=next(r for r in local['tracks']['followMeasuredCamera'] if r[0]==f)
    y0=cam[2]
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    before=np.asarray(Image.open(stage/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    b=float(np.abs(ref-before).mean())
    threshold=b; start=[*p,y0,reg['coverage'] if reg else 0]
    best=start[:]
    def rate(values):
        p[:]=values[:5]
        cam[2]=values[5]
        if reg:
            reg['coverage']=values[6]
        return float(np.abs(np.asarray(Film(local).frame(f),dtype=np.int16)-ref).mean())
    moves=[(-.007,-.003,0,.003,.007),(-7,-3,0,3,6,11),(-.5,-.24,0,.24,.5),
           (-12,-6,0,6,13,21),(-.75,-.34,0,.32,.62),(-4,-2,0,2,4),(-.56,-.31,-.14,0)]
    for k in (5,0,1,2,3,4,6,3,5):
        if k==6 and not reg:
            continue
        for d in moves[k]:
            change=best[:]
            change[k]=start[k]+d
            if k in (1,2,3,4) and change[k]<0:
                continue
            error=rate(change)
            if error<threshold:
                threshold=error
                best=change
    return f,b,threshold,[round(k,6) for k in best]
fits=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for row in ex.map(fit,range(624,631)):
  print(row,flush=True);fits.append(row)
(root/'follow-optics-fit.json').write_text(json.dumps(fits,indent=2)+'\n')
