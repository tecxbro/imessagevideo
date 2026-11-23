from pathlib import Path
import json
import numpy as np
from phones import load,runs
p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text())
t=d['tracks']
reply=[]
for f,left,top,width,height in t['sofiaSuggestedBounds']:
    a=load('source',f)
    x0,x1=max(0,int((left+width*.17)/2)),min(500,round((left+width+25)/2))
    y0,y1=max(0,int((top-165)/2)),int(top/2-4)
    rgb=a[y0:y1,x0:x1]
    r,g,b=rgb.transpose(2,0,1)
    mask=(g-r>46)&(b-r>59)&(b>135)
    intervals=runs(mask.sum(1)>8)
    if not len(intervals):
        continue
    adequate=[(lo,hi) for lo,hi in intervals if hi-lo>=10]
    if not adequate:
        continue
    lo,hi=adequate[-1]
    _,xs=np.where(mask[lo:hi])
    u,v=np.percentile(xs,[1,99])
    reply.append([f,round(float(2*(x0+u)),2),int(2*(y0+lo)),round(float(2*(v-u)+4),2),int(2*(hi-lo))])
print('reply',reply)
t['sofiaEarlierReplyBounds']=reply
cal=[]
for f in range(397,411):
    r,g,b=load('source',f).transpose(2,0,1)
    y_min=int(np.interp(f,[397,401,405,410],[455,329,240,180]))
    c=(b-r>12)&(g-r>6)&(b>210)&(b-g>=0)
    c[:y_min]=False
    c[:,:31]=False
    c[:,448:]=False
    rows=np.where(c.sum(1)>45)[0]
    if not len(rows):
        continue
    xs=np.flatnonzero(c[rows].sum(0)>0.24*len(rows))
    if len(xs)<80:
        continue
    cal.append([f,2*int(xs[0]-1),2*int(xs[-1]+1),2*int(rows[0]),2*int(rows[-1])])
print('cal',cal)
offsets=[0,2,6,49,16,-19,-23,-34,-31,-32,-36,-31,-21,-8,0]
camera=t['calendarCamera']
coords=[np.interp(np.arange(397,412),*zip(*[(row[0],row[i]) for row in camera])) for i in (1,2,3)]
t['calendarCamera']=[[f,float(coords[0][i]),round(float(coords[1][i]+offsets[i]),2),float(coords[2][i])]
                     for i,f in enumerate(range(397,412))]+[row for row in camera if row[0]>411]
t['calendarColorEnvelope']=cal
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
