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
    k=str(f)
    prior=scene['followSettledRegistration'][k]
    measured=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    base=np.asarray(Image.open(p/'clean-frames'/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    data=copy(scene)
    data['followSettledRegistration']=copy(scene['followSettledRegistration'])
    state=deepcopy(prior)
    data['followSettledRegistration'][k]=state
    values=[state.get('caseRadius',65),state['headerEnd'],state['idY'],state['composerY']]
    keys=('caseRadius','headerEnd','idY','composerY')
    previous=float(np.abs(measured-base).mean())
    best=previous
    for scale in (1,.5):
        for i,magnitude in enumerate((3,2,1.55,1.5)):
            origin=values[i]
            for n in (-2,-1,1,2):
                candidate=values[:]
                candidate[i]=origin+n*magnitude*scale
                state.update(zip(keys,candidate))
                v=np.asarray(Film(data).frame(f),dtype=np.int16)
                err=float(np.abs(measured-v).mean())
                if err<best:
                    best,values=err,candidate
    print(f,previous,best,values,flush=True)
    if best<previous-.008:
        return k,{i:round(v,6) for i,v in zip(keys,values)}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        output=dict(z for z in pool.map(solve,range(650,660)) if z)
    (p/'next-follow-case-fit.json').write_text(json.dumps(output,indent=2)+'\n')
