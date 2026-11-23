from pathlib import Path
from PIL import Image
from copy import deepcopy
import json
from concurrent.futures import ThreadPoolExecutor
import sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'tile-push-clean'))
from render import Film,interpolate
scene=json.loads((root/'tile-push-clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=root/'tile-push-full'

def probe(f):
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    prior=np.asarray(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    original=interpolate(scene['tracks']['sofiaPlateRegistration'],f)
    g=deepcopy(scene)
    track=g['tracks']['sofiaPlateRegistration']
    def replace(delta_y,xdelta,y_delta,sweep_ratio,sdelta):
        values=[f,original[0]+y_delta,original[1],original[2]*sweep_ratio,original[3]*sweep_ratio]
        for i,row in enumerate(track):
            if row[0]==f:
                track[i]=values
                break
            if row[0]>f:
                track.insert(i,values)
                break
        camera=g['tracks']['sofiaMeasuredCamera']
        x,y,scale=interpolate(scene['tracks']['sofiaMeasuredCamera'],f)
        terms=[f,x+xdelta,y+delta_y,scale+sdelta]
        for i,row in enumerate(camera):
            if row[0]==f:
                camera[i]=terms
                break
            if row[0]>f:
                camera.insert(i,terms)
                break
    achieved=(float(np.abs(ref-prior).mean()),(0,0,0,1,0))
    base_rate=achieved[0]
    for which,samples in [(3,(0,.22,.48,.67,.85)),(0,(-12,-6,-3,0,4,8,12)),(2,(-7,-4,-2,0,2,4,7)),(4,(-.0075,0,.0075,.014))]:
        for step in samples:
            values=list(achieved[1])
            values[which]=step
            replace(*values)
            shot=np.asarray(Film(g).frame(f),dtype=np.int16)
            score=float(np.abs(ref-shot).mean())
            if score<achieved[0]:
                achieved=(score,tuple(values))
    return f,base_rate,achieved
with ThreadPoolExecutor(max_workers=5) as pool:
    fit=[]
    for result in pool.map(probe,range(331,337)):
        print(result,flush=True)
        fit.append(result)
(root/'sofia-focus-fit.json').write_text(json.dumps(fit,indent=2)+'\n')
