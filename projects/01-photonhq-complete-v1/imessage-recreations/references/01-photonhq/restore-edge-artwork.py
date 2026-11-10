from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,pickle
R=Path('/workspace/imessage-recreations/references/01-photonhq');M=R/'assets/wall-art/measure';A=R/'assets/wall-edge';A.mkdir(exist_ok=True);scene=json.loads((R/'scene-wall-v4.json').read_text());cc=pickle.loads((R/'assets/wall-art/colored-components-thin-local.pkl').read_bytes());ledger=json.loads((R/'wall-ocr-provenance.json').read_text());info={q['id']:q for q in ledger};nodes=[l for l in scene['layers'] if l['id'] in info];phases=[('sms',270,8.2,9.5),('emails',300,9.5,10.666667),('calls',336,10.666667,11.666667),('imessage',372,11.666667,12.966667),('whatsapp',408,12.966667,14.2),('telegram',444,14.2,15.5)];new=[];provenance=[]
def sample(l,p,t):
 tr=l.get('keyframes',{}).get(p)
 if not tr:return l.get(p,1 if p.startswith('scale') or p=='opacity' else 0)
 tr=sorted(tr,key=lambda q:q['t'])
 if t<=tr[0]['t']:return tr[0]['value']
 for a,b in zip(tr,tr[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']) if b['t']!=a['t'] else 0;return a['value']+(b['value']-a['value'])*f
 return tr[-1]['value']
def box(l,t):
 x,y=sample(l,'x',t),sample(l,'y',t);return(x,y,x+l['width']*sample(l,'scaleX',t),y+l['height']*sample(l,'scaleY',t))
def iou(a,b):
 x=max(0,min(a[2],b[2])-max(a[0],b[0]));y=max(0,min(a[3],b[3])-max(a[1],b[1]));v=x*y;return v/max(1,(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-v)
for phase,base,start,end in phases:
 t0=base/30;pn=[l for l in nodes if info[l['id']]['phase']==phase];active=[l for l in pn if l.get('start',0)<=t0<l.get('end',100)];bb=[box(l,t0) for l in active]
 for ci,co in enumerate(cc[base]):
  cls=co['class'];b=co['box']
  if cls not in [phase,'gray']:continue
  if phase=='emails':
   if not(cls=='gray' and co['area']/(co['w']*co['h'])<.25 and co['w']/co['h']>2.8):continue
  elif co['area']/(co['w']*co['h'])<.25:continue
  if not(b[0]<4 or b[2]>1916 or b[1]<4 or b[3]>1076):continue
  if any(iou(b,a)>.55 for a in bb):continue
  im=Image.open(M/f'{base:04d}.png').convert('RGBA');tile=im.crop(b);filename=f'{phase}-{ci}.png';tile.save(A/filename);ms=[]
  for n,objects in cc.items():
   t=n/30
   if not(start-.2<=t<=end+.2):continue
   states=[]
   for l in active:
    if not(l['start']<=t<l['end']):continue
    q0=box(l,t0);q1=box(l,t);sx=(q1[2]-q1[0])/(q0[2]-q0[0]);states.append((sx,q1[0]-q0[0]*sx,(q1[1]+q1[3])/2-(q0[1]+q0[3])/2*sx))
   sx,tx,ty=np.median(states,axis=0) if states else(1,0,0);expected_cy=(b[1]+b[3])/2*sx+ty;expected_cx=(b[0]+b[2])/2*sx+tx;candidates=[]
   for q in objects:
    if q['class']!=cls and not(cls=='calls' and q['class']=='gray'):continue
    if cls=='calls' and q['class']=='gray' and q['area']/(q['w']*q['h'])<.5:continue
    qb=q['box']
    if b[0]<4 and qb[0]>4:continue
    if b[2]>1916 and qb[2]<1916:continue
    if b[1]<4 and qb[1]>4:continue
    if b[3]>1076 and qb[3]<1076:continue
    dy=abs((qb[1]+qb[3])/2-expected_cy)
    dx=abs((qb[0]+qb[2])/2-expected_cx)
    if dy>100 or dx>max(180,co['w']*.6):continue
    candidates.append((dy+dx*.3,q))
   if n==base:q=co
   elif not candidates:continue
   else:_,q=min(candidates,key=lambda z:z[0])
   qb=q['box'];sy=q['h']/co['h'];x=qb[2]-co['w']*sx if b[0]<4 else qb[0];y=qb[1];alpha=1
   if cls=='calls':
    reg=np.asarray(Image.open(M/f'{n:04d}.png').convert('RGB'))[qb[1]:qb[3],qb[0]:qb[2]];alpha=1 if n==base else float(np.clip((255-np.quantile(reg.mean(2),.01))/255,.05,1))
   ms.append(dict(t=t,x=float(x),y=float(y),scaleX=float(sx),scaleY=float(sy),opacity=alpha,sourceBounds=list(qb)))
  if not any(abs(m['t']-t0)<.001 for m in ms):ms.append(dict(t=t0,x=b[0],y=b[1],scaleX=1,scaleY=1,opacity=1,sourceBounds=list(b)))
  ms.sort(key=lambda m:m['t']);left=max(start-.2,ms[0]['t']-.04);right=min(end+.2,ms[-1]['t']+.04);tracks={p:[dict(t=m['t'],value=m[p]) for m in ms] for p in ['x','y','scaleX','scaleY']};opacity=[dict(t=left,value=0)]+[dict(t=m['t'],value=m['opacity']) for m in ms]+[dict(t=right,value=0)]
  img=dict(id=f'edge-art-{phase}-{ci}',type='image',src='assets/wall-edge/'+filename,width=co['w'],height=co['h'],x=b[0],y=b[1],keyframes=tracks,sourceFrame=base,sourceBounds=list(b),semanticText='Edge-clipped original '+phase+' UI artwork')
  children=[]
  if cls=='calls':
   # Restore only the black material behind portions that are edge-clipped and therefore never OCR-readable.
   fullwidth=float(np.median([l['width']*sample(l,'scaleX',t0) for l in active if box(l,t0)[0]>4 and box(l,t0)[2]<1916])) if active else 800;fullwidth=max(fullwidth,co['w']*1.1);rt={p:[] for p in ['x','y','width','height','radius']}
   for m in ms:
    qb=m['sourceBounds'];w=fullwidth*m['scaleX'];h=max(1,qb[3]-qb[1]-4);xx=qb[2]-2-w if b[0]<4 else qb[0]+2
    for p,v in [('x',xx),('y',qb[1]+2),('width',w),('height',h),('radius',h/2)]:rt[p].append(dict(t=m['t'],value=v))
   children.append(dict(id=f'edge-material-{phase}-{ci}',type='rect',fill='#000000',width=fullwidth,height=co['h'],radius=co['h']/2,keyframes=rt))
  children.append(img);new.append(dict(id=f'edge-restore-{phase}-{ci}',type='group',start=left,end=right,children=children,keyframes={'opacity':opacity},editability='Native clipped material plus isolated original edge artwork, measured source bounds; no full-frame assets.'));provenance.append(dict(id=new[-1]['id'],phase=phase,sourceFrame=base,sourceBounds=list(b),observations=ms,asset=img['src']))
scene['layers']=new+[l for l in scene['layers'] if not l['id'].startswith('edge-restore-')];(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));(R/'edge-artwork-provenance.json').write_text(json.dumps(provenance,indent=2));print('Restored original clipped edge elements',len(new))
