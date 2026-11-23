from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import Film

root=Path(sys.argv[1])
s=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit(f):
    frame=str(f)
    candidate=copy(s)
    candidate['threadRegistration']=copy(s['threadRegistration'])
    candidate['threadRegistration']['follow']=copy(s['threadRegistration']['follow'])
    state=deepcopy(s['threadRegistration']['follow'][frame])
    candidate['threadRegistration']['follow'][frame]=state
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    baseline=np.asarray(Film(candidate).frame(f),dtype=np.int16)
    opening=float(np.abs(baseline-target).mean())
    best=opening
    # Header name and badge move vertically and separate during the withdrawal.
    if f==694:
        state['headerInk']=[479,-4,39,18,510]
        state['header'][2]=-31
        state['focus']=[6,9,2.75]
    else:
        state['headerInk']=[485,83,40,12,510]
        state['headerBadgeTrail']=[16,0]
    def score():
        diff=np.asarray(Film(candidate).frame(f),dtype=np.int16)-target
        return float(np.abs(diff).mean())
    best=score()
    print(f,'first',opening,best,flush=True)
    for scale,fields in (
        (1,[('focus',(1.1,2.6,.6)),('header',(3.5,1.4,2.1,2.4,3.2,.42)),
            ('headerInk',(1.6,1.8,3.4,2.2,28)),('headerBadgeTrail',(2.9,1.7))]),
        (1,[('railBlend',(6,8)),('blue',(1.5,2.5,2.0,2)),
            ('corners',(2.1,2.4))]),
        (.52,[('focus',(.95,2.6,.53)),('header',(3.5,1.4,2.1,2.4,3.2,.42)),
               ('headerInk',(1.6,1.8,3.4,2.2,28)),('headerBadgeTrail',(2.9,1.7)),
               ('railBlend',(6,8))]),
    ):
        for key,steps in fields:
            if key not in state: continue
            values=state[key]
            for i,step in enumerate(steps):
                initial=values[i]
                chosen=initial
                for n in (-2,-1,1,2):
                    values[i]=initial+n*step*scale
                    if key=='focus' and i==2 and values[i]<.35 or key=='headerBadgeTrail' and i==0 and values[i]<0:
                        continue
                    err=score()
                    if err<best:
                        best,chosen=err,values[i]
                values[i]=round(chosen,4)
        print(f,scale,best,flush=True)
    # Center the shapes and text independently from the remaining square screen edges.
    for pose,steps in zip(state['controls'],[(1.9,1.65,2.5,1.9)]*2):
        for i,step in enumerate(steps):
            initial=pose[i]
            chosen=initial
            for n in (-2,-1,1,2):
                value=initial+n*step
                pose[i]=round(value) if i>=2 else value
                err=score()
                if err<best:
                    best,chosen=err,pose[i]
            pose[i]=round(chosen) if i>=2 else round(chosen,3)
    for key,step in [('controlFocus',.5),('controlLight',.15)]:
        v=state[key]
        chosen=v
        for n in (-2,-1,1,2):
            state[key]=max(0,v+n*step)
            err=score()
            if err<best:
                best,chosen=err,state[key]
        state[key]=round(chosen,3)
    print(f,'result',opening,best,{k:state[k] for k in ('header','controls','focus','controlFocus','controlLight')},flush=True)
    return frame,state if best<opening-.10 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=2) as pool:
        data=dict(pool.map(fit,(694,695)))
    (root/'release-fit.json').write_text(json.dumps({k:v for k,v in data.items() if v},indent=2)+'\n')
