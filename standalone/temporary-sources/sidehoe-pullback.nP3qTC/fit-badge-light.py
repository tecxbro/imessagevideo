from pathlib import Path
import json
import sys
from PIL import Image
import numpy as np
from scipy.ndimage import minimum_filter
from scipy.optimize import least_squares

p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
s=json.loads((p/'project/scene.json').read_text())['tracks']
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-follow-entry.0vQCoz/final-dual-frames')

def normalized(frames):
    for f in frames:
        cx,cy,w,h,_=interpolate(s['closingBadgeShape'],f)
        box=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
        yield [np.asarray(Image.open(folder/f'{f:06d}.png').convert('RGB').transform(
                    (512,512),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC),dtype=np.float32)
                 for folder in (src,old)]

# Measure interior pigments. Edges, cutouts, outlines and heart are excluded.
design=[]
truth=[]
prior=[]
knots=np.array([0,14,31,54,77,108,136,168,194],dtype=float)
for a,b in normalized(range(704,713)):
    ax=(a[:,:,0]>214)&(a[:,:,1]>102)&(a[:,:,0]-a[:,:,1]>6)
    bx=(b[:,:,0]>214)&(b[:,:,1]>102)&(b[:,:,0]-b[:,:,1]>6)
    safe=minimum_filter(ax&bx,size=9)
    yy,xx=np.mgrid[139:279:3,191:322:3]
    mask=safe[yy,xx]
    x,y=xx[mask]-184,yy[mask]-130
    shape=np.stack([np.interp(y,knots,e) for e in np.eye(len(knots))],axis=1)
    x=(x-70)/70
    y=np.clip(y/190,0,1)
    base=np.column_stack((shape,x,(1-x*x),x*y,(1-x*x)*y))
    design.append(base)
    truth.append(a[yy,xx][mask]);prior.append(b[yy,xx][mask])
X=np.concatenate(design)
A=np.concatenate(truth)
B=np.concatenate(prior)
result=[]
for c in range(3):
    beta=np.linalg.lstsq(X,A[:,c],rcond=None)[0]
    fit=least_squares(lambda v:X@v-A[:,c],beta,loss='soft_l1',f_scale=5,max_nfev=26)
    result.append(np.round(fit.x,2).tolist())
pigs=np.array(result).T.tolist()
a=np.abs(A-B).mean()
b=np.abs(A-X@np.asarray(result).T).mean()
print('Interior pigment error',a,b)
print('knots',knots.tolist())
print('coefficients',pigs)
(p/'badge-light.json').write_text(json.dumps(dict(knots=knots.tolist(),coefficients=pigs),indent=2)+'\n')
