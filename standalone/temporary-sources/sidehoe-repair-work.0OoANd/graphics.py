from pathlib import Path
import json
import numpy as np
from phones import load,track,runs

def badge_bounds(f, key):
    rgb=load('source',f)
    y_est=track(key+'Y',f)[0]/2
    width=track(key+'Size',f)[0]/2
    lower=max(0,round(y_est-width*.75))
    upper=min(500,round(y_est+width*.72))
    region=rgb[lower:upper,130:370]
    black=region.max(2)<105
    rows=runs(black.sum(1)>max(8,width*.12))
    if not len(rows):return
    i,j=max(rows,key=lambda p:p[1]-p[0])
    if j-i < width*.45:return
    section=black[i:j]
    cols=np.flatnonzero(section.sum(0)>max(5,(j-i)*.14))
    if not len(cols):return
    return [f,round(float((130+(cols[0]+cols[-1]+1)/2)*2),1),int((lower+(i+j)/2)*2),
            int(2*(cols[-1]-cols[0]+2)),int(2*(j-i+2))]

def scroll(f):
    rgb=load('source',f)
    red,g,b=rgb[:,57:112].transpose(2,0,1)
    cyan=(b-red>58)&(g-red>41)&(b>115)
    rows=np.flatnonzero(cyan.sum(1)>=2)
    if not len(rows):return None
    chunks=np.split(rows,np.where(np.diff(rows)>2)[0]+1)
    centers=[c.mean()*2 for c in chunks if len(c)>1 and 17<c.mean()<475]
    y0,=track('inboxY',f)
    scale,=track('inboxScale',f)
    proposed=np.array([y0+(752+i*171)*scale for i in range(11)])
    matches=[]
    for desired in centers:
        i=np.argmin(abs(proposed-desired))
        if abs(proposed[i]-desired)<67:
            matches.append(desired-proposed[i])
    if len(matches)<2:return None
    delta=np.median(matches)
    if np.median(abs(np.array(matches)-delta))>22:return None
    return round(float(y0+delta),2)

def text_bounds(key,f,anchors,j):
    rgb=load('source',f)
    y=float(np.interp(f,[a[0] for a in anchors],[a[1+j] for a in anchors]))/2
    n=32 if key=='personal' else 21
    p,q=max(0, int(y)-n),min(500,int(y)+n)
    part=rgb[p:q,78:422]
    dark=(part.max(2)<160)
    rows=runs((dark.sum(1)>4))
    if not len(rows):return 
    lo,hi=min(rows,key=lambda t:abs((t[0]+t[1])*.5+p-y)+(0 if t[1]-t[0]>10 else 15))
    if hi-lo<9: return
    yy,xx=np.where(dark[lo:hi])
    x0,x1=78+xx.min(),78+xx.max()+1
    if x1-x0<65:return
    return [f,int(x0*2),int((p+lo)*2),int((x1-x0)*2),int((hi-lo)*2)]

p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text())
t=d['tracks']
for key,frames in [('identity',range(105,134)),('closing',range(696,766))]:
    values=[z for f in frames if (z:=badge_bounds(f,key))]
    t[key+'MeasuredBox']=values
    print(key, values[0],values[-1])
reference_scroll=[[f,v] for f in range(42,102) if (v:=scroll(f)) is not None]
print('Scroll measurements',len(reference_scroll),reference_scroll[:3],reference_scroll[-3:])
t['inboxMeasuredScroll']=reference_scroll
# Expected optical centers provide text search windows, not rendering inputs.
personal=[[162,444,0],[178,455,552],[190,472,570],[201,420,518],[208,356,440],[212,127,224]]
closing=[[730,616,682],[765,619,684]]
for key,seed,ranges in [('personal',personal,[range(168,213),range(184,213)]),('closing',closing,[range(730,766),range(753,766)])]:
    for j,frames in enumerate(ranges):
        values=[v for f in frames if (v:=text_bounds(key,f,seed,j))]
        print(key,j,values[0],values[-1])
        t[f'{key}Line{j+1}']=values
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
