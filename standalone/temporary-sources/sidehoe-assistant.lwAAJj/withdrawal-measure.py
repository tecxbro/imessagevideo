from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects,binary_closing
import json
root=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prev=root/'final-frames'

def bounds(mask, left,top, minimum=0):
    labs,count=label(binary_closing(mask,iterations=1))
    out=[]
    for i,(ys,xs) in enumerate(find_objects(labs),1):
        n=np.count_nonzero(labs[ys,xs]==i)
        if n>=minimum:
            out.append([int(n),[xs.start+left,ys.start+top,xs.stop+left,ys.stop+top]])
    return sorted(out,reverse=True)
def parse(q,f):
    q=np.asarray(q,dtype=np.int16)
    y,x=np.mgrid[0:1000,0:1000]
    g=q.mean(2)
    # Locate side rails on a horizontal blank span above the composer.
    row=np.median(q[585:622],axis=(0,2))
    left=np.flatnonzero((row<130)&(np.arange(1000)<380))
    right=np.flatnonzero((row<130)&(np.arange(1000)>700))
    if not left.size:
        left=np.flatnonzero((row<194)&(np.arange(1000)<380))
    if not right.size:
        right=np.flatnonzero((row<194)&(np.arange(1000)>700))
    lx,rx = int(left[-1]+1),int(right[0])
    l,r=lx+17,rx-13
    r0,g0,b0=np.moveaxis(q[90:540,l:r],2,0)
    grey=(r0>210)&(r0<243)&(np.ptp(q[90:540,l:r],axis=2)<9)
    messages=[rect for n,rect in bounds(grey,l,90,1650) if rect[3]-rect[1]<145]
    blue=(g0-r0>5)&(b0-r0>14)&(r0>110)&(r0<246)
    aqua=bounds(blue,l,90,900)
    tray=q[663:1000,l:r]
    bright=(tray.min(2)>245)&(np.ptp(tray,axis=2)<10)
    key_parts=[rect for n,rect in bounds(bright,l,663,150) if 19<rect[2]-rect[0]<93 and 22<rect[3]-rect[1]<117]
    rows={}
    for location in sorted(key_parts, key=lambda a:a[1]):
        close=next((y for y in rows if abs(location[1]-y)<11),location[1])
        rows.setdefault(close,[]).append(location)
    return dict(rails=[lx,rx],gray=sorted(messages,key=lambda q:q[1]),blue=aqua[:3],
                tray=[(y,len(arr),float(np.median(np.array(arr)[:,2]-np.array(arr)[:,0]))) for y,arr in rows.items()])
result={}
for f in range(690,696):
    m=[parse(Image.open(r/f'{f:06d}.png').convert('RGB'),f) for r in (source,prev)]
    result[f]=m
    print(f,*m,sep='\n')
(root/'withdrawal-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
