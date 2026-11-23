from pathlib import Path
import json,sys
import numpy as np
from phones import load,runs
sys.path.insert(0,'sidehoe-recreation/tools')
from check_follow_contact import components

path=Path('sidehoe-skill-trial/repair/project/scene.json')
data=json.loads(path.read_text()); t=data['tracks']
def at(track,f):
    values=np.array(t[track])
    return [np.interp(f,values[:,0],values[:,i]) for i in range(1,values.shape[1])]
pointers=[]
for f in range(662,674):
    x,y,_=at('followCursor',f)
    cp=load('source',f)
    x0,x1=round((x-90)/2),round((x+100)/2)
    y0,y1=round((y-101)/2),round((y+45)/2)
    rgb=cp[y0:y1,x0:x1]
    mask=rgb.max(2)<119
    results=[]
    for c in components(mask):
        if len(c)<10 or len(c)>280:
            continue
        rows,columns=c.T
        l,r=int(columns.min()),int(columns.max())
        u,b=int(rows.min()),int(rows.max())
        if not (4<=r-l<=24 and 2<=b-u<=27):
            continue
        cx,cy=2*(l+x0),2*(u+y0)
        merit=abs(cx-x)*.30+abs(cy-(y-18))*.56- min(10,len(c)*.06)
        results.append((round(merit,2),cx,cy,len(c),r-l,b-u))
    print(f,(round(x),round(y)),sorted(results)[:3])
    if results:
        _,cx,cy,_,_,_=min(results)
        pointers.append([f,cx+1,cy+1])
if len(pointers)>=8:
    t['followApproachPointer']=pointers

print('follow bubble structures')
for f in [632,640,647,650,667,675,687,690,691,692,693,694,695]:
    x,y,s=at('followMeasuredCamera',f)
    rgb=load('source',f)
    x0,x1=max(0,round((x+125*s)/2)),min(500,round((x+385*s)/2))
    y0,y1=max(0,round((y+138*s)/2)),min(500,round((y+260*s)/2))
    r,g,b=rgb[y0:y1,x0:x1].transpose(2,0,1)
    mask=(g-r>10)&(b-r>13)&(b>214)&(r>140)
    possible=runs(mask.sum(1)>max(12,round(24*s)))
    if len(possible):
        u,v=max(possible,key=lambda x:x[1]-x[0])
        yy,xx=np.where(mask[u:v])
        ll,rr=np.percentile(xx,[1,99])
        tint=np.median(np.stack([r,g,b],axis=2)[u:v][mask[u:v]],axis=0).astype(int)
        print(f,[round(2*(x0+ll)),2*(y0+u),round(2*(rr-ll)),2*(v-u)],tint)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
