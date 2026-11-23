from pathlib import Path
import json
import numpy as np
from phones import load,runs
p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text()); t=d['tracks']
def at(track,f):
    a=np.array(t[track])
    return [np.interp(f,a[:,0],a[:,i]) for i in range(1,a.shape[1])]
suggestion=[]
for f in range(336,360):
    if f<353:
        x,y,s=at('sofiaMeasuredCamera',f)
    else:
        dx,y,s=at('sendGroup',f)
        x=500-200*s+dx
    expected=np.interp(f,[336,337,338,340,359],[383,393,411,433,433])
    a=load('source',f)
    x1,x2=max(0,round((x+153*s)/2)),min(500,round((x+380*s)/2))
    y1,y2=max(0,round((y+(expected-36)*s)/2)),min(500,round((y+(expected+74)*s)/2))
    rgb=a[y1:y2,x1:x2]
    r,g,b=rgb.transpose(2,0,1)
    mask=(g-r>48)&(b-r>58)&(b>143)
    boxes=runs(mask.sum(1)>max(7,round(16*s)))
    candidates=[(u,v) for u,v in boxes if (v-u)>12*s]
    if not candidates:
        continue
    u,v=candidates[-1]
    coords=np.argwhere(mask[u:v])
    if len(coords)<12:
        continue
    l_,r_=np.percentile(coords[:,1],[1,99])
    if (r_-l_)<31*s:
        continue
    box=[f,round(2*(x1+l_)-2,1),2*(y1+u),round(2*(r_-l_)+4,1),2*(v-u)]
    suggestion.append([round(float(q),2) if i else f for i,q in enumerate(box)])
print('suggestion',suggestion)
# Each word uses its own visible ink, rather than fitting a partial phrase into the final width.
words=[
 ('the',717,(148,200),(270,330)),('most',721,(197,249),(270,330)),
 ('personal',726,(247,347),(270,330)),('imessage',741,(126,226),(302,363)),
 ('assistant',749,(228,339),(302,363)),('yet',757,(339,375),(302,363))]
for name,enter,(x0,x1),(y0,y1) in words:
    ink=[]
    for f in range(enter,766):
        rgb=load('source',f)[y0:y1,x0:x1]
        aa=rgb.max(2)
        floor=min(193,int(np.percentile(aa,1)+30))
        if f<=enter+2: floor=223
        rows,cols=np.where(aa<floor)
        if len(cols)<10:
            continue
        xlo,xhi=np.percentile(cols,[.7,99.3])
        ylo,yhi=np.percentile(rows,[.6,99.4])
        darkness=np.percentile(aa[aa<floor],12)
        ink.append([f,round(2*(x0+xlo),2),round(2*(y0+ylo),2),round(2*(xhi-xlo+1),2),
                    round(2*(yhi-ylo+1),2),round(float(np.clip((252-darkness)/230,.10,1)),3)])
    if ink:
        print(name,ink[:4],ink[-1])
        t[f'closingInk-{name}']=ink
t['sofiaSuggestedBounds']=suggestion
# Recognizable objects have separate screen trajectories before the push.
for row in t['ellaProfileX']:
    if row[0] in (282,286):
        row[1]+=94
t['ellaRevealVeil']=[[282,0],[286,0],[288,.23],[290,.46],[295,.61],[300,.68],[305,.72],[312,.84]]
t['sofiaExposure']=[[313,114],[314,107],[315,93],[316,72],[317,51],[318,34],
                    [319,19],[320,11],[322,0]]
t['assistantMeasuredPosition'][0]=[134,42,267,912]
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
