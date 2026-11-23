import json
from pathlib import Path
import sys
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import minimize

p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
s=json.loads((p/'project/scene.json').read_text())['tracks']
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-follow-entry.0vQCoz/final-dual-frames')
out={}
for f in range(701,731):
    cx,cy,w,h,k=interpolate(s['closingBadgeShape'],f)
    rr=(round(cx-w/2-22),round(cy-h/2-22),round(cx+w/2+22),round(cy+h/2+22))
    l,t,r,b=rr
    X,Y=cx-l,cy-t
    A,B=[np.asarray(Image.open(d/f'{f:06d}.png').convert('RGB').crop(rr),dtype=np.float32).mean(2)
         for d in (src,old)]
    yy,xx=np.mgrid[2:A.shape[0]-2:3,2:A.shape[1]-2:3]
    tr=A[yy,xx]
    inside=(abs(xx-X)<w*.38)&(abs(yy-Y)<h*.38)
    weight=np.where(inside,.93,1.3)
    base=np.array([0,0,1.,1.])
    candidates=[]
    for radius in [0,.45,.85,1.25,1.8,2.5,3.4,4.2,5.2,6.4,7.4]:
        C=gaussian_filter(B,radius) if radius else B
        def error(v):
            dx,dy,sx,sy=v
            px=(xx-X-dx)/sx+X
            py=(yy-Y-dy)/sy+Y
            guess=map_coordinates(C,(py,px),order=1,prefilter=False)
            e=guess-tr
            return float(np.mean(weight*(abs(e)+e*e*.013)))
        if radius==0:
            baseline=error(base)
        best=minimize(error,base,bounds=((-2.5,2.5),(-4,4),(.982,1.02),(.977,1.03)),
                  method='Powell',options={'maxiter':14,'ftol':.0015})
        candidates.append((best.fun,[*np.round(best.x,4).tolist(),radius]))
    value,controls=min(candidates,key=lambda x:x[0])
    out[f]={'controls':controls,'error':[round(baseline,4),round(float(value),4)]}
    print(f,out[f],flush=True)
(p/'badge-focus.json').write_text(json.dumps(out,indent=2)+'\n')
