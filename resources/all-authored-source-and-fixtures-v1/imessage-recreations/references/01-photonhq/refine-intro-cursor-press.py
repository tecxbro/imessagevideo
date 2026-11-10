from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy,hashlib
R=Path('/workspace/imessage-recreations');REF=R/'references/01-photonhq';P=R/'verification/fidelity-review/01-intro';AS=REF/'assets/intro-review';spec=json.loads((REF/'intro-review-elements.json').read_text());base=json.loads((REF/'scene-intro-base-v4.json').read_text());old=next(l for l in base['layers'] if l['id']=='group-8-source-cursor')
def image(n):
 p=P/'source-full-click'/f'{n-53:04d}.png' if n>=54 else P/'source-full-early-pill'/f'{n-41:04d}.png';return np.array(Image.open(p).convert('RGB'))
def boxes(n):
 a=image(n).astype(float);m=(a.max(2)-a.min(2)<12)&(a.mean(2)<88);lab,num=ndimage.label(m,np.ones((3,3)));out=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start;area=np.count_nonzero(lab[sl]==j)
  if w>15 and h>35 and area>300:out.append(([x.start,y.start,x.stop,y.stop],(lab[sl]==j).astype(float)))
 return out
cb,A=max(boxes(60),key=lambda q:q[1].sum());cw,ch=cb[2]-cb[0],cb[3]-cb[1];obs=[]
cy,cx=np.where(A>.5);points=np.column_stack([cx+cb[0]-1100,cy+cb[1]-535]);center=np.array([(cb[0]+cb[2])/2-1100,(cb[1]+cb[3])/2-535]);rotations=[]
for angle in range(-60,61):
 im=Image.fromarray(A.astype('float32'),'F').rotate(angle,resample=Image.Resampling.BICUBIC,expand=True);ar=np.asarray(im);yy,xx=np.where(ar>.5);cro=ar[yy.min():yy.max()+1,xx.min():xx.max()+1];theta=-np.deg2rad(angle);M=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]]);pp=(points-center)@M.T+center;lo=pp.min(0);size=pp.max(0)-lo+1;rotations.append((angle,cro,lo,size))
for n in range(45,86):
 best=None
 for b,B in boxes(n):
  w,h=b[2]-b[0],b[3]-b[1]
  for angle,RA,lo,size in rotations:
   pr=np.asarray(Image.fromarray(RA.astype('float32'),'F').resize((w,h),Image.Resampling.BILINEAR));score=float((pr*B).sum()/max(1e-9,np.sqrt((pr*pr).sum()*(B*B).sum())));sx,sy=w/size[0],h/size[1];mode='full'
   if best is None or score>best[0]:best=(score,b,sx,sy,mode,angle,lo)
 if best and best[0]>.88:
  score,b,sx,sy,mode,angle,lo=best;obs.append(dict(frame=n,sourceBounds=b,correlation=score,clip=mode,x=b[0]-lo[0]*sx,y=b[1]-lo[1]*sy,scaleX=sx,scaleY=sy,rotation=-angle,opacity=1))
# The first visible tip is clipped by both viewport edges. Its leadingedge is
# measured; the adjacent frame supplies only the unseen turn/scale.
first=obs[0]
for n in range(45,first['frame']):
 ar=image(n).astype(float);mask=(ar.max(2)-ar.min(2)<12)&(ar.mean(2)<88);yy,xx=np.where(mask)
 if len(xx)>30:
  b=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];angle=-first['rotation'];lo=next(q[2] for q in rotations if q[0]==angle);sx,sy=first['scaleX'],first['scaleY'];obs.insert(0,dict(frame=n,sourceBounds=b,correlation=None,inferredUnseenScaleAndTurnFrom=first['frame'],clip='viewport-clipped leading tip',x=b[0]-lo[0]*sx,y=b[1]-lo[1]*sy,scaleX=sx,scaleY=sy,rotation=first['rotation'],opacity=1))
obs.sort(key=lambda q:q['frame'])
def tk(v):return [dict(t=n/30,value=float(x),ease='linear') for n,x in v]
cursor=copy.deepcopy(old);cursor.update(x=0,y=0,scaleX=1,scaleY=1,start=obs[0]['frame']/30,end=(obs[-1]['frame']+1)/30,keyframes={k:tk([(q['frame'],q[k]) for q in obs]) for k in ['x','y','scaleX','scaleY','opacity']});cursor['children']=[dict(type='group',id='intro-cursor-rotation',originX=float(center[0]),originY=float(center[1]),keyframes={'rotation':tk([(q['frame'],q['rotation']) for q in obs])},children=copy.deepcopy(old['children']))];spec['replacements'][old['id']]=cursor;spec['measurements']['cursor']=obs
# Distinct pressed-state artwork: the source changes inset lighting while the
# measured camera scales the button. Cursor-occluded underlay is inferred by symmetry.
pill=copy.deepcopy(spec['replacements']['group-6-source-pill']);
if pill['type']=='group':
 normal=next(c for c in pill['children'] if c['id']=='intro-pill-normal');pill.update(type='image',src=normal['src'],width=normal['width'],height=normal['height']);pill.pop('children',None)
