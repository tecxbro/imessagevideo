from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import sys
import numpy as np

root=Path(__file__).parent
sys.path.insert(0,str(root/'tile-project'))
from render import Film
scene=json.loads((root/'tile-project/scene.json').read_text())
landmarks=json.loads((root/'tile-native-landmarks.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=root/'final-frames'

def fit(f):
    sc=deepcopy(scene)
    before=np.asarray(Image.open(prior/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    anchor=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    bb=landmarks[str(f)][0]['face']
    l,t,r,b=bb
    crop=np.s_[t-30:min(b+8,1000),l-12:r+12]
    def rate(candidate):
        diff=np.abs(candidate-anchor)
        return (float(diff[crop].mean()),float(diff.mean()))
    treatment=next(row for row in sc['tracks']['calendarTileTreatment'] if row[0]==f)
    initial=treatment[:]
    values=(0,1,0,0,1)
    best=rate(before)
    seen=set()
    def evaluate(values):
        if values in seen:
            return None
        seen.add(values)
        detail, defocus, dy, dh, smear = values
        sc['calendarTileProfiles']={str(f):[detail,defocus]}
        treatment[1]=initial[1]+dy
        treatment[-1]=initial[-1]+dh
        treatment[-2]=initial[-2]*smear
        img=np.asarray(Film(sc).frame(f),dtype=np.int16)
        return rate(img)
    for round_no in range(2):
        stages=[(0,(0,.3,.62,.95,1.3,1.65,1.95)),(1,(.75,.92,1,1.12,1.27,1.47)),(2,(-2,-1,0,1,2)),(3,(-.009,0,.009))]
        if f>=616:
            stages.extend([(4,(.7,.85,1,1.14)),(2,(-2,0,1,2,4,6,8,10)),(3,(-.044,-.029,-.018,0,.016,.029))])
        for k,opts in stages:
            if round_no and k in (3,4):
                continue
            for option in opts:
                trial=(*values[:k],option,*values[k+1:])
                score=evaluate(trial)
                if score and score[0]<best[0] and score[1]<=rate(before)[1]+.005:
                    values,best=trial,score
    return f,rate(before),best,values
with ThreadPoolExecutor(max_workers=4) as pool:
    rows={}
    for f,before,after,values in pool.map(fit,range(603,620)):
        print(f,tuple(round(x,4) for x in before),tuple(round(x,4) for x in after),values,flush=True)
        rows[f]=values
(root/'tile-fit.json').write_text(json.dumps(rows,indent=2)+'\n')
