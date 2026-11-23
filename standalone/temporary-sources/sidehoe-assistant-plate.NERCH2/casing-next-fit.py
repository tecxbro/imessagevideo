from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import deepcopy,copy
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'casing-next/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def solve(f):
    key=str(f)
    entry=scene['threadRegistration']['sofia'][key]
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    before=np.asarray(Image.open(p/'clean-frames'/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    starting=entry['casing']
    original=float(np.abs(target-before).mean())
    data=copy(scene)
    data['threadRegistration']=copy(scene['threadRegistration'])
    data['threadRegistration']['sofia']=copy(scene['threadRegistration']['sofia'])
    place=deepcopy(entry)
    data['threadRegistration']['sofia'][key]=place
    view=np.s_[max(0,round(starting[1])-15):1000,max(0,round(starting[0])-23):
                min(1000,round(starting[0]+400*starting[2])+23)]
    initial=(original,float(np.abs(target-before)[view].mean()))
    settled=[*starting,1.0]
    def score(pose):
        place['casing']=pose[:6]
        place['casingAspect']=pose[6]
        v=np.asarray(Film(data).frame(f),dtype=np.int16)
        signal=np.abs(v-target)
        return (float(signal.mean()),float(signal[view].mean()))
    best=initial
    for mult in (1,.5):
        for i,delta in enumerate((1.4,1.8,.004,1.9,2.7,.72,.009)):
            value=settled[i]
            for direction in (-2,-1,1,2):
                option=settled[:]
                option[i]=value+direction*mult*delta
                if i in (4,5):
                    option[i]=max(0,option[i])
                result=score(option)
                if all(a<b for a,b in zip(result,best)):
                    settled,best=option,result
    print(f,initial,best,settled,flush=True)
    if best[0]<original-.007:
        return key,dict(casing=[round(k,6) for k in settled[:6]],aspect=round(settled[6],6))

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        records=dict(x for x in pool.map(solve,range(319,330)) if x)
    (p/'next-casing-fit.json').write_text(json.dumps(records,indent=2)+'\n')
