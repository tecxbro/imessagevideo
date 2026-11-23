from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json,sys,math
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film,title_heart,layer
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
baseline=Path('/tmp/sidehoe-exit.H4euj0/tile-push-full')

def fit(f):
    raw=json.loads(json.dumps(scene['titleHeartOptics'][str(f)]))
    sc=deepcopy(scene)
    sc['titleHeartOptics'][str(f)]=[[*a[:5],0,*a[6:]] for a in raw]
    plain=Film(sc).frame(f).convert('RGBA')
    ref=Image.open(source/f'{f:06}.png').convert('RGB')
    old=Image.open(baseline/f'{f:06}.png').convert('RGB')
    current=[list(a) for a in raw]
    for i,orig in enumerate(raw):
        if orig[5]<.13:
            continue
        x,y,w,h=orig[:4]
        span=math.ceil(.66*max(w,h)+12)
        roi=(math.floor(x-span),math.floor(y-span),math.ceil(x+span),math.ceil(y+span))
        bg=plain.crop(roi)
        compare=np.array(ref.crop(roi),dtype=np.int16)
        around=[(j,a) for j,a in enumerate(current) if j!=i and abs(a[0]-x)<span+max(a[2],a[3]) and abs(a[1]-y)<span+max(a[2],a[3])]
        ink=np.array(bg.convert("RGB"),dtype=np.int16)
        # Only lean on areas where the heart's tint is visible. Unmatched black
        # glyph edges would otherwise pull the heart away from its trajectory.
        keep=(ink[:,:,0]>136) | (compare[:,:,0]>compare[:,:,1]+42)
        if keep.sum()<10:
            continue
        def stamp(img, pose):
            a=pose[:]
            a[0]-=roi[0]
            a[1]-=roi[1]
            title_heart(img,a)
        left=bg.copy()
        for j,a in around:
            if j<i:
                stamp(left,a)
        drawn=[a for j,a in around if j>i]
        def score(pose):
            a=left.copy()
            stamp(a,pose)
            for b in drawn:
                stamp(a,b)
            d=np.abs(np.array(a.convert("RGB"),dtype=np.int16)-compare)
            return d[keep].mean()
        best=score(current[i])
        opts=((-1.5,-.8,-.35,0,.35,.8,1.5),(-1.5,-.8,-.35,0,.35,.8,1.5),
              (-2.4,-1.2,0,1.2,2.4),(-2.4,-1.2,0,1.2,2.4),(-6,-3,0,3,6),
              (-.10,-.06,-.03,0,.03,.06,.10),(-.055,0,.055),(-.25,0,.25))
        for col,steps in enumerate(opts):
            for offset in steps:
                a=current[i][:]
                a[col]=round(orig[col]+offset,4)
                if col==5:
                    a[col]=min(1,max(0,a[col]))
                error=score(a)+abs(offset)*(.008 if col not in (4,5) else .002)
                if error<best:
                    best=error
                    current[i]=a
    sc['titleHeartOptics'][str(f)]=current
    now=np.array(Film(sc).frame(f),dtype=np.int16)
    diff=np.abs(np.array(ref,dtype=np.int16)-now)
    olderr=float(np.abs(np.array(ref,dtype=np.int16)-np.array(old,dtype=np.int16)).mean())
    return f,olderr,float(diff.mean()),current

records={}
with ThreadPoolExecutor(max_workers=5) as pool:
    for f,b,a,c in pool.map(fit,range(186,207)):
        print(f,round(b,6),round(a,6),flush=True)
        if a<b:
            records[str(f)]=c
(root/'hearts-fit.json').write_text(json.dumps(records,indent=2)+'\n')
