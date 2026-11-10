"""Measured actual production glyph fits for connection rows and inbox reference."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from v8_utils import at
p=Path(__file__).parent;s=json.loads((p/'scene-v10-candidate.json').read_text());by={l['id']:l for l in s['layers']};fits=[]

def bbox(array,roi,tone):
    x,y,x2,y2=roi;c=array[y:y2,x:x2].astype(int)
    mask=c.max(2)<100 if tone=='black' else (c.min(2)>70)&(c.max(2)<210)&(c.max(2)-c.min(2)<20)
    yy,xx=np.where(mask)
    if not len(xx):raise ValueError('No glyph ink')
    return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)]

def record(group,node,frame,target,candidate):
    gx,gy,gsx,gsy=[at(group,k,frame/s['fps'])for k in['x','y','scaleX','scaleY']];sx=(target[2]-target[0])/(candidate[2]-candidate[0]);sy=(target[3]-target[1])/(candidate[3]-candidate[1]);nx=gx+node['x']*gsx;ny=gy+node['y']*gsy
    return dict(id=node['id'],source_bbox=target,candidate_bbox=candidate,x=(target[0]-(candidate[0]-nx)*sx-gx)/gsx,y=(target[1]-(candidate[1]-ny)*sy-gy)/gsy,scaleX=node.get('scaleX',1)*sx,scaleY=node.get('scaleY',1)*sy)
a=np.array(Image.open(p/'measurements-v8/decoded/001129.png').convert('RGB'));b=np.array(Image.open(p.parent.parent/'outputs/04-poke/v10-connect-medium/001129.png').convert('RGB'))
for name,y in [('p0468',157),('p0473',356),('p0478',555),('p0482',757)]:
    group=by[name];texts=[l for l in group['children']if l['type']=='text']
    for index,node in enumerate(texts):
        if name=='p0482':roi=(100,780,970,880);tone='black'
        else:roi=(110,y+13,y*0+580,y+88)if index==0 else(110,y+88,580,y+153);tone='black'if index==0 else'gray'
        target=bbox(a,roi,tone);candidate=bbox(b,roi,tone);fits.append(record(group,node,1129,target,candidate))
# Static header ref is fitted once, before measuring its separate source camera.
a=np.array(Image.open(p/'measurements-v8/decoded/000120.png').convert('RGB'));b=np.array(Image.open(p.parent.parent/'outputs/retained-frames/measured-frames-jRBOzF/000120.png').convert('RGB'));group=by['v8-inbox-header']
for identifier,roi in [('v8-Messages',(550,260,920,350)),('v8-Edit',(350,270,460,350))]:
    node=next(l for l in group['children']if l['id']==identifier);fits.append(record(group,node,120,bbox(a,roi,'black'),bbox(b,roi,'black')))
(p/'measurements-v8/connected-type-fit-v10.json').write_text(json.dumps({'method':'Actual production GSAPMedium font at native1129; source and candidate glyph spans measured separately per native title/domain. Headerstaticreference source120 fitted before independent camera registration.','measurements':fits},indent=2));print(fits)
