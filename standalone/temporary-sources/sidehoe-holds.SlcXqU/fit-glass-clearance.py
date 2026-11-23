"""Find the inner feather that preserves central glass through the handset hold."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from render import Film

p=Path(sys.argv[1])
root=p/'casing-next'
s=json.loads((root/'scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit(f):
    key=str(f)
    top=s['assistantExitCasing'][key][0][1]
    y=round(top)
    box=(200,y+23,797,y+70)
    target=np.asarray(Image.open(src/f'{f:06d}.png').convert('RGB').crop(box),np.int16)
    controls={}
    scene={**s,"assistantCasingGlass":controls}
    film=Film(scene)
    def measure():
        return float(np.abs(target-np.asarray(film.frame(f).crop(box),np.int16)).mean())
    old=best=measure()
    candidate=None
    for softness in (.13,.25):
        for cutoff in (1.26,1.32,1.42,1.51,1.59,1.64,1.71):
            for half_width in (.42,.58,.71):
                values=[cutoff,half_width,softness]
                controls[key]=values
                score=measure()
                if score<best:
                    best,candidate=score,values
    print(f,round(old,5),round(best,5),candidate,flush=True)
    return key,candidate if old-best>.03 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        data={key:value for key,value in pool.map(fit,range(139,162)) if value}
    s['assistantCasingGlass']=data
    (root/'scene.json').write_text(json.dumps(s,indent=2)+'\n')
    (p/'clear-glass-fit.json').write_text(json.dumps(data,indent=2)+'\n')
