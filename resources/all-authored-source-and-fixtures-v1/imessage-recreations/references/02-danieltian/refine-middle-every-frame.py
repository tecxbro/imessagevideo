"""Densify source-derived native poses to10Hz, retaining isolated assets/contours rather than any complete-frame layer."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
import numpy as np,json,copy
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-dense';P=R/'peak-middle-refinement.json';p=json.loads(P.read_text());root=p['replacements']['group-1118'];nodes={l['id']:l for l in root['children']};RUN=json.loads((R/'middle-body-runs.json').read_text());seed=[dict(t=int(k)/30,left=v['left'],scale=v['scale']) for k,v in RUN.items()];events=[];measurements={};frame_data={}
def sample(ks,t):
 if not ks:return 0
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*f
 return ks[-1]['value']
def interpolate_points(points,key,t):return sample([dict(t=q['t'],value=q[key]) for q in points],t)
def state(l,k,t):return sample(l.get('keyframes',{}).get(k,[]),t) if k in l.get('keyframes',{}) else l.get(k,1 if k.startswith('scale') else 0)
def ar(n):
 path=R/'assets/middle-every-frame'/f'source-{n:04d}.png'
 if not path.exists():path=M/f'source-{n:04d}.png'
 return np.array(Image.open(path).convert('RGB')).astype(float)
def components(mask,minarea=0):
 lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());out=[]
 for li,s in enumerate(ndimage.find_objects(lab),1):
  if not s or areas[li]<minarea:continue
  y,x=s;out.append(dict(box=[x.start,y.start,x.stop,y.stop],label=li,area=int(areas[li])))
 return out,lab
body=[]
for l in root['children']:
 if not l['id'].startswith('middle-message-'):continue
 rect=l['children'][0]
 if rect.get('type')!='rect' or not str(rect.get('fill','')).startswith('#'):continue
 name=l['id'].replace('middle-message-','');glyph=next(c for c in l['children'] if c['id'].startswith('middle-glyphs-'));cn=glyph['sourceFrame'];cy=state(l,'y',cn/30);rr=RUN[str(cn)]['runs'];near=min(rr,key=lambda q:abs(q['y']-cy));body.append(dict(name=name,node=l,rect=rect,offset=cy-near['y'],canonicalScale=RUN[str(cn)]['scale']))
nodes['middle-message-resy-command']['end']=848/30
nodes['middle-avatar-muse']['end']=848/30
# Match ordered incoming-message body runs to the already-validated semantic tracks. The foreground header is outside the sampled left body band.
for n in range(630,1033):
 a=ar(n);t=n/30;left=interpolate_points(seed,'left',t);S=(960-left)/543;x0=int(left+80*S);x1=int(left+230*S);reg=a[:,x0:x1];gray=(reg.min(2)>190)&(reg.max(2)<242)&(reg.max(2)-reg.min(2)<12);rr=ndimage.binary_closing(gray.mean(1)>.15,iterations=3);lab,num=ndimage.label(rr);runs=[]
 for sl in ndimage.find_objects(lab):
  y=sl[0]
  if y.stop-y.start>=25:runs.append(dict(y=y.start,height=y.stop-y.start))
 frame_data[n]=dict(left=left,scale=S,runs=runs);active=[b for b in body if b['node']['start']<=t<b['node']['end']]
 if not active or not runs:continue
 cost=np.full((len(active),len(runs)),1e6)
 for i,b in enumerate(active):
  l=b['node'];predY=state(l,'y',t);ratio=S/b['canonicalScale'];fullH=state(b['rect'],'height',t)*ratio
  for j,r in enumerate(runs):
   target=r['y']+b['offset']*ratio
   if r['y']<=3:target=r['y']+r['height']-fullH
   visibleH=max(0,min(1080,predY+fullH)-max(0,predY))
   cost[i,j]=abs(target-predY)+.7*abs(visibleH-r['height'])
 ii,jj=linear_sum_assignment(cost)
 for i,j in zip(ii,jj):
  if cost[i,j]>125:continue
  b=active[i];r=runs[j];ratio=S/b['canonicalScale'];fullH=state(b['rect'],'height',t)*ratio;y=r['y']+b['offset']*ratio
  if r['y']<=3:y=r['y']+r['height']-fullH
  measurements.setdefault(b['name'],[]).append(dict(t=t,x=left,y=y,scaleX=ratio,scaleY=ratio,sourceBodyRun=[r['y'],r['height']]))
for b in body:
 ms=measurements.get(b['name'],[])
 if len(ms)<2:continue
 b['node']['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']})
# Source blue message positions and their late pale fade continue through the same camera scroll.
for name,cn,reference in [('budget-reply',780,870),('love-it',930,930)]:
 l=nodes['middle-message-'+name];S0=RUN[str(cn)]['scale'];old=copy.deepcopy(l);hm=nodes['middle-message-how-about'];refS=RUN[str(reference)]['scale'];xWorld=(state(old,'x',reference/30)-960*(1-refS))/refS;dyWorld=(state(old,'y',reference/30)-state(hm,'y',reference/30))/refS;ms=[]
 for n,q in frame_data.items():
  t=n/30
  if not l['start']<=t<l['end']:continue
  a=ar(n);mask=(a[:,:,2]-a[:,:,0]>70)&(a[:,:,2]>190)&(a[:,:,1]>90)&(a[:,:,0]<130);cc,lab=components(mask,1800);predx=state(old,'x',t);predy=state(old,'y',t);valid=[c for c in cc if c['box'][2]-c['box'][0]>120 and c['box'][3]-c['box'][1]>45 and c['box'][0]>900 and abs(c['box'][0]-predx)<180 and abs(c['box'][1]-predy)<180]
  if valid:
   c=min(valid,key=lambda c:abs(c['box'][1]-predy));bb=c['box'];x,y=bb[0],bb[1]
   if y<2:
    extra=20 if name=='budget-reply' else 16;y=bb[3]-(l['children'][0]['height']+extra)*q['scale']/S0
  else:x=960+(xWorld-960)*q['scale'];y=state(hm,'y',t)+dyWorld*q['scale']
  ms.append(dict(t=t,x=x,y=y,scaleX=q['scale']/S0,scaleY=q['scale']/S0))
 if ms:l['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']});measurements[name]=ms
# The entering logos follow large curved source flights;0.5s interpolation is insufficient there.
fly=p['replacements']['group-1068'];flightlog=[]
for actor in fly['children']:
 name=actor['id'].replace('middle-fly-','');old=copy.deepcopy(actor);art=actor['children'][0];ms=[];op=[]
 for n in range(540,604,3):
  aa=ar(n);tt=n/30;bb=None
  if name!='muse':
   rr,gg,bbv=aa[:,:,0],aa[:,:,1],aa[:,:,2]
   if name=='lyft':mask=(rr>170)&(bbv>120)&(gg<100)
   elif name=='airbnb':mask=(rr>160)&(gg<130)&(bbv>65)&(bbv>rr*.3)&(bbv<rr*.75)
   elif name=='resy':mask=(rr>170)&(gg<130)&(bbv<rr*.3)
   else:mask=(gg>220)&(rr<190)&(bbv<150)
   cc,ll=components(ndimage.binary_closing(mask,iterations=2),250);choices=[]
   for c in cc:
    q=c['box'];w=q[2]-q[0];h=q[3]-q[1]
    if w>20 and h>25 and (.5<w/h<1.7 or q[0]<3 or q[2]>1917):choices.append(c)
   if choices:
    q=max(choices,key=lambda c:c['area'])['box'];w=q[2]-q[0];h=q[3]-q[1]
    if q[2]>1917:w=h
    if q[0]<3:w=h;q=[q[2]-w,q[1],q[2],q[3]]
    sx=w/(art['width']-6);sy=h/(art['height']-6);ms.append(dict(t=tt,x=q[0]-3*sx,y=q[1]-3*sy,scaleX=sx,scaleY=sy));op.append(dict(t=tt,value=1))
   else:op.append(dict(t=tt,value=0))
  else:
   mask=(aa.min(2)>155)&(aa.max(2)<245)&(aa.max(2)-aa.min(2)<10);cc,ll=components(mask,80);fits=[]
   for c in cc:
    q=c['box'];w=q[2]-q[0];h=q[3]-q[1]
    if w<100 or h<15:continue
    yy,xx=np.where(ll[q[1]:q[3],q[0]:q[2]]==c['label']);xx=xx+q[0];yy=yy+q[1];fit=np.linalg.lstsq(np.stack([2*xx,2*yy,np.ones(len(xx))],1),xx*xx+yy*yy,rcond=None)[0];cx,cy,constant=fit;rad=np.sqrt(max(1,constant+cx*cx+cy*cy));std=float(np.std(np.sqrt((xx-cx)**2+(yy-cy)**2)))
    if not(35<rad<400 and std<5.5):continue
    oldcx=state(old,'x',tt)+art['width']*state(old,'scaleX',tt)/2;oldcy=state(old,'y',tt)+art['height']*state(old,'scaleY',tt)/2;fits.append((std*25+np.hypot(cx-oldcx,cy-oldcy),cx,cy,rad))
   if fits:
    _,cx,cy,rad=min(fits);ms.append(dict(t=tt,x=float(cx-rad),y=float(cy-rad),scaleX=float(2*rad/art['width']),scaleY=float(2*rad/art['height'])));op.append(dict(t=tt,value=1))
   else:op.append(dict(t=tt,value=0))
 if ms:
  actor['start']=min(actor['start'],ms[0]['t']);actor['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']});actor['keyframes']['opacity']=op;flightlog.append(dict(actor=name,measurements=ms))
# Track the actual foreground header by the unique green orb, including the source's slower zoom and vertical settling.
header=p['replacements']['group-1077'];hseed=copy.deepcopy(header);a=ar(675);mask=(a[:,:,1]>220)&(a[:,:,0]<190)&(a[:,:,2]<150);cc,lab=components(mask,300);base=min((c['box'] for c in cc if 750<(c['box'][0]+c['box'][2])/2<1100 and c['box'][1]<400),key=lambda b:abs((b[0]+b[2])/2-915));hms=[]
for n in [n for n in range(600,1033) if n>=630 or n%3==0]:
 a=ar(n);roi=a[:400,750:1120];mask=(roi[:,:,1]>220)&(roi[:,:,0]<190)&(roi[:,:,2]<150);cc,lab=components(mask,300);valid=[c['box'] for c in cc if c['box'][2]-c['box'][0]>25 and c['box'][3]-c['box'][1]>25]
 if not valid:continue
 b=min(valid,key=lambda b:abs((b[0]+b[2])/2+750-915));b=[b[0]+750,b[1],b[2]+750,b[3]];sx=(b[2]-b[0])/(base[2]-base[0]);sy=(b[3]-b[1])/(base[3]-base[1]);hms.append(dict(t=n/30,x=b[0]-base[0]*sx,y=b[1]-base[1]*sy,scaleX=sx,scaleY=sy))
header['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in hms] for k in ['x','y','scaleX','scaleY']})
# The same original avatars remain independently posed; add the Airbnb agent during its earlier typing/card turn too.
for name in ['budget','how-about','airbnb-booked','lyft-booked','resy-booked']:
 l=nodes['middle-avatar-'+name];original=copy.deepcopy(l);kind='airbnb' if name in ['how-about','airbnb-booked'] else ('lyft' if name=='lyft-booked' else 'resy');src=Path(l['children'][0]['src']);im=np.array(Image.open(src).convert('RGB')).astype(float)
 def hue(aa):
  r,g,b=aa[:,:,0],aa[:,:,1],aa[:,:,2]
  if kind=='airbnb':return(r>160)&(g<130)&(b>65)&(b>r*.3)&(b<r*.75)
  if kind=='lyft':return(r>170)&(b>120)&(g<100)
  return(r>170)&(g<130)&(b<r*.3)
 yy,xx=np.where(hue(im));intrinsic=[xx.min(),yy.min(),xx.max()+1,yy.max()+1];nativeW=126*(intrinsic[2]-intrinsic[0])/im.shape[1];nativeH=126*(intrinsic[3]-intrinsic[1])/im.shape[0];ms=[]
 if name=='how-about':l['start']=27.35
 for n,q in frame_data.items():
  t=n/30
  if not l['start']<=t<l['end']:continue
  aa=ar(n);left=max(0,int(q['left']-210));right=int(q['left']-10);roi=aa[:,left:right];cc,lab=components(ndimage.binary_closing(hue(roi),iterations=1),250);valid=[c['box'] for c in cc if c['box'][2]-c['box'][0]>35 and c['box'][3]-c['box'][1]>30]
  if not valid:continue
  target=state(original,'y',t)+63*q['scale']
  if name=='how-about' and t<29.:
   target=850 if t<28.1 else 980-(t-28.5)*400
  b=min(valid,key=lambda b:abs((b[1]+b[3])/2-target));b=[b[0]+left,b[1],b[2]+left,b[3]];sx=(b[2]-b[0])/nativeW;sy=(b[3]-b[1])/nativeH;y=b[1]
  if b[3]>1077:sy=sx
  if b[1]<2:sy=sx;y=b[3]-nativeH*sy
  ms.append(dict(t=t,x=b[0]-126*intrinsic[0]/im.shape[1]*sx,y=y-126*intrinsic[1]/im.shape[0]*sy,scaleX=sx,scaleY=sy))
 if ms:l['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']})
# Track the actual Muse portrait circle instead of snapping it to a newly born message's future bottom edge.
muse=nodes['middle-avatar-muse'];oldMuse=copy.deepcopy(muse);src=Path(muse['children'][0]['src']);im=np.array(Image.open(src).convert('RGB')).astype(float);mm=(im.min(2)>170)&(im.max(2)<245)&(im.max(2)-im.min(2)<18);iy,ix=np.where(mm);ib=[ix.min(),iy.min(),ix.max()+1,iy.max()+1];iw=126*(ib[2]-ib[0])/im.shape[1];ih=126*(ib[3]-ib[1])/im.shape[0];mms=[]
for n,q in frame_data.items():
 t=n/30
 if not muse['start']<=t<muse['end']:continue
 aa=ar(n);left=max(0,int(q['left']-210));right=int(q['left']-10);reg=aa[:,left:right];mask=(reg.min(2)>170)&(reg.max(2)<245)&(reg.max(2)-reg.min(2)<18);cc,ll=components(mask,500);valid=[c['box'] for c in cc if c['box'][2]-c['box'][0]>50 and c['box'][3]-c['box'][1]>35 and .6<(c['box'][2]-c['box'][0])/(c['box'][3]-c['box'][1])<1.6]
 if not valid:continue
 target=state(oldMuse,'y',t)+63*q['scale'];b=min(valid,key=lambda b:abs((b[1]+b[3])/2-target));b=[b[0]+left,b[1],b[2]+left,b[3]];sx=(b[2]-b[0])/iw;sy=(b[3]-b[1])/ih;y=b[1]
 if b[1]<2:sy=sx;y=b[3]-ih*sy
 if b[3]>1077:sy=sx
 mms.append(dict(t=t,x=b[0]-126*ib[0]/im.shape[1]*sx,y=y-126*ib[1]/im.shape[0]*sy,scaleX=sx,scaleY=sy))
if mms:muse['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in mms] for k in ['x','y','scaleX','scaleY']})
# Reactions use their corresponding measured parent poses rather than retaining the old sparse tracks.
for kind,parent in [('command-like','airbnb-command'),('budget-like','budget-reply')]:
 l=nodes['middle-reaction-'+kind];par=nodes['middle-message-'+parent];l['keyframes'].update(copy.deepcopy({k:par['keyframes'][k] for k in ['x','y','scaleX','scaleY']}))
# Keep the card aligned with the measured follow-up bubble; its original held artwork remains bounded and independent.
card=nodes['middle-airbnb-rich-card'];oldcard=copy.deepcopy(card);cm=[];how=nodes['middle-message-how-about'];s0=RUN['855']['scale']
for n,q in frame_data.items():
 t=n/30
 if not card['start']<=t<card['end']:continue
 if t<28.85:cm.append(dict(t=t,x=state(oldcard,'x',t),y=state(oldcard,'y',t),scaleX=state(oldcard,'scaleX',t),scaleY=state(oldcard,'scaleY',t)));continue
 ratio=q['scale']/s0*.98;bottom=state(how,'y',t)-34*q['scale'];cm.append(dict(t=t,x=q['left'],y=bottom-546*ratio,scaleX=ratio*737/693,scaleY=ratio*546/514))
card['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in cm] for k in ['x','y','scaleX','scaleY']})
# Restore the sender label above Airbnb's typing/card message. It is independent native source lettering, not part of the bitmap card.
a=ar(855);alpha=np.clip((253-a[410:460,525:660].mean(2))/253,0,1);d,stats=trace_alpha(alpha,525,410);labels=[]
for n,q in frame_data.items():
 t=n/30
 if not 27.35<=t<33.3:continue
 top=state(card,'y',t) if t>=28.25 else (788-(t-27.5)*150);l=int(q['left']+8*q['scale']);r=min(1920,int(q['left']+190*q['scale']));y0=max(0,int(top-80*q['scale']));y1=max(0,int(top-5*q['scale']))
 if y1<=y0:continue
 aa=ar(n)[y0:y1,l:r];mask=(aa.max(2)<200)&(aa.max(2)-aa.min(2)<25);ys,xs=np.where(mask)
 if len(xs)<15:continue
 S=q['scale']/s0;labels.append(dict(t=t,x=float(xs.min()+l-536*S),y=float(ys.min()+y0-425*S),scaleX=S,scaleY=S))
if labels:root['children']=[l for l in root['children'] if l['id']!='middle-airbnb-card-sender-label']+[dict(id='middle-airbnb-card-sender-label',type='path',d=d,fill='#000000',semanticText='Airbnb',sourceFrame=855,start=27.35,end=min(33.3,labels[-1]['t']+.1),keyframes={k:[dict(t=m['t'],value=m[k]) for m in labels] for k in ['x','y','scaleX','scaleY']})]
p['bodyPoseMeasurements']=measurements;p['provenance'].append(dict(kind='dense native middle motion refinement',cadence='Every source frame at native30fps for630–1032; original10Hz flying entrance retained',sourceFrames=[n for n in frame_data],diagnosis='The0.5s anchors corrected semantic/layout misses but linear interpolation missed the fast source scroll easing. Densify isolated message/blue/header/avatar poses and retain the original bounded artwork/native contours.',messagePoseCount=sum(len(v) for v in measurements.values()),headerMeasurements=hms,airbnbSenderLabelMeasurements=labels,flyingMeasurements=flightlog));P.write_text(json.dumps(p,indent=2));print('Densified middle poses',sum(len(v) for v in measurements.values()),'header',len(hms),'frames',len(frame_data),flush=True)
