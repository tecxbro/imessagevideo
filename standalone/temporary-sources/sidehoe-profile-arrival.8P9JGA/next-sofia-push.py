from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import deepcopy,copy
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'clean/scene.json').read_text())
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def solve(f):
    key=str(f)
    src=np.asarray(Image.open(ref/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    r=deepcopy(scene['threadRegistration']['sofia'][key])
    left,right=r['rails']
    active=np.s_[:,max(0,left-6):min(1000,right+6)]
    frame=np.asarray(Film(scene).frame(f),dtype=np.int16)
    a=np.abs(src-frame)
    prior=(float(a.mean()),float(a[active].mean()))
    opt=copy(scene)
    opt['threadRegistration']=copy(scene['threadRegistration'])
    opt['threadRegistration']['sofia']=copy(scene['threadRegistration']['sofia'])
    opt['threadRegistration']['sofia'][key]=r
    start=r.get('focus',[0,0,.75])
    value=list(start)
    best=prior
    for spread in (1,.5):
        for i,size in enumerate((2.7,4.1,.49)):
            origin=value[i]
            for sign in (-2,-1,1,2):
                work=value[:]
                work[i]=origin+sign*size*spread
                if i>0:
                    work[i]=max(0,work[i])
                r['focus']=work
                b=np.abs(src-np.asarray(Film(opt).frame(f),dtype=np.int16))
                after=(float(b.mean()),float(b[active].mean()))
                if all(b<a for a,b in zip(best,after)):
                    best,value=after,work
    print(f,prior,best,value,flush=True)
    return (key,value) if best[0]<prior[0] else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        data=dict(z for z in pool.map(solve,range(337,343)) if z)
    (p/'next-sofia-push.json').write_text(json.dumps(data,indent=2)+'\n')
