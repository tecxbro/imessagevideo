"""Add actual early Muse portrait/typing birth; preserve every630+ layer state."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
R=Path('/workspace/imessage-recreations/references/02-danieltian');P=R/'header-formation-prototype.json';p=json.loads(P.read_text());base=json.loads((R/'scene-final-v11.json').read_text());N={n['id']:n for n in base['layers']};g=copy.deepcopy(N['group-1118']);C={n['id']:n for n in g['children']};records=[]
def ar(n):
 path=R/'assets/header-formation-measure'/f'frame-{n:04d}.png'
 if n==630:path=R/'assets/middle-every-frame/source-0630.png'
 return np.array(Image.open(path).convert('RGB')).astype(float)
def bbox(a,kind):
 if kind=='avatar':l,r,t,b=200,400,400,1080;lo,hi,spread=170,246,18
 else:l,r,t,b=390,760,350,1080;lo,hi,spread=190,246,16
 reg=a[t:b,l:r];mask=(reg.min(2)>lo)&(reg.max(2)<hi)&(reg.max(2)-reg.min(2)<spread);mask=ndimage.binary_closing(mask,iterations=2);lab,num=ndimage.label(mask,np.ones((3,3)));out=[]
 for sl in ndimage.find_objects(lab):
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  ok=(w>55 and h>45 and .65<w/h<1.6) if kind=='avatar' else(w>80 and h>35 and 1.2<w/h<3.6)
  if ok:out.append([xx.start+l,yy.start+t,xx.stop+l,yy.stop+t])
 return max(out,key=lambda b:(b[2]-b[0])*(b[3]-b[1])) if out else None
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
def state(n,k,t):return sample(n.get('keyframes',{}).get(k,[dict(t=0,value=n.get(k,1 if k.startswith('scale') or k=='opacity' else 0))]),t)
def update(node,rows):
 if not rows:return
 node['start']=min(node['start'],rows[0]['n']/30)
 for k in ['x','y','scaleX','scaleY','opacity']:
  old=node.get('keyframes',{}).get(k,[]);old=[q for q in old if q['t']>=21]
  if not old:old=[dict(t=21,value=state(node,k,21))]
  node.setdefault('keyframes',{})[k]=[dict(t=q['n']/30,value=q[k]) for q in rows]+old
for kind,id in [('avatar','middle-avatar-muse'),('typing','middle-muse-typing')]:
 node=C[id];ref=bbox(ar(630),kind)
 if not ref:raise ValueError('No canonical source630 '+kind)
 refPose={k:state(node,k,21) for k in ['x','y','scaleX','scaleY']};rows=[]
 def observed(n,b):
  a=ar(n)[b[1]:b[3],b[0]:b[2]]
  if kind=='avatar':return float(np.quantile(a.max(2)-a.min(2),.995))
  mm=(a.min(2)>190)&(a.max(2)<247)&(a.max(2)-a.min(2)<18);v,c=np.unique(a[mm].astype('uint8'),axis=0,return_counts=True);return float(253-v[c.argmax()].mean())
 refStrength=observed(630,ref)
 for n in range(620,630):
  b=bbox(ar(n),kind)
  if not b:continue
  sx=(b[2]-b[0])/(ref[2]-ref[0]);sy=(b[3]-b[1])/(ref[3]-ref[1]);rows.append(dict(n=n,x=b[0]-(ref[0]-refPose['x'])*sx,y=b[1]-(ref[1]-refPose['y'])*sy,scaleX=refPose['scaleX']*sx,scaleY=refPose['scaleY']*sy,opacity=float(np.clip(observed(n,b)/max(1,refStrength),0,1))))
 update(node,rows);records.append(dict(kind=kind,referenceBounds=ref,measurements=rows))
 if kind=='typing' and rows:
  label=C['middle-muse-typing-label']
  def caption(n):
   a=ar(n)[350:1000,400:650];m=(a.max(2)<100)&(a.max(2)-a.min(2)<20)
   if m.sum()<10:m=(a.max(2)<220)&(a.max(2)-a.min(2)<20)
   row=ndimage.binary_closing(m.sum(1)>2,iterations=2);lab,num=ndimage.label(row);runs=[sl[0] for sl in ndimage.find_objects(lab) if sl[0].stop-sl[0].start>4]
   if not runs:return None
   q=runs[0];mm=m.copy();mm[:q.start]=False;mm[q.stop:]=False;yy,xx=np.where(mm);b=[int(xx.min()+400),int(yy.min()+350),int(xx.max()+401),int(yy.max()+351)];opacity=float(np.clip((253-np.quantile(a[mm].mean(1),.1))/253,0,1));return b,opacity
  rb,_=caption(630);lr=[]
  for n in range(620,630):
   q=caption(n)
   if not q:continue
   b,opacity=q;sx=(b[2]-b[0])/(rb[2]-rb[0]);sy=(b[3]-b[1])/(rb[3]-rb[1]);lr.append(dict(n=n,x=b[0]-rb[0]*sx,y=b[1]-rb[1]*sy,scaleX=sx,scaleY=sy,opacity=opacity))
  update(label,lr)
p['replacements']['group-1118']=g;p['provenance'].append(dict(kind='Measured Muse portrait and typing before630',diagnosis='Source622+ already shows the incoming Muse portrait/capsule. Earlier lifetime21.0 omitted it; the header prototype must not accidentally trace the unrelated Muse sender into its own title mask.',records=records));P.write_text(json.dumps(p,indent=2));base['layers']=[copy.deepcopy(p['replacements'].get(n['id'],n)) for n in base['layers']];(R/'scene-header-formation-prototype.json').write_text(json.dumps(base,indent=2));print('Added early Muse source poses',records,flush=True)
