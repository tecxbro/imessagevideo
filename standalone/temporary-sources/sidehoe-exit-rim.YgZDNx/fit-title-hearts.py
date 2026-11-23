"""Fit independently drawn heart contours on the authored title's rendered matte."""
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from render import Film, title_heart

w=Path(sys.argv[1])
s=json.loads((w/'heart-next/scene.json').read_text())
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def fit(frame):
    key=str(frame)
    poses=s["titleHeartOptics"][key]
    base_scene={**s,'titleHeartOptics':{key:[p[:5]+[0]+p[6:] for p in poses]}}
    bed=Film(base_scene).frame(frame).convert("RGBA")
    target=Image.open(ref/f"{frame:06}.png").convert("RGB")
    fitted=[p.copy() for p in poses]
    shape_data={}
    for i, old in enumerate(poses):
        if old[5]<.08:
            continue
        x,y,width,height=old[:4]
        extent=math.ceil(math.hypot(width,height)*.80+5)
        box=(max(0,round(x-extent)),max(0,round(y-extent)),min(1000,round(x+extent)),min(1000,round(y+extent)))
        earlier=bed.crop(box)
        later=Image.new('RGBA',earlier.size)
        for j,p in enumerate(fitted):
            if i==j:
                continue
            title_heart(earlier if j<i else later,[p[0]-box[0],p[1]-box[1],*p[2:]],shape_data.get(str(j)))
        ref_crop=np.asarray(target.crop(box),np.int16)
        g=old[:8].copy()
        base=old[8:]
        controls=[0,0,0,0,0]
        def cost(g,shape):
            stage=earlier.copy()
            title_heart(stage,[g[0]-box[0],g[1]-box[1],*g[2:],*base],shape)
            stage.alpha_composite(later)
            delta=ref_crop-np.asarray(stage,np.int16)[:,:,:3]
            # G and RGB balance hold visibility in pink washes and over black type.
            return float(np.abs(delta).mean())
        first=best=cost(g,None)
        for wave in (1,.5,.24):
            for k,step in enumerate((.7,.7,1.3,1.3,4.8,.038,.034,.26,17,17,27,27,23)):
                v=[*g,*controls]
                center=v[k]
                for sign in (-2,-1,1,2):
                    v[k]=center+step*sign*wave
                    if not 0<=v[5]<=1 or v[7]<0:
                        continue
                    score=cost(v[:8],v[8:])
                    if score<best:
                        best,g,controls=score,v[:8],v[8:]
        if first-best>.035:
            fitted[i]=[*(round(q,5) for q in g),*base]
            shape_data[str(i)]=[round(q,4) for q in controls]
    full=bed.copy()
    for i,p in enumerate(fitted):
        title_heart(full,p,shape_data.get(str(i)))
    base=Film(s).frame(frame)
    target=np.asarray(target,np.int16)
    old,new=[np.abs(np.asarray(m.convert('RGB'),np.int16)-target).mean() for m in (base,full)]
    print(frame,round(old,7),round(new,7),len(shape_data),flush=True)
    if not new<old:
        return key,None
    return key,dict(poses=fitted,contours=shape_data)


if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        results=dict(pool.map(fit,range(188,197)))
    (w/'title-heart-fit.json').write_text(json.dumps({f:v for f,v in results.items() if v},indent=2)+'\n')
