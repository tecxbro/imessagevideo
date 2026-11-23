from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from render import Film

p=Path(sys.argv[1])
baseline=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def measure(frame):
    f=str(frame)
    src=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB'),np.int16)
    prior=np.asarray(Image.open(p/'prior-full'/f'{frame:06}.png').convert('RGB'),np.int16)
    state=copy(baseline)
    state['inboxScrollRegistration']=copy(baseline['inboxScrollRegistration'])
    state['inboxScrollRegistration'][f]=reg=deepcopy(baseline['inboxScrollRegistration'][f])
    film=Film(state)
    streak,=film.track('inboxScrollSmear',frame)
    row=[.38,max(.12,streak*.26),0,0]
    chrome=[.38,streak*.23 if streak>2 else 0,0,0]
    reg['rowExposure']=row
    reg['chromeExposure']=chrome
    before=float(np.abs(src-prior).mean())
    def cost():
        a=np.asarray(film.frame(frame),dtype=np.int16)
        return float(np.abs(src-a).mean())
    clo=cost()
    for fields,magnitude in (
        ((row,chrome),1),((row,chrome),.48)
    ):
        for vals in fields:
            steps=(.45,2.0,1.0,2.25) if vals is row else (.42,1.8,1.3,1.25)
            for index, stride in enumerate(steps):
                initial=vals[index]
                selected=initial
                for move in (-2,-1,1,2):
                    value=initial+move*stride*magnitude
                    if (index<=1 and value<0) or (index>=2 and abs(value)>10):
                        continue
                    vals[index]=value
                    err=cost()
                    if err<clo:
                        selected,clo=value,err
                vals[index]=selected
    params={k:[round(x,4) for x in reg[k]] for k in ('rowExposure','chromeExposure')}
    print(frame,before,clo,params,flush=True)
    return f,params if clo<before-.04 else {}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=7) as pool:
        results={k:v for k,v in pool.map(measure,range(42,60)) if v}
    (p/'inbox-exposure-fit.json').write_text(json.dumps(results,indent=2)+'\n')
