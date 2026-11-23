from pathlib import Path
from PIL import Image
import numpy as np
from scipy.optimize import minimize
import json,sys

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=root/'upper-probe'

def segment(profile):
    candidates=np.flatnonzero(profile[:,1]>114)
    if not candidates.size:return None
    lo=candidates[0]
    for i in range(lo+11,len(profile)-4):
        if np.max(profile[i:i+3,1])<101:
            return lo,i
    return None

data={}
for f in range(134,162):
    left,top,width=interpolate(scene['tracks']['assistantMeasuredPosition'],f)
    a,b=[np.asarray(Image.open(d/f'{f:06d}.png').convert('RGB'),dtype=np.float32) for d in (source,prior)]
    result={}
    for label, left_est, panels in (
            ('left',left,(a,b)), ('right',1000-(left+width),(a[:,::-1],b[:,::-1]))):
        lo=max(0,round(left_est)-32)
        hi=min(1000,round(left_est)+98)
        controls=[]
        before=[]
        after=[]
        y0=min(965,int(top+130))
        step=12 if f in (134,135,136,137) else 26
        for y in range(y0,997,step):
            aa,bb=[np.median(p[y-3:y+4,lo:hi],axis=0) for p in panels]
            paper=(aa[:8]+bb[:8]).mean(axis=0)*.5
            ref=paper-aa; pred=paper-bb
            target=segment(ref); authored=segment(pred)
            if target is None or authored is None: continue
            j,k=target; u,v=authored
            xx=np.arange(max(2,min(j,u)-7),min(len(ref)-2,max(k,v)+7))
            actual=ref[xx]
            def loss(vs):
                du,dv,alpha=vs
                pos=np.interp(xx,[0,j+du,k+dv,len(ref)-1],[0,u,v,len(ref)-1])
                shade=np.stack([np.interp(pos,np.arange(len(ref)),c) for c in pred.T],axis=1)
                e=abs(alpha*shade-actual)
                return float((e+.008*e*e).mean())+.12*(du**2+dv**2)+5*(alpha-1)**2
            initial=(0,0,1)
            opt=minimize(loss,initial,method='Powell',bounds=[(-5,5),(-6,6),(.71,1.23)],
                         options={'maxiter':16,'ftol':.002})
            du,dv,alpha=opt.x
            if k+dv-j-du<=8: continue
            q=abs(pred[xx]-actual).mean()
            before.append(q)
            pos=np.interp(xx,[0,j+du,k+dv,len(ref)-1],[0,u,v,len(ref)-1])
            shade=np.stack([np.interp(pos,np.arange(len(ref)),c) for c in pred.T],axis=1)
            after.append(abs(shade*alpha-actual).mean())
            controls.append([y,lo+j+du,lo+k+dv,lo+u,lo+v,alpha])
        if len(controls)>=5:
            result[label]=[lo,hi,np.round(controls,4).tolist()]
        if f in (134,135,136,137,141,150,158,161) and before:
            print(f,label,len(controls),round(float(np.mean(before)),3),round(float(np.mean(after)),3),flush=True)
    data[f]=result
(root/'lower-sides.json').write_text(json.dumps(data,indent=2)+'\n')
