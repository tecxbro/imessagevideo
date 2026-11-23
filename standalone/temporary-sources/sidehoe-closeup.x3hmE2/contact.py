from collections import deque
import csv
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

first,last=673,690
left,top,width,height=660,970,460,338
def decode(path):
    output=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(path),
        '-an','-vf',f"select=between(n\\,{first}\\,{last}),crop={width}:{height}:{left}:{top},format=rgb24",
        '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    return np.frombuffer(output,dtype=np.uint8).reshape(last-first+1,height,width,3)

def bounds(image,f):
    v=image.astype(np.int16)
    mask=(v[:,:,2]-v[:,:,0]>15)&(v[:,:,2]>226)&(v[:,:,1]>145)&(v[:,:,0]>155)
    mask[:20,:]=mask[180:,:]=False
    mask[:,:20]=mask[:,380:]=False
    cy,cx=np.where(mask)
    # Outer coded chip extent remains visible left of the emoji and cursor.
    lows,highs=np.where(mask[:,117:205])[0].min(),np.where(mask[:,117:205])[0].max()
    chip=(left+int(cx.min()),top+int(lows),left+int(cx.max()),top+int(highs))

    x0=897-left
    ink=(v[71:,x0:408].max(axis=-1)<71)
    y,x=np.where(ink)
    remaining={(int(a),int(b)) for a,b in zip(y,x,strict=True)}
    groups=[]
    while remaining:
        point=remaining.pop()
        connected=[point]
        queue=deque([point])
        while queue:
            y,x=queue.pop()
            for test in ((y+1,x),(y-1,x),(y,x-1),(y,x+1)):
                if test in remaining:
                    remaining.remove(test)
                    connected.append(test)
                    queue.append(test)
        groups.append(connected)
    sprite=max(groups,key=len)
    assert len(sprite)>450,(f,len(sprite))
    ty=min(y for y,x in sprite)
    xs=[x for y,x in sprite if y==ty]
    tip=(xs[len(xs)//2]+left+x0,ty+top+71)
    gap=max(0,tip[1]-chip[3],tip[0]-chip[2],chip[0]-tip[0])
    return chip,tip,gap

source,candidate,out=map(Path,sys.argv[1:])
with out.open('w',newline='') as h:
    writer=csv.writer(h)
    writer.writerow(['version','frame','seconds','chip left','chip top','chip right','chip bottom','cursor tip x','cursor tip y','gap pixels'])
    mask_contact={}
    for name,movie in [('Source',source),('Revised',candidate)]:
        touch=[]
        for f,image in enumerate(decode(movie),first):
            chip,tip,gap=bounds(image,f)
            writer.writerow([name,f,f/25,*chip,*tip,gap])
            if gap==0: touch.append(f)
            if f in (673,674,675,676,681,690):
                print(name,f,chip,tip,gap,flush=True)
        mask_contact[name]=touch[0]
events=json.loads((candidate.parent/'sound/events.json').read_text())
cue=next(c for c in events['cues'] if c['eventId']=='follow.yes-contact')
assert cue['frame']==675 and cue['sample']==1296000,cue
assert mask_contact=={'Source':675,'Revised':675},mask_contact
print(mask_contact,'cue',cue['sample'])
