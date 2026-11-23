from pathlib import Path
import json,sys
import numpy as np
sys.path.insert(0,'sidehoe-recreation/tools')
from check_follow_contact import components
from phones import load
p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text()); t=d['tracks']
updates=[]
for i,(f,y,s) in enumerate(t['inboxIdentifiedRowPose']):
    if f<71:
        continue
    rgb=load('source',f)[:,75:133]
    r,g,b=rgb.transpose(2,0,1)
    mask=(b-r>40)&(g-r>22)&(b>105)
    rev={}
    for c in components(mask):
        if 22<=len(c)<140 and np.ptp(c[:,1])<=9 and np.ptp(c[:,0])<=11:
            center=(2*(c[:,1].mean()+75),2*c[:,0].mean())
            key=round(center[0]/4)
            rev.setdefault(key,[]).append(center)
    col=max(rev.values(),key=len) if rev else []
    if len(col)<4:
        continue
    x=float(np.median([a[0] for a in col]))
    scale=(500-x)/330
    ys=sorted([a[1] for a in col])
    valid=[ys[0]]
    for y0 in ys[1:]:
        if y0-valid[-1]>70:
            valid.append(y0)
    first=3 if f==101 else 4
    y=float(np.median([yc-(752+(first+j)*171)*scale for j,yc in enumerate(valid)]))
    t['inboxIdentifiedRowPose'][i]=[f,round(y,2),round(scale,4)]
    updates.append((f,x,y,scale))
rows=t['inboxIdentifiedRowPose']
for f in range(72,100):
    before,now,after=rows[f-43:f-40]
    expected=(before[1]+after[1])/2
    if abs(now[1]-expected)>65:
        now[1]=round(expected,2)
t['sofiaExposure']=[[313,114],[314,92],[315,66],[316,43],[317,27],[318,17],[319,9],
                    [320,4],[322,0]]
t['followExposure']=[[624,121],[625,92],[626,58],[627,38],[628,25],[629,15],[630,9],
                     [631,4],[633,0]]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(updates)
