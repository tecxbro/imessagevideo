from pathlib import Path
from copy import deepcopy
from PIL import Image
from treatments import follow_pointer
from render import Film
import numpy as np
import json

p=Path(__file__).parent
s=json.loads((p/'cursor-next'/'scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old_path=p/'clean-frames'
standard=np.array([(0,0),(1,.558),(.984,.596),(.595,.601),
                   (.806,.946),(.799,.978),(.760,.997),(.688,1),
                   (.648,.979),(.362,.684),(0,.794)])
target=np.array([(.012,0),(1,.565),(.984,.610),(.595,.615),
                 (.825,.946),(.805,.981),(.764,.998),(.689,1),
                 (.619,.974),(.352,.684),(.008,.806)])
retained={}
for f in range(670,696):
    frame=str(f)
    x,y,w,h,sx,sy,alpha,lean=s['followPointerOptics'][frame]
    variant=deepcopy(s)
    variant['followPointerOptics'][frame][6]=0
    rect=(int(x)-11,int(y)-11,int(x+w+abs(lean))+13,int(y+h)+13)
    im=Film(variant).frame(f)
    bg=im.crop(rect).convert('RGBA')
    u=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB').crop(rect),dtype=np.float32)
    a=np.asarray(Image.open(old_path/f'{f:06}.png').convert('RGB').crop(rect),dtype=np.float32)
    hue=(u.max(2)-u.min(2))
    # Inspect the handle and edge without scoring foreground emoji as arrow ink.
    mask=(hue<42)&(u.max(2)<188)
    def cost(image):
        rgb=np.asarray(image.convert('RGB'),dtype=np.float32)
        diff=np.abs(rgb-u)
        return float(diff.mean()),float(diff[mask].mean())
    best=None
    for q in (0,.5,.75,1,1.25):
        for dx in (-.35,0,.35):
            for dy in (-.35,0,.35):
                contour=standard+(target-standard)*q
                moving=bg.copy()
                follow_pointer(moving,x-rect[0]+dx,y-rect[1]+dy,w,h,sx,alpha,lean,
                               vertical_softness=sy,rounded=True,contour=contour)
                v=cost(moving)
                value=v[0]+v[1]*.40
                if best is None or value<best[0]:
                    best=value,q,dx,dy,v,contour
    old=(np.abs(a-u).mean(),np.abs(a-u)[mask].mean())
    _,q,dx,dy,v,contour=best
    if v[0]<old[0] and v[1]<old[1] and q:
        retained[frame]=dict(outline=contour.tolist(),dx=dx,dy=dy,reference=old[0].item(),fitted=v[0])
    print(f, tuple(round(float(n),3) for n in old), q,dx,dy,tuple(round(n,3) for n in v),flush=True)
(p/'cursor-contour.json').write_text(json.dumps(retained,indent=2)+'\n')
