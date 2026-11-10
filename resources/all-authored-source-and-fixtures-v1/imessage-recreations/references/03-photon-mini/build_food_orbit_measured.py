"""Native measured food/order transforms for source730–799 only.
Keeps UI/phone/backplane roots untouched; no reference frame playback.
"""
from pathlib import Path
from PIL import Image
from scipy.optimize import linear_sum_assignment
import json,copy,numpy as np,math
R=Path(__file__).resolve().parent;D=R/'food-orbit-measure';scene=json.loads((R/'final-v13.scene.json').read_text());roots={n['id']:n for n in scene['layers']};food=json.loads((D/'food-refined-measurements.json').read_text());words=json.loads((D/'order-body-measurements.json').read_text());cal=json.loads((D/'native-order-metrics.json').read_text());orderIDs=['p03-220','p03-224','p03-228','food-tail-top-order','food-tail-right-order'];foodIDs=[id for id in roots if id.startswith(('authentic-food-','food-tail-extra-'))];replacements={};ledger=[]
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);e=b.get('ease','linear')
   if e=='easeOut':f=1-(1-f)**3
   if e=='easeIn':f=f**3
   return a['value']+(b['value']-a['value'])*f
 return ks[-1]['value']
def state(n,k,t):return sample(n.get('keyframes',{}).get(k,[dict(t=0,value=n.get(k,1 if k.startswith('scale') or k=='opacity' else 0))]),t)
def anchor(id,n):
 q=roots[id];t=max(24.5,n/30);x,y=state(q,'x',t),state(q,'y',t)
 if id in orderIDs:w,h=cal[id]['rect']
 else:w,h=q['width'],q['height']
 return np.array([x+w*state(q,'scaleX',t)/2,y+h*state(q,'scaleY',t)/2])
def assign(ids,observed,kind):
 tracks={id:{} for id in ids};last={};velocity={}
 for n in range(730,800):
  obs=observed.get(str(n),[]);obs=obs[:len(ids)]
  if not obs:continue
  cost=np.zeros((len(ids),len(obs)))
  for i,id in enumerate(ids):
   if id in last and n-last[id][0]<=3:pred=last[id][1]+velocity.get(id,np.zeros(2))*(n-last[id][0])
   else:pred=anchor(id,n)
   for j,o in enumerate(obs):cost[i,j]=np.linalg.norm(pred-np.array(o['center']))
  ii,jj=linear_sum_assignment(cost)
  for i,j in zip(ii,jj):
   id=ids[i];o=copy.deepcopy(obs[j]);c=np.array(o['center']);tracks[id][n]=o
   if id in last:
    dt=n-last[id][0];v=(c-last[id][1])/dt;velocity[id]=v if dt>3 else .5*velocity.get(id,v)+.5*v
   last[id]=(n,c)
 # Fill only short, coherent missing measurements. Big objects crossing the phone remain hidden rather than being invented above the UI.
 for id,ts in tracks.items():
  nums=sorted(ts)
  for a,b in zip(nums,nums[1:]):
   if b-a<2 or b-a>4:continue
   ca=np.array(ts[a]['center']);cb=np.array(ts[b]['center'])
   if np.linalg.norm(cb-ca)/(b-a)>120:continue
   for n in range(a+1,b):
    f=(n-a)/(b-a);o={};c=ca+(cb-ca)*f
    if kind=='food':
     A=np.array(ts[a]['matrix']);B=np.array(ts[b]['matrix']);M=A+(B-A)*f;corn=np.array(ts[a]['corners'])+(np.array(ts[b]['corners'])-np.array(ts[a]['corners']))*f;size=np.ptp(corn,axis=0);lo=corn.min(0);hi=corn.max(0);phone=not(hi[0]<620 or lo[0]>1260 or hi[1]<20 or lo[1]>1080)
     if phone and np.prod(size)>2500:continue
     o={**ts[a],'matrix':M.tolist(),'corners':corn.tolist(),'center':c.tolist(),'opacity':ts[a]['opacity']+(ts[b]['opacity']-ts[a]['opacity'])*f,'interpolatedGap':True}
    else:
     bb=np.array(ts[a]['bbox'])+(np.array(ts[b]['bbox'])-np.array(ts[a]['bbox']))*f;o={**ts[a],'bbox':bb.tolist(),'center':c.tolist(),'opacity':ts[a]['opacity']+(ts[b]['opacity']-ts[a]['opacity'])*f,'interpolatedGap':True}
    ts[n]=o
 return tracks
byKind={'pizza':{},'ramen':{}}
for ns,models in food.items():
 for k in byKind:byKind[k][ns]=[m for m in models if m['kind']==k]
