from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.optimize import minimize
import json,sys

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=root/'display-probe'
results={}
for f in range(134,162):
    a,b=[np.array(Image.open(d/f'{f:06d}.png').convert('RGB'),dtype=np.float32) for d in (source,prior)]
    l,t,w=interpolate(scene['tracks']['assistantMeasuredPosition'],f)
    top=round(t-42)
    bottom=round(t+75)
    step=13 if f<=137 else 31
    controls=[]
    previous=[]
    later=[]
    for x in range(112, 895, step):
        xs=np.arange(x-3,x+4)
        left=np.arange(top,bottom)
        paper=a[top:top+9,xs].mean(axis=(0,1))
        aa=(paper-a[top:bottom,xs]).mean(1)
        bb=(paper-b[top:bottom,xs]).mean(1)
        k=np.flatnonzero(aa.mean(1)>115)
        j=np.flatnonzero(bb.mean(1)>115)
        if not k.size or not j.size:
            continue
        def rim(profile,lo):
            for i in range(lo+13,len(profile)-4):
                if np.max(profile[i:i+4,1])<104:
                    return [lo,i]
            return []
        ax,bx=rim(aa,k[0]),rim(bb,j[0])
        if not ax or not bx or min(np.diff(ax)[0],np.diff(bx)[0])<10:
            continue
        m,n=ax
        u,v=bx
        start=max(0,min(m,u)-9)
        end=min(len(left),max(n,v)+8)
        iy=np.arange(start,end)
        target=aa[iy]
        beta=np.mean(aa[m+3:max(m+4,min(n,m+14)),1])
        alpha=np.mean(bb[u+3:max(u+4,min(v,u+14)),1])
        c_guess=float(np.clip(beta/max(50,alpha),.64,1.28))
        def residual(z):
            p,q,gain=z
            xy=np.interp(iy,[0,m+p,n+q,len(left)-1],[0,u,v,len(left)-1])
            transform=np.stack([np.interp(xy,np.arange(len(left)),channel) for channel in bb.T],axis=1)
            error=(gain*transform-target)
            return float(np.mean(np.abs(error)+.009*(error**2)))+.06*(p*p+q*q)+4.2*(gain-1)**2
        result=minimize(residual,[0,0,c_guess],method='Powell',
                        bounds=[(-7.0,7.0),(-7.0,7.0),(.64,1.29)],
                        options={'maxiter':16,'ftol':.002})
        p,q,gain=result.x
        new_a,new_b=top+m+p,top+n+q
        if new_b-new_a<9:continue
        x_mid=float(x)
        controls.append([x_mid,new_a,new_b,top+u,top+v,gain])
        xy=np.interp(iy,[0,m+p,n+q,len(left)-1],[0,u,v,len(left)-1])
        transform=np.stack([np.interp(xy,np.arange(len(left)),channel) for channel in bb.T],axis=1)
        previous.extend(np.abs(bb[iy]-target).flatten().tolist())
        later.extend(np.abs(gain*transform-target).flatten().tolist())
    if len(controls)<12:continue
    controls=np.array(controls)
    records=[round(np.mean(previous),3),round(np.mean(later),3)]
    print(f,len(controls),records,flush=True)
    results[f]=[top,bottom,np.round(controls,4).tolist()]
(root/'upper-fit.json').write_text(json.dumps(results,indent=2)+'\n')
