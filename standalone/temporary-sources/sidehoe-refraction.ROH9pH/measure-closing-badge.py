"""Estimate an editable rounded outline from source edge samples."""
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

scratch=Path(sys.argv[1])
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
scene=json.loads((scratch/'project/scene.json').read_text())
shapes={int(v[0]):v[1:] for v in scene['tracks']['closingBadgeShape']}
result={}
for frame in range(701,712):
    x,y,w,h,r=shapes[frame]
    l,t=np.floor([x-w/2-6,y-h/2-6]).astype(int)
    right,bottom=np.ceil([x+w/2+6,y+h/2+6]).astype(int)
    target,prior=[np.asarray(Image.open(root/f'{frame:06}.png').convert('RGB'),np.float32)[t:bottom,l:right]
                  for root in (source,scratch/'clean-frames')]
    yy,xx=np.mgrid[t:bottom,l:right].astype(float)
    xx+=.5
    yy+=.5
    # The face tone varies vertically because of the top reflection.
    shade=np.percentile(target[:,target.shape[1]//2-5:target.shape[1]//2+5].mean(2),50,axis=1)
    end_mask=(yy[:,0]>y+h*.15)&(yy[:,0]<y+h*.44)
    shade[(yy[:,0]>y-h*.18)&(yy[:,0]<y+h*.19)]=float(np.median(shade[end_mask]))
    shade=np.convolve(np.clip(shade,51,94),[.08,.18,.48,.18,.08],mode="same")
    paper=np.median(target[0:3].mean(2))
    alpha=np.clip((paper-target.mean(2))/(paper-shade[:,None]),0,1)
    band=(alpha>.02)&(alpha<.98)
    band|=np.maximum(abs(xx-x)-w/2,abs(yy-y)-h/2)>-4
    band&=(yy<y-h*.32)|(yy>y+h*.32)|(abs(xx-x)>w*.46)
    def modeled(v):
        cx,cy,width,height,rx,ry,feather=v
        dx=abs(xx-cx)-(width/2-rx)
        dy=abs(yy-cy)-(height/2-ry)
        # Approximate Euclidean distance to the elliptical rounded corners.
        sx=np.maximum(dx,0)/rx
        sy=np.maximum(dy,0)/ry
        length=np.sqrt(sx*sx+sy*sy)
        distance=(length-1)/(np.sqrt((sx/rx)**2+(sy/ry)**2)/np.maximum(length,1e-5)+1e-6)
        return np.clip(.5-distance/feather,0,1)
    first=np.array([x,y,w,h,r/256*w,r/256*h,1.6])
    span=np.array([2,2,4,4,10,10,1.3])
    def cost(v):
        miss=(modeled(v)-alpha)[band]
        return np.mean(np.sqrt(.15**2+miss*miss)-.15)
    fitted=first.copy()
    best=cost(fitted)
    for precision in (1,.48,.23,.11,.06):
        for k,step in enumerate((.65,.65,1.3,1.3,3,3,.32)):
            pivot=fitted.copy()
            for n in (-2,-1,1,2):
                candidate=pivot.copy()
                candidate[k]+=n*step*precision
                if abs(candidate[k]-first[k])>span[k]:
                    continue
                score=cost(candidate)
                if score<best:
                    fitted,best=candidate,score
    prior_alpha=np.clip((paper-prior.mean(2))/(paper-shade[:,None]),0,1)
    prev=float(np.abs(prior_alpha-alpha)[band].mean())
    revised=float(np.abs(modeled(fitted)-alpha)[band].mean())
    print(frame,round(prev,5),round(revised,5),fitted.round(4).tolist(),flush=True)
    if revised<prev:
        result[str(frame)]=fitted.round(4).tolist()
(scratch/'closing-outline-fit.json').write_text(json.dumps(result,indent=2)+'\n')
