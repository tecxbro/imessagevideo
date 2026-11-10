"""Close semantic-association and spring/birth failures found by the v10 every-frame scan."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import json,copy,numpy as np
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-every-frame';P=R/'peak-middle-refinement.json';p=json.loads(P.read_text());g=p['replacements']['group-1118'];N={n['id']:n for n in g['children']};RUN=json.loads((R/'middle-body-runs.json').read_text());seed=[dict(t=int(k)/30,value=v['scale']) for k,v in RUN.items()];ledger=[]
def ar(n):return np.array(Image.open(M/f'source-{n:04d}.png').convert('RGB')).astype(float)
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
def state(n,k,t):return sample(n['keyframes'][k],t) if k in n.get('keyframes',{}) else n.get(k,1 if k.startswith('scale') else 0)
def cam(n):return sample(seed,n/30)
def keyset(node,k,rows):
 old=[x for x in node.setdefault('keyframes',{}).get(k,[]) if round(x['t']*30) not in {m['n'] for m in rows}];node['keyframes'][k]=sorted(old+[dict(t=m['n']/30,value=m[k]) for m in rows],key=lambda q:q['t'])
def grayruns(a,n):
 S=cam(n);left=960-543*S;roi=a[:,int(left+80*S):int(left+230*S)];m=(roi.min(2)>190)&(roi.max(2)<242)&(roi.max(2)-roi.min(2)<12);rr=ndimage.binary_closing(m.mean(1)>.15,iterations=3);lab,num=ndimage.label(rr);return [dict(y=sl[0].start,height=sl[0].stop-sl[0].start) for sl in ndimage.find_objects(lab) if sl[0].stop-sl[0].start>=25]
def bodybox(a,n,r,width=1200):
 S=cam(n);left=960-543*S;y0=max(0,r['y']-5);y1=min(1080,r['y']+r['height']+5);x0=max(0,int(left-8));x1=min(1920,int(left+width*S+30));reg=a[y0:y1,x0:x1];mask=(reg.min(2)>190)&(reg.max(2)<246)&(reg.max(2)-reg.min(2)<14);lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());cands=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w>70 and h>20 and xx.start<100:cands.append((areas[li],[xx.start+x0,yy.start+y0,xx.stop+x0,yy.stop+y0]))
 return max(cands,key=lambda v:v[0])[1] if cands else None
# A departed long Resy command must never inherit the short Budget body's track. Settled older rows share one measured camera transform.
budget=N['middle-message-budget'];dy={'kickoff':-952.7,'airbnb-command':-724.5,'lyft-command':-549.6,'resy-command':-(567-282)/RUN['780']['scale']};last={}
for name,offset in dy.items():
 node=N['middle-message-'+name];cn=next(c['sourceFrame'] for c in node['children'] if c['id'].startswith('middle-glyphs-'));sc=RUN[str(cn)]['scale'];rows=[]
 for n in range(750,871):
  t=n/30;S=cam(n);y=state(budget,'y',t)+offset*S;ratio=S/sc;H=node['children'][0]['height']*ratio
  if y+H<=0:
   node['end']=min(node['end'],t);break
  rows.append(dict(n=n,x=960-543*S,y=y,scaleX=ratio,scaleY=ratio));last[name]=n
 for k in ['x','y','scaleX','scaleY']:keyset(node,k,rows)
 ledger.append(dict(kind='shared settled old-message geometry tied to unique Budget track',message=name,worldOffset=offset,lastVisibleFrame=last.get(name)))
N['middle-avatar-muse']['end']=min(N['middle-avatar-muse']['end'],N['middle-message-resy-command']['end'])
# Fit each new gray message's actual isolated capsule during its own spring, then retain accepted camera poses.
windows={'kickoff':(636,650,1),'airbnb-command':(662,678,2),'lyft-command':(675,691,3),'resy-command':(696,712,4),'budget':(729,746,None),'airbnb-booked':(949,965,None),'lyft-booked':(968,985,None),'resy-booked':(999,1015,None)}
for name,(first,lastn,count) in windows.items():
 node=N['middle-message-'+name];body=node['children'][0];w=body['width'];h=body['height'];old=copy.deepcopy(node);rows=[];fills=[];op=[]
 for n in range(first,lastn+1):
  a=ar(n);runs=grayruns(a,n)
  if count and len(runs)<count:continue
  if count:r=runs[count-1]
  else:
   target=state(old,'y',n/30);valid=[q for q in runs if q['y']>max(300,target-180) and q['y']<target+180]
   if not valid:continue
   r=min(valid,key=lambda q:abs(q['y']-target))
  b=bodybox(a,n,r)
  if not b:continue
  l,t,rr,bb=b;ratio=(rr-l)/w
  if not(.35<ratio<1.6):continue
  sy=(bb-t)/h if bb<1078 else ratio
  # Keep glyph aspect stable for clipped/small-body spring poses.
  if not(.7<sy/ratio<1.3):sy=ratio
  rows.append(dict(n=n,x=l,y=t,scaleX=ratio,scaleY=sy));roi=a[t:bb,l:rr];gray=(roi.min(2)>190)&(roi.max(2)<246)&(roi.max(2)-roi.min(2)<14);v,ct=np.unique(roi[gray].astype('uint8'),axis=0,return_counts=True);fill=v[ct.argmax()];fills.append(dict(t=n/30,value='#'+''.join(f'{x:02x}' for x in fill)));ink=roi[(roi.max(2)-roi.min(2)<15)&(roi.max(2)<180)];value=1.
  if len(ink)>30:value=float(np.clip((fill.mean()-np.quantile(ink.mean(1),.1))/max(1,fill.mean()),0,1))
  op.append(dict(t=n/30,value=value))
 if not rows:continue
 node['start']=rows[0]['n']/30
 for k in ['x','y','scaleX','scaleY']:keyset(node,k,rows)
 for k in ['scaleX','scaleY']:body.get('keyframes',{}).pop(k,None)
 body.setdefault('keyframes',{})['fill']=fills
 # Original source text can fade in slightly after the gray plate appears.
 for c in node['children']:
  if c['id'].startswith(('middle-glyphs-','middle-blue-mention-')) and name!='resy-booked':c.setdefault('keyframes',{})['opacity']=op
 ledger.append(dict(kind='native isolated message spring',message=name,measurements=rows))
# Actual outgoing blue typing capsule enters before the earlier nominal start.
node=N['middle-message-budget-reply'];old=copy.deepcopy(node);body=node['children'][0];cn=780;S0=RUN[str(cn)]['scale'];rows=[];ws=[];hs=[]
for n in range(748,781):
 a=ar(n);m=(a[:,:,2]-a[:,:,0]>45)&(a[:,:,2]>180)&(a[:,:,0]<160);lab,num=ndimage.label(m,np.ones((3,3)));cc=[]
 for sl in ndimage.find_objects(lab):
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if xx.start>1000 and w>120 and h>35:cc.append([xx.start,yy.start,xx.stop,yy.stop])
 if not cc:continue
 b=max(cc,key=lambda q:(q[2]-q[0])*(q[3]-q[1]));S=cam(n)/S0;l,t,r,bottom=b;rows.append(dict(n=n,x=l,y=t,scaleX=S,scaleY=S));ws.append(dict(t=n/30,value=(r-l)/S));hs.append(dict(t=n/30,value=(bottom-t)/S))
if rows:
 node['start']=rows[0]['n']/30
 for k in ['x','y','scaleX','scaleY']:keyset(node,k,rows)
 body['keyframes']['width']=[q for q in body['keyframes'].get('width',[]) if q['t']>780/30]+ws;body['keyframes']['width'].sort(key=lambda q:q['t'])
 body['keyframes']['height']=hs
 for c in node['children']:
  if c['id'].startswith('middle-source-dot-'):c['start']=node['start']
 ledger.append(dict(kind='earlier actual blue typing birth',firstFrame=rows[0]['n'],measurements=rows))
# The Airbnb agent starts typing before the card reveal; it follows the actual scrolling body instead of one fixed825 pose.
typ=N['middle-airbnb-typing'];rows=[];S0=RUN['825']['scale'];old=copy.deepcopy(typ)
for n in range(808,841):
 a=ar(n);runs=[q for q in grayruns(a,n) if q['y']>650 and q['height']<150]
 if not runs:continue
 q=runs[-1];b=bodybox(a,n,q,width=330)
 if not b or b[2]-b[0]>350:continue
 S=cam(n)/S0;rows.append(dict(n=n,x=b[0],y=b[1],scaleX=S,scaleY=S))
if rows:
 typ['start']=rows[0]['n']/30;typ['end']=(rows[-1]['n']+1)/30
 for k in ['x','y','scaleX','scaleY']:typ['keyframes']={**typ.get('keyframes',{}),k:[dict(t=m['n']/30,value=m[k]) for m in rows]}
# Measure the actual card's spring bounds, not a guessed tiny start followed by linear interpolation.
card=N['middle-airbnb-rich-card'];art=card['children'][0];rows=[];blurs=[]
for n in range(838,871):
 a=ar(n);S=cam(n);left=960-543*S;mask=a.min(2)<249;mask[:300]=False;mask[:,:max(0,int(left-65))]=False;mask[:,min(1920,int(left+900)):]=False;mask=ndimage.binary_closing(mask,iterations=5);lab,num=ndimage.label(mask,np.ones((3,3)));cc=[]
 for sl in ndimage.find_objects(lab):
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if xx.start<left+100 and w>250 and h>150:cc.append([xx.start,yy.start,xx.stop,yy.stop])
 if not cc:continue
 b=max(cc,key=lambda q:(q[2]-q[0])*(q[3]-q[1]));l,t,r,bottom=b;l=max(l,left-8);sx=(r-l)/art['width'];sy=(bottom-t)/art['height'];rows.append(dict(n=n,x=l,y=t,scaleX=sx,scaleY=sy));blurs.append(dict(t=n/30,value=max(0,(846-n)*1.1)))
if rows:
 card['start']=rows[0]['n']/30
 for k in ['x','y','scaleX','scaleY']:keyset(card,k,rows)
 card['keyframes']['blur']=blurs
 ledger.append(dict(kind='native product-card independent spring bounds',measurements=rows))
# Source chat persists through34.3, then clears before the first end phrase. Preserve accepted final bubble geometry and continue the measured exit.
for node in [g]+g['children']:
 if abs(node.get('end',0)-34.2)<.0001:node['end']=1030/30
 def extend(c):
  if abs(c.get('end',0)-34.2)<.0001:c['end']=1030/30
  for q in c.get('children',[]):extend(q)
 extend(node)
lastPose=state(N['middle-message-resy-booked'],'y',1025/30);exitkeys=[dict(t=0,value=0),dict(t=1025/30,value=0)]
for n in range(1026,1030):
 a=ar(n);rr=grayruns(a,n)
 if rr:exitkeys.append(dict(t=n/30,value=rr[-1]['y']-lastPose))
g.setdefault('keyframes',{})['y']=exitkeys;p['replacements']['group-1077']['end']=1030/30
# Reattach reactions after authoritative parent-pose corrections.
for name,parent in [('command-like','airbnb-command'),('budget-like','budget-reply')]:
 node=N['middle-reaction-'+name];par=N['middle-message-'+parent]
 for k in ['x','y','scaleX','scaleY']:node['keyframes'][k]=copy.deepcopy(par['keyframes'][k])
p['provenance'].append(dict(kind='v11 complete-frame diagnosis repairs',diagnosis='v10 source peaks exposed semantic body theft, fast nonlinear scroll between10Hz anchors, independent newborn spring scaling, late typing starts, a guessed rich-card entry, and premature34.2 phase cut.',records=ledger));p['changed_frames']=[[630,1029]];(R/'v11-middle-refinement.json').write_text(json.dumps(p,indent=2));print('Prepared v11 middle pose/birth fixes',len(ledger),flush=True)
