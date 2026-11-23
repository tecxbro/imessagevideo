from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json,sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'clean'))
from render import Film,interpolate
scene=json.loads((root/'clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=root/'clean-frames'

def fit(f):
    sc=deepcopy(scene)
    old=np.array(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    ref=np.array(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    def set_row(name,values):
        t=sc['tracks'][name]
        for i,r in enumerate(t):
            if r[0]==f:
                t[i]=[f,*values];break
            if r[0]>f:
                t.insert(i,[f,*values]);break
    def get(name):
        return interpolate(scene['tracks'][name],f)
    before=np.abs(ref-old).mean()
    parameters=[*get('followMeasuredCamera'),*get('followKeyboardY'),*get('followExposure'),*get('followMessageLift'),*get('followLowerLift')]
    v=parameters[:]
    def apply(row):
        set_row('followMeasuredCamera',row[:3]);set_row('followKeyboardY',row[3:4]);set_row('followExposure',row[4:5])
        set_row('followMessageLift',row[5:6]);set_row('followLowerLift',row[6:7])
    def rate(row):
        apply(row)
        return float(np.abs(np.array(Film(sc).frame(f),dtype=np.int16)-ref).mean())
    best=before
    moves=[(-3,-1,0,1,3),(-18,-12,-8,-4,0,4,8,12,18,25,32),(-.015,-.009,-.005,0,.005,.010,.02),
           (-20,-12,-6,-2,0,3,6,12,18),(-42,-28,-12,-6,0,6,14,25,42),
           (-16,-10,-6,-3,0,3,6,10,15),(-15,-9,-5,-2,0,3,6,10,15)]
    for k in (1,3,2,1,0,4,5,6,3,4):
        for delta in moves[k]:
            row=v[:]
            row[k]=parameters[k]+delta
            if k==4 and row[k]<0:
                continue
            new=rate(row)
            if new<best:
                best=new;v=row
    return f,float(before),float(best),parameters,v

result=[]
with ThreadPoolExecutor(max_workers=5) as pool:
    for record in pool.map(fit,range(624,631)):
        print(record,flush=True)
        result.append(record)
(root/'follow-entry-fit.json').write_text(json.dumps(result,indent=2)+'\n')
