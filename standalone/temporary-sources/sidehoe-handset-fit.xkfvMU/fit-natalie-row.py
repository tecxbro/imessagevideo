from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import copy
import json
import sys

import numpy as np
from PIL import Image
from render import Film

root=Path(sys.argv[1])
scene=json.loads((root/'row-next/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
keys=('avatar','name','preview','time','chevron')

def sample(n):
    key=str(n)
    data=copy.copy(scene)
    data['assistantRowRegistration']={key:{a:[0,0,0] for a in keys}}
    scene_film=Film(scene)
    x,y,width=scene_film.track('assistantMeasuredPosition',n)
    row_y,alpha=scene_film.track('assistantRowPose',n)
    if not alpha or y+row_y>999:
        return {}
    y0=max(0,round(y+row_y-19))
    target=np.asarray(Image.open(reference/f'{n:06}.png').convert('RGB'),dtype=np.float32)
    original=np.asarray(Image.open(root/'clean-frames'/f'{n:06}.png').convert('RGB'),dtype=np.float32)
    empty=np.asarray(Film(data).frame(n),dtype=np.float32)
    controls={}
    for actor in keys:
        data['assistantRowRegistration'][key][actor][2]=1
        component=np.asarray(Film(data).frame(n),dtype=np.float32)
        data['assistantRowRegistration'][key][actor][2]=0
        renderer=component-empty
        footprint=(np.abs(renderer[y0:]).max(2)>3.3)
        yy,xx=np.where(footprint)
        if xx.size<19:
            continue
        x0,x1=max(0,xx.min()-55),min(1000,xx.max()+72)
        a0=max(0,yy.min()-21+y0)
        a1=min(1000,yy.max()+22+y0)
        color=target[a0:a1,x0:x1]-empty[a0:a1,x0:x1]
        pad=58
        patch=np.pad(renderer[a0:a1,x0:x1],((pad,pad),(pad,pad),(0,0)))
        pix_y,pix_x=patch.shape[:2]
        h,w=color.shape[:2]
        initial=float(np.abs(patch[pad:pad+h,pad:pad+w]-color).mean())
        best=initial
        chosen=(0,0,1)
        def score(dx,dy,c):
            newest=patch[pad-dy:pad-dy+h,pad-dx:pad-dx+w]*c
            # Prefer modest registration adjustments when the actor is almost out of frame.
            return float(np.abs(newest-color).mean())+abs(dx)*.0003+abs(dy)*.0015+abs(c-1)*.006
        xshift=range(-34,53,3) if actor in ('avatar','name','preview') else range(-34,52,4)
        for dx in xshift:
            for dy in range(-10,18,2):
                for c in (.7,1,1.22):
                    cost=score(dx,dy,c)
                    if cost<best:
                        best=cost
                        chosen=(dx,dy,c)
        controls[actor]=[*chosen]
    if not controls:
        return {}
    data['assistantRowRegistration'][key]=controls
    change=np.asarray(Film(data).frame(n),dtype=np.float32)
    err0=float(np.abs(target-original).mean())
    err1=float(np.abs(target-change).mean())
    print(n,err0,err1,controls,flush=True)
    return {key:controls} if err1<err0 else {}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=3) as pool:
        result={}
        for item in pool.map(sample,range(135,144)):
            result.update(item)
    (root/'natalie-row-fit.json').write_text(json.dumps(result,indent=2)+'\n')
