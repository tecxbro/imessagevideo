from pathlib import Path
from PIL import Image
import json,numpy as np
from scipy.ndimage import label,find_objects,binary_closing

root=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-pullback.nP3qTC/final-title-frames')
def crop(q,b):
    l,t,r,b=map(round,b)
    l,t,r,b=max(0,l),max(0,t),min(1000,r),min(1000,b)
    return l,t,q[t:b,l:r]
def pieces(q,b,predicate,minimum,maximum,close=0):
    l,t,roi=crop(q,b)
    if not roi.size:
        return []
    see=predicate(roi)
    if close:
        see=binary_closing(see,iterations=close)
    cc,nn=label(see)
    out=[]
    for i,(yy,xx) in enumerate(find_objects(cc),1):
        mask=(cc[yy,xx]==i)
        n=mask.sum()
        if minimum<=n<=maximum:
            points=np.argwhere(mask)
            y,x=points.mean(axis=0)
            out.append([float(x+l+xx.start),float(y+t+yy.start),int(n),
                        [l+xx.start,t+yy.start,l+xx.stop,t+yy.stop]])
    return sorted(out,key=lambda t:t[1])
def big(p):
    if not p:return None
    return max(p,key=lambda n:n[2])
def read(q,f):
    dark=lambda a:a.max(2)<152
    cyan=lambda a:(a[:,:,0]<99)&(a[:,:,0]>5)&(a[:,:,1]>135)&(a[:,:,2]>171)
    blue=lambda a:(a[:,:,0]<184)&(a[:,:,1]-a[:,:,0]>19)&(a[:,:,2]-a[:,:,0]>50)
    beige=lambda a:(a[:,:,0]>130)&(a[:,:,0]-a[:,:,2]>33)&(a[:,:,0]-a[:,:,1]>12)
    # Unread dots are measured separately to distinguish photo and text offsets.
    unread=pieces(q,(114,500,220,1000),cyan,45,830)
    mh=pieces(q,(165,310,358,600),beige,3550,30000,close=2)
    dh=pieces(q,(645,310,864,606),blue,3000,32000,close=2)
    status=pieces(q,(150,94,274,306),dark,105,2500,close=6)
    heading=pieces(q,(351,210,650,411),dark,500,5900,close=6)
    return dict(time=big(status),head=big(heading),marie=big(mh),darla=big(dh),unread=unread)
rows={}
for f in range(10,50):
    records=[read(np.asarray(Image.open(d/f'{f:06}.png').convert('RGB'),dtype=np.int16),f) for d in (source,prior)]
    rows[f]=records
    if f in (10,16,22,31,37,40,41,42,43,45,48,49):
        print(f)
        for a,b in zip(records,('source','previous')):
            print(b,{k:([tuple(round(x,1) for x in t[:2]) for t in v] if k=='unread' else (None if v is None else tuple(round(x,1) for x in v[:3]))) for k,v in a.items()})
(root/'inbox-landmarks.json').write_text(json.dumps(rows,indent=2)+'\n')
