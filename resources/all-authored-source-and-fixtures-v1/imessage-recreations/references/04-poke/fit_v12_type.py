"""Fit actual browser glyph bounds after independently ranked native font changes."""
from pathlib import Path
from PIL import Image
import json,numpy as np,hashlib,math
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;scene=json.loads((p/'scene-v12-font-prototype-01.json').read_text());by={g['id']:g for g in scene['layers']};fps=scene['fps'];output=[]
def bbox(file,roi,kind):
    a=np.array(Image.open(file).convert('RGB')).astype(int);x0,y0,x1,y1=roi;c=a[y0:y1,x0:x1]
    mask=c.max(2)<100 if kind=='black'else(c.min(2)>75)&(c.max(2)<215)&(c.max(2)-c.min(2)<12)
    yy,xx=np.where(mask)
    if not len(xx):raise ValueError((file,roi,kind))
    return [int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)]
def fit(group,node,n,srcroi,candroi,kind):
    a=bbox(p/f'measurements-v8/decoded/{n:06}.png',srcroi,kind);candidate=root/f'outputs/04-poke/v12-font-diagnostic-01/{n:06}.png';b=bbox(candidate,candroi,kind);t=n/fps;gx,gy,sx,sy=[at(group,k,t)for k in['x','y','scaleX','scaleY']];rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);nx=gx+node['x']*sx;ny=gy+node['y']*sy
    if not(.85<rx<1.16 and .85<ry<1.16):raise ValueError(('Unisolated or censored glyph ROI',node['id'],a,b,rx,ry))
    output.append(dict(id=node['id'],frame=n,text=node['text'],source_ink=a,candidate_ink=b,x=(a[0]-(b[0]-nx)*rx-gx)/sx,y=(a[1]-(b[1]-ny)*ry-gy)/sy,scaleX=node.get('scaleX',1)*rx,scaleY=node.get('scaleY',1)*ry,candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest()))
inbox=by['v8-inbox-rows'];items={l['id']:l for l in inbox['children']}
for id,srcroi,candroi,kind in[
 ('v8-Nikki',[440,670,735,725],[400,670,900,725],'black'),
 ('v8-NikkiSub',[440,728,980,800],[400,728,1300,810],'gray'),
 ('v8-NikkiTime',[900,670,1080,730],[900,670,1250,730],'gray'),
 ('v8-Jony',[440,870,700,930],[400,870,900,930],'black'),
 ('v8-JonySub',[440,925,1100,1040],[400,925,1300,1040],'gray'),
 ('v8-JonyTime',[900,870,1080,930],[900,870,1250,930],'gray')]:fit(inbox,items[id],120,srcroi,candroi,kind)
for id,n in[('p0430',925),('p0436',988),('p0442',988),('p0448',988),('p0454',988),('p0460',1054)]:
    g=by[id];gx,gy,sx,sy=[at(g,k,n/fps)for k in['x','y','scaleX','scaleY']]
    for node in g['children']:
        if node['type']!='text':continue
        y=node['y'];roi=[max(0,math.floor(gx+20*sx)),max(0,math.floor(gy+(y-3)*sy)),min(1440,math.ceil(gx+820*sx)),min(1080,math.ceil(gy+(y+47)*sy))];fit(g,node,n,roi,roi,'black'if node.get('fontWeight')==600 else'gray')
(p/'measurements-v8/type-browser-fit-v12.json').write_text(json.dumps(dict(method='Actual GSAP text-only diagnostic removes overlapping photo/emoji/chrome contamination. Font choices independently ranked against original alpha shapes. Per-text numeric fit uses original native ink boxes; no source UI bitmap is output.',sceneSHA256=hashlib.sha256((p/'scene-v12-font-prototype-01.json').read_bytes()).hexdigest(),measurements=output),indent=2));print(json.dumps(output,indent=2))
