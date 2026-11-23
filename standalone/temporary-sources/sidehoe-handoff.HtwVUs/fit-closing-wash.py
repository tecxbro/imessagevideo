from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import interpolate

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
track=scene['tracks']['closingWashFields']
fade=scene['tracks']['endingFade']

gy,gx=np.mgrid[0:1000:13,0:1000:13]
visible=(~((gx>=233)&(gx<=773)&(gy>=298)&(gy<=712)))&(gx>10)&(gy>15)&(gx<990)&(gy<990)
yy,xx=gy[visible]/999,gx[visible]/999
scales=np.array(([.30,.20,.18,.10,.23,12,57,12])*2)
lower=np.array(([-.6,.30,.07,.07,-2.5,-44,-85,-44])*2)
upper=np.array(([2.6,1.9,1.3,.92,2.5,110,350,110])*2)
movement=np.array(( [.39,.27,.23,.17,.55,22,77,18] )*2)

def design(v):
    additions=[]
    for i in range(0,len(v),8):
        cx,cy,sx,sy,skew,r,g,b=v[i:i+8]
        y=yy-cy
        along=(xx-cx+skew*y)/sx
        down=y/sy
        mask=np.exp(-along**2-down**2)
        colors=np.array((r,g,b))
        light=mask[:,None]*colors
        geometry=np.array((
            2*along/sx,2*along*skew/sx+2*down/sy,
            2*along**2/sx,2*down**2/sy,-2*along*y/sx,
        ))
        deriv=[*(light[None]*geometry[:,:,None]),*(mask[None,:,None]*np.eye(3)[:,None,:])]
        additions.append((light,np.array(deriv)))
    field=np.sum([l for l,d in additions],axis=0)
    gradients=np.concatenate([d for l,d in additions],axis=0)
    unclipped=253-field
    active=(unclipped>0)&(unclipped<255)
    return np.clip(unclipped,0,255), -gradients*active

def fit(f):
    a=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.float64)
    target=a[gy[visible],gx[visible]]
    x=np.array(interpolate(track,f))
    initial=x.copy()
    low=np.maximum(lower,initial-movement)
    high=np.minimum(upper,initial+movement)
    gain,=interpolate(fade,f)
    goal=target
    def cost(gray):
        residual=gray*gain-goal
        return float(np.mean(np.abs(residual))),residual
    A,J=design(x)
    base,residual=cost(A)
    best=base
    for pass_ in range(48):
        J=(J*gain*scales[:,None,None]).reshape(16,-1)
        robust=(np.abs(residual.ravel())**2+2.0)**-.5
        weighted_J=J*robust
        normal=weighted_J@J.T
        ridge=np.eye(16)*max(.09,.005*np.max(np.diag(normal))*.83**(pass_//8))
        direction=-np.linalg.solve(normal+ridge, weighted_J@residual.ravel())*scales
        accepted=False
        for amount in (1,.56,.24,.10):
            guess=np.clip(x+direction*amount,low,high)
            gray,grad=design(guess)
            value,result=cost(gray)
            if value<best-.00008:
                x,best,residual,J=guess,value,result,grad
                accepted=True
                break
        if not accepted:
            break
    print(f,round(base,4),round(best,4),flush=True)
    return f,x.round(6).tolist(),base,best

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        fits=list(pool.map(fit,range(711,775)))
    (root/'wash-fit.json').write_text(json.dumps(fits,indent=2)+'\n')
