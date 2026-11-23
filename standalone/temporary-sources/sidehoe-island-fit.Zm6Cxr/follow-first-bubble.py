from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import copy, deepcopy
from PIL import Image, ImageDraw
from render import Film
import sys,json
import numpy as np

root=Path(sys.argv[1])
s=json.loads((root/'project/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def measure(f):
    label=str(f)
    entry=deepcopy(s['threadRegistration']['follow'][label])
    base_box,ink=entry['items'][0]
    l,t,r,b=base_box
    xt,yt=max(l-24,0),max(t-28,0)
    xr,yb=min(r+24,1000),min(b+4,1000)
    a=Image.open(reference/f'{f:06}.png').convert('RGB')
    crop=np.asarray(a.crop((xt,yt,xr,yb)),dtype=np.float32)
    gray=crop.mean(2)
    width,height=xr-xt,yb-yt
    center=round((l+r)/2)-xt
    hist=np.median(gray[:,center-24:center+24],axis=1)
    hit=np.flatnonzero(hist<248)
    if not hit.size:
        return {}
    top,bottom=hit[0]+yt,hit[-1]+yt+1
    start=(l,top,r,bottom,min((bottom-top)*.43,48))
    glass=np.array([253,253,253])
    fillmask=(gray>234)&(gray<246)&(np.indices(gray.shape)[0]>hit[0]+8)&(np.indices(gray.shape)[0]<hit[-1]-5)
    if not np.any(fillmask):
        return {}
    tone=np.rint(np.median(crop[fillmask],axis=0)).astype(int).tolist()
    field=np.clip((glass.mean()-gray)/(glass.mean()-np.mean(tone)),0,1)
    def score(k):
        x0,y0,x1,y1,roundness=k
        h=y1-y0
        frame=Image.new('L',(width,height),0)
        scene=ImageDraw.Draw(frame)
        tx=x0+h*.13-xt
        ty=y0-yt
        scene.rounded_rectangle((tx,ty,x1-xt-1,y1-yt-1),roundness,fill=255)
        # Include the little grey tail in the silhouette.
        scene.polygon(((tx+1,ty+h-18),(tx-h*.10,ty+h-1),(tx+15,ty+h-4)),fill=255)
        return float(np.abs(np.asarray(frame,dtype=float)/255-field).mean())
    win=score(start)
    best=list(start)
    for mul in (1,.50):
        for i,step in enumerate((6,3,6,3,5)):
            prior=best[i]
            for move in (-2,-1,1,2):
                values=best[:]
                values[i]=prior+step*mul*move
                result=score(values)
                if result<win:
                    best,win=values,result
    l0,y0,r0,b0,radius=best
    raw=np.asarray(a,dtype=np.float32).mean(2)
    initial_ink=[list(row) for row in ink]
    for n,(gx,gy,gw,gh) in enumerate(ink):
        box=(max(int(gx)-8,int(l0)+5),max(int(gy)-9,int(y0)+4),
             min(int(gx+gw)+20,int(r0)-10),min(int(gy+gh)+8,int(b0)-4))
        a0,b0i,c0,d0=box
        patch=raw[b0i:d0,a0:c0]
        mask=patch<175
        intervals=np.flatnonzero(mask.sum(1)>max(7,gw*.023))
        if not intervals.size:
            continue
        spans=np.split(intervals,np.where(np.diff(intervals)>2)[0]+1)
        span=max(spans,key=len)
        q,p=span[0],span[-1]+1
        yy,xx=np.where(mask[q:p])
        if len(xx)>180 and 12<=p-q<=gh+9:
            initial_ink[n]=[int(a0+xx.min()),int(b0i+q),int(xx.max()-xx.min()+1),int(p-q)]
    entry['items'][0]=[[round(k,3) for k in (l0,y0,r0,b0)],initial_ink]
    entry['corners'][0]=round(radius,2)
    entry['bubbleFill']=[tone,[232,232,235]]
    opts=[entry]
    fallback=deepcopy(entry)
    fallback['items'][0][1]=ink
    opts.append(fallback)
    old=np.asarray(Film(s).frame(f),dtype=np.int16)
    target=np.asarray(a,dtype=np.int16)
    view=np.s_[yt:yb,xt:xr]
    full=float(np.abs(old-target).mean())
    initial=float(np.abs(old[view]-target[view]).mean())
    best=initial
    adopted=None
    for option in opts:
        scene=copy(s)
        scene['threadRegistration']=copy(s['threadRegistration'])
        scene['threadRegistration']['follow']=copy(s['threadRegistration']['follow'])
        scene['threadRegistration']['follow'][label]=option
        new=np.asarray(Film(scene).frame(f),dtype=np.int16)
        local=float(np.abs(new[view]-target[view]).mean())
        overall=float(np.abs(new-target).mean())
        if local<best and overall<full:
            best=local
            adopted=option
    print(f,round(initial,5),round(best,5),adopted and adopted['items'][0],flush=True)
    return {label:adopted} if adopted else {}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        data={}
        for record in pool.map(measure,range(671,694)):
            data.update(record)
    (root/'follow-bubble-fit.json').write_text(json.dumps(data,indent=2,default=lambda n:n.item())+'\n')
