from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json,sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'final-clean'))
from render import Film,interpolate
scene=json.loads((root/'final-clean/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
previous=root/'final-frames'

def fit(f):
    local=deepcopy(scene)
    ref=np.asarray(Image.open(reference/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    prior=np.asarray(Image.open(previous/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    watches=('assistantMeasuredPosition','assistantBodyFocus','assistantBevelDepth','assistantIslandBox','assistantPinPose','assistantRowPose')
    nodes=[interpolate(scene['tracks'][key],f) for key in watches]
    focus0=nodes[1][0]
    if str(f) in scene.get('assistantPrism',{}):
        prism=scene['assistantPrism'][str(f)]
    else:
        prism=None
    base_pin=scene.get('assistantEntranceOptics',{}).get(str(f),{}).get('pin')
    state=[0]*14
    def apply(z):
        stage=[v[:] for v in nodes]
        for j in range(3): stage[0][j] +=z[j]
        stage[1][0]=max(.05,focus0+z[3])
        stage[2][0]+=z[4]
        for j in range(4): stage[3][j]+=z[5+j]
        for j in range(3): stage[4][j]+=z[9+j]
        stage[5][0]+=z[12]
        for key,row in zip(watches,stage,strict=True):
            local['tracks'][key]=[[f,*row]]
        if base_pin:
            local['assistantEntranceOptics'][str(f)]['pin']=[base_pin[i]+z[9+i] for i in range(3)]+base_pin[3:]
        if prism is not None:
            local['assistantPrism'][str(f)]=[[x,y,*[c*(1+z[13]) for c in spectrum]] for x,y,*spectrum in prism]
        return stage
    raw=float(np.abs(ref-prior).mean());best=raw
    moves=[
      (-4,-2,0,2,4),(-6,-3,-1.5,0,1.5,3,6),(-5,-2,0,2,5),
      (-1.8,-.85,0,.75,1.5),(-9,-4,0,3,7),
      (-6,-3,0,3,6),(-8,-4,0,4,8),(-9,-4,0,4,9),(-8,-4,0,4,8),
      (-6,-3,0,3,6),(-7,-3,0,3,7),(-9,-4,0,4,9),(-9,-4,0,4,9),(-.6,-.35,0,.25)
    ]
    for key in (1,0,2,3,4,6,7,5,8,9,10,11,12,13,3,4):
        if key==13 and prism is None:
            continue
        for val in moves[key]:
            change=state[:];change[key]=val
            apply(change)
            diff=float(np.abs(np.asarray(Film(local).frame(f),dtype=np.int16)-ref).mean())
            if diff<best:
                best=diff;state=change
    return f,raw,best,state,apply(state)
out=[]
with ThreadPoolExecutor(max_workers=4) as exe:
    for result in exe.map(fit,range(134,142)):
        print(result,flush=True)
        out.append(result)
(root/'reveal-opening-probe.json').write_text(json.dumps(out,indent=2)+'\n')
