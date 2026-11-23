from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import copy,deepcopy
from PIL import Image
import numpy as np
import json,sys
from render import Film
p=Path(sys.argv[1])
s=json.loads((p/'sofia-next/scene.json').read_text())
geometry=json.loads((p/'next-sofia-composer.json').read_text())
keys=json.loads((p/'next-sofia-keys.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def fit(f):
    k=str(f)
    state=copy(s)
    state['threadRegistration']=deepcopy(s['threadRegistration'])
    reg=state['threadRegistration']['sofia'][k]
    target=np.array(Image.open(source/f'{f:06}.png').convert('RGB'),np.int16)
    film=Film(state)
    def score():
        return float(np.abs(target-np.array(film.frame(f),np.int16)).mean())
    before=score()
    best=before
    patch={}
    choices=[]
    for name in ('composer','edgeRamps','keyPoses'):
        if name=='composer' and k in geometry:
            proposed={name:geometry[k][name]}
        elif name=='edgeRamps' and k in geometry:
            proposed={'edgeRamps':geometry[k]['edgeRamps'],'railHardware':geometry[k]['railHardware']}
        elif name=='keyPoses' and any(keys[k]):
            proposed={name:keys[k]}
        else:
            continue
        prev={key:reg.get(key) for key in proposed}
        reg.update(proposed)
        value=score()
        if value<best:
            best=value
            patch.update(proposed)
        else:
            for key,setting in prev.items():
                if setting is not None: reg[key]=setting
                else: reg.pop(key,None)
    best_focus=None
    for focus in (.4,.6,.85,1.10,1.4,1.72,2.08):
        reg['focus']=[0,0,focus]
        value=score()
        if value<best:
            best,best_focus=value,focus
    if best_focus is not None:
        patch['focus']=[0,0,best_focus]
    print(f,round(before,5),round(best,5),list(patch),flush=True)
    return k,patch
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        result=dict(pool.map(fit,range(343,352)))
    (p/'next-sofia-fit.json').write_text(json.dumps(result,indent=2)+'\n')
