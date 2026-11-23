from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from render import Film,refract_control,screen_matte

p=Path(sys.argv[1]); source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
scene=json.loads((p/'project/scene.json').read_text())
def fit(f):
    k=str(f); film=Film(scene)
    x,y,w=film.track('assistantMeasuredPosition',f)
    ref=Image.open(source/f'{f:06}.png').convert('RGB')
    base=Image.open(p/'casing-probe'/f'{f:06}.png').convert('RGB')
    data={}
    groups=[
        ('time',(91,67,204,141)),('cellular',(591,65,669,142)),
        ('wifi',(669,65,726,142)),('battery',(726,65,806,142)),
        ('edit',(107,187,200,252)),('filter',(727,186,787,249)),('heading',(349,170,565,258)),
    ]
    for name,(l,t,r,b) in groups:
        scale=w/900
        box=(round(x+l*scale),round(y+t),round(x+r*scale),round(y+b))
        target=np.asarray(ref.crop(box),np.int16)
        prior=base.crop(box)
        previous=float(np.abs(target-np.asarray(prior,np.int16)).mean())
        matte=screen_matte(prior)
        def cost(param):
            patch=refract_control(prior,param,matte=matte)
            return float(np.abs(target-np.asarray(patch,np.int16)).mean())
        best=previous
        v=[0,0,1,1,0,0,0,1,0,0,0]
        for gap in (3.5,6,9,12,16):
            initial=[*v[:9],gap,.7]
            trial=cost(initial)
            if trial<best:
                best,v=trial,initial
        for precision in (1,.56,.29,.13):
            for i,inc in enumerate((1.7,2.2,.069,.18,.039,.88,.88,.22,.77,3.5,.34)):
                start=v[i]
                better=start
                for sign in (-2,-1,1,2):
                    v[i]=start+sign*inc*precision
                    if (i in (2,3) and not .62<v[i]<1.62 or
                        i==7 and not .40<v[i]<2.4 or i in (8,9) and v[i]<0 or i==10 and not 0<=v[i]<=1):
                        continue
                    result=cost(v)
                    if result<best:
                        best,better=result,v[i]
                v[i]=better
        if best<previous-.12:
            data[name]=[list(box),[round(c,5) for c in v]]
        print(f,name,round(previous,3),round(best,3),[round(c,3) for c in v],flush=True)
    return k,data
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        measured=dict(pool.map(fit,range(153,162)))
    (p/'exit-ink-fit.json').write_text(json.dumps(measured,indent=2)+'\n')
