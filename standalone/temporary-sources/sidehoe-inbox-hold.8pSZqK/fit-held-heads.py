from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
from copy import copy
from render import Film
import json
import sys
import numpy as np

p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def solve(index):
    base=Film(s)
    frames=(16,26,34,40)
    samples=[]
    for f in frames:
        x0=[169,411,651][index]
        offset=s['inboxHeldRegistration'][str(f)]['pins'][index]
        y=base.track('inboxY',f)[0]
        k=base.track('inboxScale',f)[0]
        cx=500-410*k+(x0+offset[0])*k
        cy=y+(473+offset[1])*k
        rect=(int(cx-70),int(cy-69),int(cx+70),int(cy+71))
        exact=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB').crop(rect),dtype=np.float32)
        samples.append((f,rect,exact))
    candidates=copy(s)
    candidates['inboxHeldRegistration']=copy(s['inboxHeldRegistration'])
    config={}
    for f, _, _ in samples:
        entry=copy(s['inboxHeldRegistration'][str(f)])
        entry['pinHeadPoses']=[[],[],[]]
        config[f]=entry
    def cost(pose):
        current=[]
        for f,rect,exact in samples:
            ref=config[f]
            ref['pinHeadPoses'][index]=pose
            candidates['inboxHeldRegistration'][str(f)]=ref
            actual=np.asarray(Film(candidates).frame(f).crop(rect),dtype=np.float32)
            current.append(float(np.abs(exact-actual).mean()))
        return sum(current)/len(current)
    pose=[1,1,0,0,0]
    initial=best=cost(pose)
    for mul in (1,.5,.25):
        for i,step in enumerate((.055,.056,4.5,5,2.7)):
            start=pose[i]
            for k in (-2,-1,1,2):
                trial=pose[:]
                trial[i]=start+k*step*mul
                score=cost(trial)
                if score<best:
                    best,pose=score,trial
    print(index,round(initial,4),round(best,4),pose,flush=True)
    return pose

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=3) as pool:
        v=list(pool.map(solve,range(3)))
    (p/'pin-head-fit.json').write_text(json.dumps(v,indent=2)+'\n')
