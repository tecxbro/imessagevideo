from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
import render
from treatments import follow_pointer

p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def fit(f):
    x,y,w,h,soft_x,soft_y,opacity,lean=s['followPointerOptics'][str(f)]
    contour=s.get('followPointerContour',{}).get(str(f))
    box=(round(x)-9,round(y)-6,round(x+w+max(0,lean))+9,round(y+h)+7)
    l,t,r,b=box
    head=render.Film(s).frame(f).crop(box)
    original=render.follow_pointer
    render.follow_pointer=lambda *a,**k:None
    try:
        substrate=render.Film(s).frame(f).crop(box).convert('RGBA')
    finally:
        render.follow_pointer=original
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB').crop(box),dtype=np.int16)
    before=np.abs(np.asarray(head,dtype=np.int16)-target).mean()
    origin=np.array([x-l,y-t,w,h,soft_x,soft_y,opacity,lean])
    best=origin.copy()
    error=float('inf')
    def loss(values):
        image=substrate.copy()
        xx,yy,ww,hh,soft_x,soft_y,alpha,slant=values
        follow_pointer(image,xx,yy,ww,hh,soft_x,alpha,lean=slant,
                       vertical_softness=soft_y,rounded=True,contour=contour)
        return np.abs(np.asarray(image,dtype=np.int16)[:,:,:3]-target).mean()
    error=loss(best)
    for round_scale in (1,.65,.35,.15):
        for i,magnitude in enumerate((.46,.45,.8,.95,.15,.23,.02,.61)):
            axis=best[i]
            for step in (-2,-1,1,2):
                trial=best.copy()
                trial[i]=axis+step*magnitude*round_scale
                if np.any(abs(trial[:4]-origin[:4])>np.array([1.6,1.45,4.0,4.5])):
                    continue
                if np.min(trial[4:6])<0 or np.max(trial[4:6])>2.1 or not .90<=trial[6]<=1:
                    continue
                score=loss(trial)
                if score<error:
                    best,error=trial,score
    result=best.copy()
    result[:2]+=(l,t)
    print(f,round(float(before),4),round(float(error),4),result.round(4).tolist(),flush=True)
    return (str(f),result.round(4).tolist()) if error<before-.35 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        result=dict(v for v in pool.map(fit,range(676,691)) if v)
    (p/'pointer-fit.json').write_text(json.dumps(result,indent=2)+'\n')
