from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import Film

p=Path(sys.argv[1]); src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
s=json.loads((p/'project/scene.json').read_text()); film=Film(s)

def group(selected,n):
    idx=np.flatnonzero(selected)
    return [a for a in np.split(idx,np.flatnonzero(np.diff(idx)>1)+1) if len(a)>=n]
def mkband(img, axis, center, width0, width1, span, samples, outward, hardware=False):
    a=img if axis=='side' else img.transpose(1,0,2)
    start,stop=max(0,round(center-width0)),min(1000,round(center+width1))
    if stop<=start+4: return None
    cross=a[samples[0]:samples[1],start:stop]; medium=np.median(cross,axis=0)
    darkest=int(np.argmin(medium.mean(1)))
    idx=np.arange(len(medium))
    toward=idx>darkest if outward<0 else idx<darkest
    shade=np.clip((medium.mean(1)-126)/127,0,1)*toward
    inner=min(999,stop+3) if outward<0 else max(0,start-4)
    buttons=[]
    if hardware:
        body=a[span[1]:span[2],start:stop].astype(float)
        rim=idx<darkest-5 if outward<0 else idx>darkest+5
        outer=(rim)&(medium.mean(1)>110)
        if outer.any():
            difference=medium[outer,None,0].T-body[:,:,0][:,outer]
            strength=np.max(difference,axis=1)
            for q in group(strength>24.0,max(12,round(span[2]*.018))):
                local=q[len(q)//3:2*len(q)//3]
                delta=np.median(body[local],axis=0)-medium
                delta[~rim]=0
                if np.max(abs(delta))<21:
                    continue
                buttons.append([int(q[0]+span[1]),int(q[-1]+span[1]),1.65,
                    np.rint(delta).astype(int).clip(-142,142).tolist()])
    # A separate per-row screen pigment remains visible beside the gasket.
    return [axis,start,span,np.rint(medium).astype(int).tolist(),
            np.round(shade,4).tolist(),inner,buttons]

data={}
for f in range(630,660):
    key=str(f); rec=s['followSettledRegistration'][key]
    x,y,scale=film.track('followMeasuredCamera',f); aspect=1
    if 'camera' in rec: x,y,scale,aspect=rec['camera']
    w=scale*400; height=scale*aspect*827
    a=np.asarray(Image.open(src/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    # Fit rail paint in an unobstructed part of the message glass.
    basis=[round(y+scale*222),round(y+scale*432)]
    upper=round(y+scale*54); end=min(1000,round(y+height-scale*54))
    straight=[max(0,upper-1),upper+37,end-34,end]
    tops=[round(x+scale*59),round(x+scale*93),round(x+w-scale*92),round(x+w-scale*57)]
    hi=[round(x+w*.29),round(x+w*.71)]
    bands=[
     mkband(a,'side',x,10,29,straight,basis,-1,True),
     mkband(a,'side',x+w,29,11,straight,basis,1,True),
     mkband(a,'cross',y,5,23,tops,hi,-1),
     mkband(a,'cross',y+height,17,7,tops,hi,1),
    ]
    data[key]=[band for band in bands if band]
    print(f,[(b[0],b[1],b[2],[[sub[0],sub[1]] for sub in b[6]]) for b in data[key]])
(p/'bevel-fit.json').write_text(json.dumps(data,indent=2)+'\n')
