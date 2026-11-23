from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def study(f):
    key=str(f)
    e=Film(scene)
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    prev=np.asarray(e.frame(f),dtype=np.int16)
    px,py,diameter=e.track('assistantPinPose',f)
    bx,by,w=e.track('assistantMeasuredPosition',f)
    bx+=px*w/900
    cy=by+py
    radius=diameter*.53
    rect=np.s_[max(0,round(cy-radius)):min(1000,round(cy+radius)),
                  max(0,round(bx-radius)):min(1000,round(bx+radius))]
    prior=np.abs(prev-ref)
    initial=float(prior.mean()),float(prior[rect].mean())
    update=copy(scene)
    update['assistantScreenRegistration']=copy(scene['assistantScreenRegistration'])
    entry=deepcopy(scene['assistantScreenRegistration'].get(key,{}))
    update['assistantScreenRegistration'][key]=entry
    def score(params):
        entry['badgePose']=params
        a=np.abs(np.asarray(Film(update).frame(f),dtype=np.int16)-ref)
        return float(a.mean()),float(a[rect].mean())
    args=[px,py,diameter,0.0]
    best=initial
    for scale in (1,.5):
        for i,amp in enumerate((2.6,2.4,3.5,.26)):
            start=args[i]
            for direction in (-2,-1,1,2):
                values=args[:]
                values[i]=start+direction*amp*scale
                if i==3:
                    values[i]=min(1,max(0,values[i]))
                result=score(values)
                if all(a<b for a,b in zip(result,best)):
                    args,best=values,result
    print(f,initial,best,[round(x,4) for x in args],flush=True)
    if best[0]<initial[0]-.009:
        return key,[round(k,5) for k in args]

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        report=dict(z for z in pool.map(study,range(138,157)) if z)
    (p/'assistant-badge-fit.json').write_text(json.dumps(report,indent=2)+'\n')
