from copy import copy
from pathlib import Path
from PIL import Image
from render import Film
from concurrent.futures import ProcessPoolExecutor
import sys,json
import numpy as np

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def solve(f):
    key=str(f)
    light=np.array(scene['assistantEntranceOptics'][key]['flare'])
    stage=Film(scene)
    blank=copy(scene)
    blank['assistantRailRefraction']={key:[]}
    base=np.asarray(Film(blank).frame(f),dtype=np.float32)
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    old=np.asarray(stage.frame(f),dtype=np.float32)
    all_fields=[]
    for xmin,xmax,priors in ((14,200,light[:5]),(808,1000,light[5:])):
        y,x=np.mgrid[907:1000:3,xmin:xmax:3]
        x=x.ravel()
        y=y.ravel()
        a=base[y,x]
        b=target[y,x]
        prior=priors[:,:5]
        paint=priors[:,5:]
        strength=np.eye(len(priors))*1.1

        def fit(specs):
            channels=[]
            for xx,yy,w,h,angle in specs:
                channels.append(np.exp(-((x-xx-(y-yy)*angle)/w)**2-((y-yy)/h)**2))
            D=np.stack(channels,axis=1)
            coef=paint.copy()
            for n in range(2):
                residual=np.abs(np.clip(a+D@coef,0,255)-b)
                weights=(7+residual)**-.37
                for c in range(3):
                    X=D*weights[:,c,None]
                    vec=np.linalg.solve(D.T@X+strength,X.T@(b-a)[:,c]+strength@paint[:,c])
                    coef[:,c]=np.clip(vec,-170,170)
            d=np.abs(np.clip(a+D@coef,0,255)-b)
            fn=float(d.mean())+np.sum(np.abs(specs-prior)*[.0014,.0008,.0009,.0007,.001])
            return fn,coef

        proposals=prior.copy()
        best=fit(proposals)
        for mult in (1,.52,.25):
            for i in range(len(proposals)):
                for j,step in enumerate((3.7,5.8,2.8,5.4,.12)):
                    start=proposals[i,j]
                    for sign in (-1,1):
                        trial=proposals.copy()
                        trial[i,j]=start+sign*step*mult
                        if min(trial[i,2:4])<4:
                            continue
                        res=fit(trial)
                        if res[0]<best[0]:
                            best,proposals=res,trial
        all_fields.extend(np.round(np.column_stack([proposals,best[1]]),5).tolist())

    trial=copy(scene)
    trial['assistantRailRefraction']={key:all_fields}
    revised=np.asarray(Film(trial).frame(f),dtype=np.float32)
    earlier,during=(np.abs(m-target) for m in (old,revised))
    print(f,earlier.mean(),during.mean(),earlier[907:].mean(),during[907:].mean(),flush=True)
    return (key,all_fields) if during.mean()<earlier.mean() else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=2) as pool:
        records=dict(row for row in pool.map(solve,(136,137)) if row)
    (root/'flare-fit.json').write_text(json.dumps(records,indent=2)+'\n')
