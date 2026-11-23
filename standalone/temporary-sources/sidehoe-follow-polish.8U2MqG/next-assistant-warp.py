from concurrent.futures import ProcessPoolExecutor
from copy import copy
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from render import Film

root=Path(sys.argv[1])
scene=json.loads((root/'sofia-next/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
xs=np.array([0,37,74,155,236,310,387,474,559,642,727,816,904,949,982,1000])
ys=np.array([0,70,145,230,295,326,355,383,421,460,512,575,634,710,785,860,932,982,1000])
nx,ny=len(xs),len(ys)
level=np.arange(nx*ny).reshape(ny,nx)
operators=[]
for k in (0,1):
    for idx,point in np.ndenumerate(level):
        i,j=idx
        n=i if k==0 else j
        if not 0<n<(ny if k==0 else nx)-1: continue
        row=np.zeros(nx*ny)
        before=level[i-1,j] if k==0 else level[i,j-1]
        after=level[i+1,j] if k==0 else level[i,j+1]
        row[[before,point,after]]=[1,-2,1]
        operators.append(row)
D=np.array(operators)
curvature=D.T@D

def fit(f):
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    pixels=np.asarray(Image.open(root/'clean-frames'/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    target=ref[:,:,0]*.27+ref[:,:,1]*.58+ref[:,:,2]*.15
    prior=pixels[:,:,0]*.27+pixels[:,:,1]*.58+pixels[:,:,2]*.15
    yy,xx=np.mgrid[:1000,:1000]
    film=Film(scene)
    _,lower,_=film.track("assistantMeasuredPosition",f)
    cursor=yy<lower-38
    gradient_y,gradient_x=np.gradient(target)
    energy=np.minimum(1,np.hypot(gradient_x,gradient_y)/30)
    anchors=np.zeros((ny,nx,2))
    weights=np.zeros((ny,nx))
    for i,j in np.ndindex(ny,nx):
        x,y=xs[j],ys[i]
        if x in (0,1000):
            weights[i,j]=.9
            continue
        l,t,r,b=max(18,x-47),max(18,y-53),min(x+47,982),min(y+53,982)
        valid=~cursor[t:b:2,l:r:2]
        detail=energy[t:b:2,l:r:2]
        if len(detail)==0 or (detail*valid).mean()<.018:
            continue
        weight=(.29+detail*.85)*valid
        truth=target[t:b:2,l:r:2]
        old=prior[t:b:2,l:r:2]
        origin=np.average(abs(truth-old),weights=weight)
        if origin<.65:
            continue
        def cost(dx,dy):
            region=prior[t+dy:b+dy:2,l+dx:r+dx:2]
            return np.average(abs(truth-region),weights=weight)
        best=origin
        shift=(0,0)
        for dy in range(-12,13,3):
            for dx in range(-12,13,3):
                val=cost(dx,dy)+.012*(abs(dx)+abs(dy))
                if val<best:
                    shift,best=(dx,dy),val
        qi,qj=shift
        for dy in range(qj-2,qj+3):
            for dx in range(qi-2,qi+3):
                val=cost(dx,dy)+.012*(abs(dx)+abs(dy))
                if val<best:
                    shift,best=(dx,dy),val
        confidence=min(1,float((origin-best)/7))*min(1,detail.mean()/.10)
        if confidence>.018:
            anchors[i,j]=shift
            weights[i,j]=confidence
    w=weights.ravel()
    smooth=np.linalg.solve(np.diag(w+.014)+.21*curvature,w[:,None]*anchors.reshape(-1,2))
    smooth=smooth.reshape((ny,nx,2)).clip(-15,15)
    old=float(abs(ref-pixels).mean())
    data=copy(scene)
    score=old
    improved=None
    for gain in (.42,.66,.86,1.08):
        vals=[xs.tolist(),ys.tolist(),(smooth*gain).round(4).tolist()]
        data['assistantHandsetWarp']={str(f):vals}
        revised=np.asarray(Film(data).frame(f),dtype=np.int16)
        cost=float(np.abs(ref-revised).mean())
        if cost<score:
            score,improved=cost,vals
    print(f,round(old,5),round(score,5),int(np.count_nonzero(weights)),flush=True)
    return (str(f),improved) if score<old-.02 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=7) as pool:
        output=dict(v for v in pool.map(fit,range(134,142)) if v)
    (root/'next-assistant-warp-fit.json').write_text(json.dumps(output,indent=2)+'\n')