for kind in byKind:
 ids=[id for id in foodIDs if ('ramen' in id)==(kind=='ramen')];tracks=assign(ids,byKind[kind],'food');asset=R/'assets'/('apple-pizza.png' if kind=='pizza' else 'apple-ramen.png');W,H=Image.open(asset).size
 for id,ts in tracks.items():
  if not ts:raise ValueError('No measurements for '+id)
  first=ts[min(ts)];previous=None;rows=[]
  for n in range(730,800):
   o=ts.get(n,first);M=np.array(o['matrix']);U,sv,V=np.linalg.svd(M[:,:2])
   if np.linalg.det(U)<0:U[:,1]*=-1;sv[1]*=-1
   if np.linalg.det(V)<0:V[1,:]*=-1;sv[1]*=-1
   tu=math.degrees(math.atan2(U[1,0],U[0,0]));tv=math.degrees(math.atan2(V[1,0],V[0,0]));choices=[]
   for swap in [False,True]:
    aa,bb=(tu,tv) if not swap else(tu+90,tv-90);ss=sv if not swap else sv[::-1]
    for k in range(-3,4):
     a,b=aa+180*k,bb-180*k;penalty=abs(a)+abs(b) if previous is None else abs(a-previous[0])+abs(b-previous[1]);choices.append((penalty,a,b,ss))
   _,u,v,sigma=min(choices,key=lambda q:q[0]);previous=(u,v);center=M@np.array([W/2,H/2,1]);rows.append(dict(n=n,x=float(center[0]),y=float(center[1]),rotation=float(u),scaleX=float(sigma[0]),scaleY=float(sigma[1]),innerRotation=float(v),opacity=float(o['opacity']) if n in ts else 0))
  child=dict(id='food14-art-'+id,type='image',src=str(asset),x=-W/2,y=-H/2,width=W,height=H,editability='Authentic bounded original Apple artwork; native affine pose, not a source frame.');inner=dict(id='food14-affine-inner-'+id,type='group',children=[child],keyframes={'rotation':[dict(t=q['n']/30,value=q['innerRotation']) for q in rows]});node=dict(id=id,type='group',children=[inner],start=730/30,end=800/30,keyframes={k:[dict(t=q['n']/30,value=q[k]) for q in rows] for k in ['x','y','rotation','scaleX','scaleY','opacity']},editability='Two native rotations plus nonuniform scale reproduce the measured2D affine projection. Internal original food artwork is bitmap.');replacements[id]=node;ledger.append(dict(id=id,kind=kind,observedFrames=sorted(n for n,o in ts.items() if not o.get('interpolatedGap')),interpolatedFrames=sorted(n for n,o in ts.items() if o.get('interpolatedGap')),measurements=rows))
# Independent short-word glyph bounds determine the actual projected Order! pose.
wordObs={}
for ns,items in words.items():
 n=int(ns);a=np.array(Image.open(R/'lunch-native'/f'{n-609:03d}.png').convert('RGB')).astype(float);oo=[]
 for q in items:
  l,t,r,b=map(int,q['bbox']);roi=a[t:b,l:r];neutral=roi.max(2)-roi.min(2)<20;v=roi.mean(2)[neutral];alpha=float(np.clip((253-np.quantile(v,.08))/253,0,1)) if len(v) else 1;oo.append({**q,'center':[(l+r)/2,(t+b)/2],'opacity':alpha})
 wordObs[ns]=oo
tracks=assign(orderIDs,wordObs,'order')
for id,ts in tracks.items():
 if not ts:raise ValueError('No Order measurements '+id)
 node=copy.deepcopy(roots[id]);bb=cal[id]['bbox'];gw,gh=bb[2]-bb[0],bb[3]-bb[1];first=ts[min(ts)];rows=[]
 for n in range(730,800):
  q=ts.get(n,first);l,t,r,b=q['bbox'];w,h=r-l,b-t;angle=q.get('rotation',0)
  if h<12 or abs(angle)>5:angle=0
  rad=math.radians(angle);c,ss=abs(math.cos(rad)),abs(math.sin(rad));den=c*c-ss*ss;sx=(c*w-ss*h)/den/gw;sy=(c*h-ss*w)/den/gh
  if sx<=0 or sy<=0:sx=w/gw;sy=h/gh;angle=0;rad=0
  mat=np.array([[math.cos(rad)*sx,-math.sin(rad)*sy],[math.sin(rad)*sx,math.cos(rad)*sy]]);corn=np.array([[bb[0],bb[1]],[bb[2],bb[1]],[bb[2],bb[3]],[bb[0],bb[3]]])@mat.T;rows.append(dict(n=n,x=float(l-corn[:,0].min()),y=float(t-corn[:,1].min()),scaleX=float(sx),scaleY=float(sy),rotation=float(angle),opacity=float(q['opacity']) if n in ts else 0))
 node.update(start=730/30,end=800/30,originX=0,originY=0);node['keyframes']={k:[dict(t=q['n']/30,value=q[k]) for q in rows] for k in ['x','y','scaleX','scaleY','rotation','opacity']};replacements[id]=node;ledger.append(dict(id=id,kind='Order!',observedFrames=sorted(n for n,q in ts.items() if not q.get('interpolatedGap')),interpolatedFrames=sorted(n for n,q in ts.items() if q.get('interpolatedGap')),sourceNativeGlyphBox=bb,measurements=rows))
spec=dict(replacements=replacements,changed_frame_range=[730,799],provenance=dict(method='Every native frame: authentic separate food-template SIFT/RANSAC/local refinement, measured opacity, short-word OCR/body isolation and actual native font glyph calibration.',sourceMapping='lunch-native/{frame-609:03d}.png',roots=ledger,limitations='2D affine projection approximates the original3D food surface; original raster food internals remain bitmap. Small or occluded instances with no reliable measurement are hidden; short coherent gaps are explicitly interpolated. Native Order! font/AA can differ from source. No full-frame/video playback.'))
(R/'food-orbit-proposals.json').write_text(json.dumps(spec,indent=2));scene['layers']=[copy.deepcopy(replacements.get(n['id'],n)) for n in scene['layers']]
def absolute(n):
 if isinstance(n,dict):
  if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((R/n['src']).resolve())
  for v in n.values():absolute(v)
 elif isinstance(n,list):
  for v in n:absolute(v)
absolute(scene);scene['source']['notes']+=' Measured independent food/order orbits730–799: native affine transforms of original Apple assets and native Order! word/bubble geometry, with explicit source bounds/visibility/opacity and measurement gaps.';(R/'food-orbit-prototype.scene.json').write_text(json.dumps(scene,indent=2));print('Built',len(replacements),'independent food/order roots',sum(len(q['observedFrames']) for q in ledger),'observed poses',flush=True)
