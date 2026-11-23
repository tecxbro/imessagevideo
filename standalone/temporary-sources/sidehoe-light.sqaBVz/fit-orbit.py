from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json,sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film,interpolate
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
baseline=Path('/tmp/sidehoe-sofia.fuoOwt/clean-frames')
readings=json.loads((root/'orbit-landmarks.json').read_text())

def fit(f):
    local=deepcopy(scene)
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    old=np.asarray(Image.open(baseline/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    orig=[*interpolate(scene['tracks']['redOrbit'],f),*interpolate(scene['tracks']['blueOrbit'],f)]
    def select(a,k,key):
        r,g,b=np.moveaxis(a,2,0)
        x,y,size=orig[k:k+3]
        lo,hi=int(x-size*.68),int(x+size*.76)
        top,bottom=int(y-size*.70),int(y+size*.70)
        if key=='red':
            mask=(r-g>80)&(r>208)&(g<147)&(b<230)
        else:
            mask=(b-r>67)&(b-g>50)&(b>226)&(g>100)&(g<191)
            if f<534:
                lo=min(lo,238)
            hi=min(hi,571)
        yy,xx=np.where(mask[top:bottom,lo:hi])
        if len(yy)<100:
            return x,y,size
        return ((xx.min()+xx.max()+1)/2+lo,(yy.min()+yy.max()+1)/2+top,
                max(xx.max()-xx.min(),yy.max()-yy.min()))
    seeds=orig[:]
    for k,key in ((0,'red'),(3,'blue')):
        im=select(ref,k,key); prev=select(old,k,key)
        for j in range(3):
            delta=im[j]-prev[j]
            seeds[k+j]+=float(delta*.75 if j==2 else delta)
    def overlay(name,q):
        track=local['tracks'][name]
        for i,a in enumerate(track):
            if a[0]==f:
                track[i]=[f,*q]
                break
            if a[0]>f:
                track.insert(i,[f,*q])
                break
    def rate(row):
        overlay('redOrbit',row[:3])
        overlay('blueOrbit',row[3:])
        return float(np.abs(np.array(Film(local).frame(f),dtype=np.int16)-ref).mean())
    before=float(np.abs(old-ref).mean())
    score=before
    best=orig[:]
    for candidate in (seeds,[*seeds[:3],*orig[3:]],[*orig[:3],*seeds[3:]]):
        value=rate(candidate)
        if value<score:
            score=value;best=candidate
    for _ in range(2):
        for i in range(6):
            entry=best[i]
            for delta in (-6,-4,-2,0,2,4,6):
                row=best[:]
                row[i]=entry+delta
                val=rate(row)
                if val<score:
                    score=val;best=row
    return f,before,score,[round(x,5) for x in best]
result=[]
with ThreadPoolExecutor(max_workers=6) as ex:
    for row in ex.map(fit,range(518,545)):
        print(row,flush=True)
        result.append(row)
(root/'orbit-fit.json').write_text(json.dumps(result,indent=2)+'\n')