poses=spec['measurements']['pill'];pm={q['frame']:q for q in poses};q=pm[72];W,H=pill['width'],pill['height'];source72=image(72);a=source72.copy();bb=q['sourceBounds'];cx=(bb[0]+bb[2]-1)/2;cursor72=next(o['sourceBounds'] for o in obs if o['frame']==72)
for y in range(max(0,cursor72[1]-10),min(1080,cursor72[3]+10)):
 for x in range(max(0,cursor72[0]-10),min(1920,cursor72[2]+10)):
  mx=round(2*cx-x)
  if 0<=mx<1920:a[y,x]=source72[y,mx]
box=[max(0,int(np.floor(q['x']))-2),max(0,int(np.floor(q['y']))-2),min(1920,int(np.ceil(q['x']+W*q['scaleX']))+2),min(1080,int(np.ceil(q['y']+H*q['scaleY']))+2)];path=AS/'pill-pressed-72.png';Image.fromarray(a).crop(box).save(path);px=(box[0]-q['x'])/q['scaleX'];py=(box[1]-q['y'])/q['scaleY'];pw=(box[2]-box[0])/q['scaleX'];ph=(box[3]-box[1])/q['scaleY'];U=Image.open(pill['src']).convert('RGB');PI=Image.open(path).convert('RGB');weights=[]
for n in range(65,80):
 if n not in pm:continue
 v=pm[n];roi=[max(0,int(v['x'])),max(0,int(v['y'])),min(1920,int(np.ceil(v['x']+W*v['scaleX']))),min(1080,int(np.ceil(v['y']+H*v['scaleY'])))];rw,rh=roi[2]-roi[0],roi[3]-roi[1];sx,sy=v['scaleX'],v['scaleY'];uv=np.array(U.transform((rw,rh),Image.Transform.AFFINE,(1/sx,0,(roi[0]-v['x'])/sx,0,1/sy,(roi[1]-v['y'])/sy),Image.Resampling.BILINEAR,fillcolor='white')).astype(float);psx=sx*pw/PI.width;psy=sy*ph/PI.height;vx=v['x']+sx*px;vy=v['y']+sy*py;pv=np.array(PI.transform((rw,rh),Image.Transform.AFFINE,(1/psx,0,(roi[0]-vx)/psx,0,1/psy,(roi[1]-vy)/psy),Image.Resampling.BILINEAR,fillcolor='white')).astype(float);S=image(n)[roi[1]:roi[3],roi[0]:roi[2]].astype(float);m=(S[:,:,2]-S[:,:,0]>25);D=(pv-uv)[m];V=(S-uv)[m];val=float(np.clip((D*V).sum()/max(1,(D*D).sum()),0,1));weights.append((n,val))
normal=dict(type='image',id='intro-pill-normal',src=pill['src'],x=0,y=0,width=W,height=H);pressed=dict(type='image',id='intro-pill-pressed',src=str(path),x=px,y=py,width=pw,height=ph,keyframes={'opacity':tk([(45,0),(64,0)]+weights+[(80,0),(119,0)])});group={k:v for k,v in pill.items() if k not in ['src','width','height']};group['type']='group';group['children']=[normal,pressed];spec['replacements']['group-6-source-pill']=group;spec['assets'].append(dict(id='intro-pill-pressed',kind='bounded original pressed button graphic',sourceFrame=72,sourceBounds=box,asset=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reconstruction='Cursor-occluded underlay mirrored from the unobscured symmetric half. Native blend weight fitted against the visible blue surface.'));spec['measurements']['pill-press-weights']=[dict(frame=n,weight=w) for n,w in weights];latest=json.loads((REF/'intro-review-elements.json').read_text());latest['replacements']['group-8-source-cursor']=spec['replacements']['group-8-source-cursor'];latest['replacements']['group-6-source-pill']=spec['replacements']['group-6-source-pill'];latest['measurements']['cursor']=obs;latest['measurements']['pill-press-weights']=spec['measurements']['pill-press-weights'];latest['assets']=[a for a in latest['assets'] if a.get('id')!='intro-pill-pressed']+[a for a in spec['assets'] if a.get('id')=='intro-pill-pressed'][-1:];spec=latest;(REF/'intro-review-elements.json').write_text(json.dumps(spec,indent=2));(P/'cursor-press-measurements.json').write_text(json.dumps(dict(cursor=obs,weights=weights,pressedBounds=box),indent=2));print(json.dumps(dict(cursorFirst=obs[0]['frame'],cursorLast=obs[-1]['frame'],minCorrelation=min(o['correlation'] for o in obs if o['correlation'] is not None),weights=weights),indent=2))
