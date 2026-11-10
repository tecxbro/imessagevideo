"""Scoped source02 burst/phone, reasoning and Amazon reveal refinements; immutable input is preserved."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/root-early-end-measure';A=R/'assets/early-end-art';A.mkdir(exist_ok=True);BASE=R/'scene-final-v9.json';S=json.loads(BASE.read_text());orig={l['id']:l for l in S['layers']};patch={};added=[];ledger=[];gradients=[]
def ar(n):return np.array(Image.open(M/f'frame-{n:04d}.png').convert('RGB')).astype(float)
def save_art(n,box,name):
 a=Image.fromarray(ar(n).astype('uint8')).crop(tuple(map(int,box)));p=A/(name+'.png');a.save(p);ledger.append(dict(kind='bounded original phone hardware or emoji artwork',sourceFrame=n,sourceBounds=list(map(int,box)),asset=str(p)));return dict(type='image',id='early-art-'+name,src=str(p),x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1],sourceFrame=n,sourceBounds=list(map(int,box)))
def components(mask,minarea=1):
 lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());out=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl or areas[li]<minarea:continue
  y,x=sl;out.append(dict(box=[x.start,y.start,x.stop,y.stop],area=int(areas[li]),label=li))
 return out,lab
# The original circular send body and each measured burst particle are native geometry, rather than a generated random cloud.
burst=[];circlems=[];arrow=None
for n in range(171,183):
 a=ar(n);mask=(a[:,:,2]-a[:,:,0]>25)&(a[:,:,1]-a[:,:,0]>10)&(a[:,:,2]>160);mask[:280]=False;mask[:,:1100]=False;cc,lab=components(mask,30);rounds=[c for c in cc if 40<c['box'][2]-c['box'][0]<250 and 40<c['box'][3]-c['box'][1]<250 and .7<(c['box'][2]-c['box'][0])/(c['box'][3]-c['box'][1])<1.4]
 if rounds:
  c=max(rounds,key=lambda c:c['area']);x,y,r,b=c['box'];inside=a[y:b,x:r];vals,cnt=np.unique(inside[lab[y:b,x:r]==c['label']].astype('uint8'),axis=0,return_counts=True);color=vals[cnt.argmax()];circlems.append(dict(t=n/30,x=x,y=y,width=r-x,height=b-y,fill='#'+''.join(f'{v:02x}' for v in color)))
  if n==171:
   aa=np.clip((inside[:,:,0]-int(color[0]))/(255-int(color[0])),0,1);yy,xx=np.indices(aa.shape);ellipse=((xx-(r-x)/2)/((r-x)/2-5))**2+((yy-(b-y)/2)/((b-y)/2-5))**2<1;aa*=ellipse;d,stats=trace_alpha(aa);arrow=dict(id='early-send-arrow',type='path',d=d,fill='#FFFFFF',sourceFrame=n)
 # Saturated small blue components are particle centers; the pale central circle is deliberately excluded.
 pm=(a[:,:,0]<160)&(a[:,:,1]<215)&(a[:,:,2]<235)&(a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]-a[:,:,0]>15);pm[:300]=False;pm[:,:1100]=False;pc,pl=components(pm,1);dots=[]
 for i,c in enumerate(pc):
  x,y,r,b=c['box'];w,h=r-x,b-y
  if w>12 or h>12 or c['area']>120:continue
  reg=a[y:b,x:r];vals=reg[pl[y:b,x:r]==c['label']];color=np.median(vals,axis=0).astype(int);dots.append(dict(id=f'early-particle-{n}-{i}',type='circle',x=x,y=y,width=max(1,w),height=max(1,h),fill='#'+''.join(f'{v:02x}' for v in color),sourceFrame=n))
 burst.append(dict(id='early-particle-pose-'+str(n),type='group',children=dots,start=n/30,end=(n+1)/30))
circ=dict(id='early-send-circle',type='circle',start=5.7,end=181/30,keyframes={k:[dict(t=m['t'],value=m[k]) for m in circlems] for k in ['x','y','width','height','fill']});burst.append(circ)
if arrow:
 ax=circlems[0]['x'];ay=circlems[0]['y'];aw=circlems[0]['width'];ah=circlems[0]['height'];burst.append(dict(id='early-send-arrow-pose',type='group',children=[arrow],start=5.7,end=5.98,keyframes={'x':[dict(t=m['t'],value=m['x']) for m in circlems],'y':[dict(t=m['t'],value=m['y']) for m in circlems],'scaleX':[dict(t=m['t'],value=m['width']/aw) for m in circlems],'scaleY':[dict(t=m['t'],value=m['height']/ah) for m in circlems],'opacity':[dict(t=5.7,value=1),dict(t=5.9,value=.7),dict(t=5.98,value=0)]}))
patch['group-968']=dict(id='group-968',type='group',children=burst,start=5.7,end=6.1)
# The native composer hands off to the sent message before the phone enters.
for lid in ['group-801','composer-v5-char-51']:
 l=copy.deepcopy(orig[lid]);l['end']=min(l['end'],175/30);patch[lid]=l
l=copy.deepcopy(orig['group-857']);l['end']=5.7;patch[l['id']]=l
# Fit phone translation from the original avatar's beige region, avoiding a guessed late phone reveal.
ref=np.array(Image.open(R/'assets/muse-avatar.png').convert('RGB')).astype(float);beige=(ref[:,:,0]-ref[:,:,2]>25)&(ref[:,:,1]-ref[:,:,2]>10)&(ref[:,:,0]>140);refY=np.where(beige)[0].mean();phone=[];frames=sorted(int(p.stem.split('-')[-1]) for p in M.glob('frame-*.png') if 183<=int(p.stem.split('-')[-1])<=261)
for n in frames:
 a=ar(n);sub=a[:650,840:1080];mask=(sub[:,:,0]-sub[:,:,2]>25)&(sub[:,:,1]-sub[:,:,2]>10)&(sub[:,:,0]>140);yy=np.where(mask)[0]
 if len(yy)>100:phone.append(dict(t=n/30,y=float(yy.mean()-refY)))
# Keep the measured held phone pose rather than extrapolating below the reference coordinate system.
G=copy.deepcopy(orig['group-995']);G['start']=6.1;G['keyframes']={'y':[dict(t=m['t'],value=m['y']) for m in phone]};y183=next(m['y'] for m in phone if abs(m['t']-6.1)<.001);hardware=[]
for box,name in [((296,0,1624,250),'phone-rounded-top'),((296,250,363,355),'phone-left-bridge'),((1554,250,1624,355),'phone-right-bridge')]:
 im=save_art(183,box,name);im['y']-=y183;hardware.append(im)
G['children'][2:2]=hardware
# Reconstruct the sent message's original glyphs and tail once, then fit its separate flight and phone arrival.
cn=225;a=ar(cn);co,lab=components((a[:,:,2]-a[:,:,0]>45)&(a[:,:,1]>85)&(a[:,:,2]>175),100);bc=max((c for c in co if c['box'][2]-c['box'][0]>400 and c['box'][3]-c['box'][1]>80),key=lambda c:c['area']);x0,y0,x1,y1=bc['box'];crop=a[y0:y1,x0:x1];blue=(crop[:,:,2]-crop[:,:,0]>45)&(crop[:,:,0]<160);vals,cnt=np.unique(crop[blue].astype('uint8'),axis=0,return_counts=True);bg=vals[cnt.argmax()];alpha=np.clip((crop[:,:,0]-int(bg[0]))/(255-int(bg[0])),0,1);alpha*=ndimage.binary_fill_holes(blue);dd,stats=trace_alpha(alpha);glyph=dict(id='early-sent-message-glyphs',type='path',d=dd,fill='#FFFFFF',semanticText='muse, my boss wants a team offsite\ntmr. can u help?',sourceFrame=cn)
shape=np.clip((255-crop[:,:,0])/(255-int(bg[0])),0,1);shape[ndimage.binary_fill_holes(shape>.35)]=1;bodyd,bstats=trace_alpha(shape);body=dict(id='early-sent-message-shape',type='path',d=bodyd,fill='#'+''.join(f'{v:02x}' for v in bg));blue_ms=[];flight=[]
for n in sorted(set(range(175,181))|set(frames)):
 a=ar(n);cc,ll=components((a[:,:,2]-a[:,:,0]>10)&(a[:,:,1]>85)&(a[:,:,2]>175),100);rects=[c for c in cc if c['box'][2]-c['box'][0]>400 and c['box'][3]-c['box'][1]>40]
 if not rects:continue
 c=max(rects,key=lambda c:c['area']);l,t,r,b=c['box'];sx=(r-l)/(x1-x0);sy=sx;yy=t
 if t<2:yy=b-(y1-y0)*sy
 reg=a[max(0,t):b,l:r];mask=(reg[:,:,2]-reg[:,:,0]>10)&(reg[:,:,1]>85)&(reg[:,:,2]>175);vv=reg[mask];mode=np.median(vv,0) if len(vv) else bg;opacity=float(np.clip((255-mode[0])/(255-int(bg[0])),0,1));m=dict(t=n/30,x=l,y=yy,scaleX=sx,scaleY=sy,opacity=opacity)
 if n<183:flight.append(m)
 else:
  py=min(phone,key=lambda q:abs(q['t']-n/30))['y'];m['y']-=py;blue_ms.append(m)
for c in G['children']:
 if c['id']=='bubble-983':
  c.clear();c.update(id='bubble-983',type='group',children=[body,glyph],start=185/30,end=8.73,keyframes={k:[dict(t=m['t'],value=m[k]) for m in blue_ms] for k in ['x','y','scaleX','scaleY','opacity']})
# The first flying copy is still dark while the blue fill appears, then the later phone copy is white.
if flight:
 flbody=copy.deepcopy(body);flbody['id']='early-flight-body';flglyph=copy.deepcopy(glyph);flglyph['id']='early-flight-glyphs';flglyph['fill']='#5F7887';added.append(dict(id='early-sent-message-flight',type='group',children=[flbody,flglyph],start=flight[0]['t'],end=6.0,keyframes={k:[dict(t=m['t'],value=m[k]) for m in flight] for k in ['x','y','scaleX','scaleY','opacity']}))
# Measured typing appearance and dot colors; do not show the agent typing before the source does.
typing=[]
for n in frames:
 a=ar(n);mask=(a.min(2)>190)&(a.max(2)<245)&(a.max(2)-a.min(2)<18);mask[:450]=False;mask[:,:380]=False;mask[:,1400:]=False;cc,ll=components(mask,100);valid=[c for c in cc if c['box'][0]<600 and 150<c['box'][2]-c['box'][0]<400 and c['box'][3]-c['box'][1]>60]
 if valid:typing.append(n)
firstTyping=min(typing)/30 if typing else 7.
for c in G['children']:
 if c['id'] in ['bubble-987','circle-988','circle-989','circle-990']:c['start']=firstTyping
 if c['id'] in ['circle-988','circle-989','circle-990']:
  cx=c['x']+c['width']/2;cy=c['y']+c['height']/2;colors=[]
  for m in phone:
   n=round(m['t']*30)
   if n not in typing:continue
   a=ar(n);yy=int(round(cy+m['y']));xx=int(round(cx))
   if 0<=yy<1080:color=a[yy,xx].astype(int);colors.append(dict(t=m['t'],value='#'+''.join(f'{v:02x}' for v in color)))
  if colors:c.setdefault('keyframes',{})['fill']=colors
patch['group-995']=G;ledger.append(dict(kind='native measured phone reveal',sourceFrames=[round(m['t']*30) for m in phone],measurements=phone,firstTyping=firstTyping,sentMessageMeasurements=blue_ms,flightMeasurements=flight))
# Reasoning rows reveal much faster than the earlier approximation; fit each exact row independently and retain native semantic contours.
reasonframes=sorted(int(p.stem.split('-')[-1]) for p in M.glob('frame-*.png') if 270<=int(p.stem.split('-')[-1])<=360);rows={}
for n in reasonframes:
 a=ar(n);mask=a.max(2)<245;run=ndimage.binary_closing(mask.sum(1)>3,iterations=3);lab,num=ndimage.label(run);boxes=[]
 for sl in ndimage.find_objects(lab):
  yy=sl[0]
  if yy.stop-yy.start<15:continue
  ys,xs=np.where(mask[yy.start:yy.stop]);boxes.append([int(xs.min()),yy.start,int(xs.max()+1),yy.stop])
 rows[n]=boxes
canonical=360;ca=ar(canonical);baseRows=rows[canonical];copytext=['Checking what I know about Photon...','👥9 people · 📍880 Harrison St · ❤️Loves sushi','Offsite tomorrow. What do we need?','🏠A place to stay','🚗Rides','🍣Food','Let me find agents who can help...'];new=[]
for i,b in enumerate(baseRows):
 l,t,r,bot=b;roi=ca[t:bot,l:r];color=(roi.max(2)-roi.min(2)>22)&(roi.min(2)<235);labels,num=ndimage.label(ndimage.binary_dilation(color,iterations=4),np.ones((3,3)));ebox=[]
 for sl in ndimage.find_objects(labels):
  if not sl:continue
  yy,xx=sl
  if xx.stop-xx.start<12 or yy.stop-yy.start<12:continue
  ebox.append([max(l,l+xx.start-3),max(t,t+yy.start-3),min(r,l+xx.stop+3),min(bot,t+yy.stop+3)])
 neutral=(roi.max(2)-roi.min(2)<12)&(roi.max(2)<240);vals,cnt=np.unique(roi[neutral].astype('uint8'),axis=0,return_counts=True);fill=vals[cnt.argmax()] if len(vals) else np.array([164,164,164]);alpha=np.clip((255-roi.mean(2))/(255-float(fill.mean())),0,1)
 for x,y,rr,bb in ebox:alpha[y-t:bb-t,x-l:rr-l]=0
 d,stats=trace_alpha(alpha,l,t);path=dict(id='early-reasoning-copy-'+str(i),type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in fill),semanticText=copytext[i],sourceFrame=canonical,editability='Native semantic glyph contours, not live font text.');children=[path]
 for j,eb in enumerate(ebox):children.append(save_art(canonical,eb,'reason-emoji-'+str(i)+'-'+str(j)))
 ms=[];fills=[];emo=[]
 for n,rr in rows.items():
  if len(rr)<=i:continue
  q=rr[i];ref=rr[0];sx=(ref[2]-ref[0])/(baseRows[0][2]-baseRows[0][0]);sy=(ref[3]-ref[1])/(baseRows[0][3]-baseRows[0][1]);aa=ar(n);reg=aa[q[1]:q[3],q[0]:q[2]];neut=(reg.max(2)-reg.min(2)<12)&(reg.max(2)<240);vv,cc=np.unique(reg[neut].astype('uint8'),axis=0,return_counts=True);fc=vv[cc.argmax()] if len(vv) else fill;fills.append(dict(t=n/30,value='#'+''.join(f'{v:02x}' for v in fc)));spread=float(np.quantile(reg.max(2)-reg.min(2),.995));baseSpread=float(np.quantile(roi.max(2)-roi.min(2),.995));emo.append(dict(t=n/30,value=min(1,spread/max(1,baseSpread))));ms.append(dict(t=n/30,x=q[0]-l*sx,y=q[1]-t*sy,scaleX=sx,scaleY=sy))
 path['keyframes']={'fill':fills}
 for c in children[1:]:c['keyframes']={'opacity':emo}
 st=8.7 if i==0 else ms[0]['t']-.035;new.append(dict(id='early-reasoning-row-'+str(i),type='group',children=children,start=st,end=12.2,keyframes={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']}));ledger.append(dict(kind='native reasoning row timing',semanticText=copytext[i],sourceFrame=canonical,sourceBounds=b,measurements=ms,**stats))
new[0]['keyframes']['opacity']=[dict(t=8.7,value=0),dict(t=8.88,value=1)]
patch['reason-v5-measured-camera']=dict(id='reason-v5-measured-camera',type='group',children=new,start=8.7,end=12.2)
# Amazon's later held suffix was absent from the earlier partial-reveal outline. Use the full held lettering, but keep independent prefix/capsule/suffix motion and clipping.
provider=next(l for l in S['layers'] if l.get('start')==37.65 and l.get('end')==38.1);amazon=[]
def capsule(n):
 a=ar(n);roi=a[450:650,350:1550];mask=(roi.min(2)>170)&(roi.max(2)<250)&(roi.max(2)-roi.min(2)<15);cc,ll=components(mask,100);bb=[c['box'] for c in cc if c['box'][2]-c['box'][0]>140 and c['box'][3]-c['box'][1]>50]
 if not bb:return None
 b=max(bb,key=lambda q:(q[2]-q[0])*(q[3]-q[1]));return [b[0]+350,b[1]+450,b[2]+350,b[3]+450]
cap=capsule(1140)
if cap:
 cap=[cap[0]-2,cap[1]-2,cap[2]+2,cap[3]+2];im=save_art(1140,cap,'amazon-capsule-held');im['x']=im['y']=0;cps=[];pieces={'prefix':[],'suffix':[]};a=ar(1140)
 for n in range(1130,1144):
  cb=capsule(n)
  if not cb:continue
  cb=[cb[0]-2,cb[1]-2,cb[2]+2,cb[3]+2];cps.append(dict(t=n/30,x=cb[0],y=cb[1],scaleX=(cb[2]-cb[0])/(cap[2]-cap[0]),scaleY=(cb[3]-cb[1])/(cap[3]-cap[1])));aa=ar(n)
  for name,lo,hi in [('prefix',100,cb[0]-5),('suffix',cb[2]+5,1850)]:
   reg=aa[470:625,lo:hi];mask=(reg.max(2)<225)&(reg.max(2)-reg.min(2)<25);yy,xx=np.where(mask)
   if len(xx):pieces[name].append(dict(t=n/30,box=[int(xx.min()+lo),int(yy.min()+470),int(xx.max()+lo+1),int(yy.max()+470+1)]))
 amazon.append(dict(id='early-amazon-capsule-pose',type='group',children=[im],keyframes={k:[dict(t=m['t'],value=m[k]) for m in cps] for k in ['x','y','scaleX','scaleY']}))
 for name,text in [('prefix','It brings'),('suffix','into your group chats.')]:
  mm=pieces[name]
  if not mm:continue
  b=min(mm,key=lambda q:abs(q['t']-38))['box'];l,t,r,bot=b;roi=a[t:bot,l:r];alpha=np.clip((253-roi.mean(2))/253,0,1);d,stats=trace_alpha(alpha);path=dict(id='early-amazon-'+name+'-glyphs',type='path',d=d,fill='#000000',semanticText=text,sourceFrame=1140);w=r-l;h=bot-t;tracks={'x':[],'y':[]};clipW=[]
  for m in mm:tracks['x'].append(dict(t=m['t'],value=m['box'][0]));tracks['y'].append(dict(t=m['t'],value=m['box'][1]));clipW.append(dict(t=m['t'],value=min(1,(m['box'][2]-m['box'][0])/w)))
  inner=dict(id='early-amazon-'+name+'-compensation',type='group',children=[path],keyframes={'scaleX':[dict(t=q['t'],value=1/max(.001,q['value'])) for q in clipW]});clip=dict(id='early-amazon-'+name+'-clip',type='group',clip=dict(x=0,y=-5,width=w,height=h+15),children=[inner],keyframes={'scaleX':clipW});amazon.append(dict(id='early-amazon-'+name+'-pose',type='group',children=[clip],start=mm[0]['t'],end=38.1,keyframes=tracks));ledger.append(dict(kind='complete held Amazon copy with independent reveal',semanticText=text,sourceFrame=1140,sourceBounds=b,measurements=mm,**stats))
 patch[provider['id']]={**copy.deepcopy(provider),'children':amazon}
(R/'early-end-refinement.json').write_text(json.dumps(dict(replacements=patch,new_layers=added,gradients=gradients,changed_intervals=[[5.7,8.73],[8.7,12.2],[37.65,38.1]],provenance=ledger),indent=2));print('Prepared early/end scoped replacements',list(patch),'added',len(added),flush=True)
