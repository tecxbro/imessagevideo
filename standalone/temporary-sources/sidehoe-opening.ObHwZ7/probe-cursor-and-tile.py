from pathlib import Path
from PIL import Image
from render import Film
import json
import numpy as np

p=Path(__file__).parent
s=json.loads((p/'cursor-next/scene.json').read_text())
film=Film(s)
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=p/'clean-frames'
stats=[]
for frame in [*range(614,621),*range(669,697)]:
    f=str(frame)
    name=f'{frame:06}.png'
    image=film.frame(frame)
    rect=(380,max(0,630+(frame-615)*28),620,min(1000,885+(frame-615)*38))
    if frame>=669:
        if f not in s['followPointerOptics']:
            rect=(400,480,550,650)
        else:
            x,y,w,h,_,_,_,lean=s['followPointerOptics'][f]
            rect=(int(x)-11,int(y)-11,int(x+w+abs(lean))+13,int(y+h)+13)
    a,b,c=[np.asarray(im.convert('RGB'),dtype=np.int16) for im in (Image.open(source/name),Image.open(prior/name),image)]
    u,v=[np.abs(a-q) for q in (b,c)]
    x0,y0,x1,y1=rect
    patch=np.s_[y0:y1,x0:x1]
    pixel_counts=int(np.sum(np.any(b!=c,axis=2)))
    metrics=dict(frame=frame,changed_pixels=pixel_counts,full=[u.mean(),v.mean()],
                 local=[u[patch].mean(),v[patch].mean()])
    stats.append(metrics)
    print(frame,pixel_counts,*[[round(float(d),4) for d in metrics[k]] for k in ('full','local')],flush=True)
(p/'cursor-and-tile.json').write_text(json.dumps(stats,indent=2)+'\n')
