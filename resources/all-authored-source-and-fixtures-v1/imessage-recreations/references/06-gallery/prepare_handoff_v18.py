"""Close native108 cut and phone's measured225–239 exit; keep120–224 unchanged."""
from pathlib import Path
import json,copy,importlib.util
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw
from scipy.signal import correlate
from scipy.ndimage import label,find_objects,binary_fill_holes,binary_dilation
D=Path(__file__).resolve().parent;R=D.parent.parent;F=D/'native-transition-v18';A=D/'assets';BASE=R/'outputs/06-gallery/final-v17'
s=json.loads((BASE/'scene.json').read_text());provenance=[]
def restore(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str):o[k]=str((BASE/v).resolve())
   else:restore(v)
 elif isinstance(o,list):
  for x in o:restore(x)
restore(s)
@lru_cache(maxsize=64)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
def get(id):return next(x for x in s['layers'] if x['id']==id)
def keys(rows,k,offset=0):return [{'t':r['frame']/30,'value':float(r[k]+offset),'ease':'linear'} for r in rows if r.get(k) is not None]
def asset(name,ar,bounds,notes):
 p=A/(name+'.png');Image.fromarray(np.uint8(ar)).save(p);provenance.append({'path':str(p),'source_frame':108,'bounds':bounds,'kind':notes});return str(p)
def image(id,src,x,y,w,h,**kw):return dict(type='image',id=id,src=src,x=x,y=y,width=w,height=h,**kw)

# At108 the source cuts to the enlarged lower conversation immediately. Its camera
# then moves374px upward by120; it is not a crossfade between two phone layouts.
ref=load(120);t=(255-ref[98:275,550:1206]).mean(1);den=np.sum(t*t);poses=[]
for f in range(108,121):
 a=load(f);p=(255-a[:,550:1206]).mean(1);energy=np.r_[0,np.cumsum(np.sum(p*p,1))];dots=sum(correlate(p[:,c],t[:,c],mode='valid',method='fft') for c in range(3));alpha=dots/den;err=energy[177:]-energy[:-177]-dots*dots/den;err[(alpha<.7)|(alpha>1.3)]=1e12;k=int(np.argmin(err));sub=0.
 if 0<k<len(err)-1:
  dd=err[k-1]-2*err[k]+err[k+1]
  if dd>0:sub=float(np.clip(.5*(err[k-1]-err[k+1])/dd,-.5,.5))
 poses.append({'frame':f,'scroll':k+sub-98,'mse':float(err[k]/den)})
poses[-1]['scroll']=0.
g=get('rene-final11-group-63');g['start']=108/30;g['keyframes']['opacity']=[{'t':108/30,'value':1}];g['keyframes']['y']=keys(poses,'scroll')
thread=next(x for x in g['children'] if x['id']=='rene-final11-group-38');thread['start']=108/30;thread['keyframes']['y']=[{'t':108/30,'value':0}]+[x for x in thread['keyframes']['y'] if x['t']>=4]
for id in ['rene-final11-group-61','rene-final11-group-62']:
 q=next(x for x in g['children'] if x['id']==id);q['start']=108/30;q['keyframes']['y']=[{'t':108/30,'value':0}]+[x for x in q['keyframes']['y'] if x['t']>=4]
oldhw=g['children'][0];oldhw['start']=4
hardware=np.uint8(load(108)[:,337:1593]);rgba=np.dstack([hardware,np.full((1080,1256),255,np.uint8)]);rgba[:,54:1203,3]=0
extended=np.zeros((1800,1256,4),np.uint8);extended[:1080]=rgba;extended[1080:]=rgba[-1:]
hwpath=asset('v18-handoff-original-rails',extended,[337,0,1593,1080],'physical hardware rails only; transparent display; uniform bottom rail texture extended;108–119 only')
g['children'].insert(0,image('v18-handoff-hardware',hwpath,337,-poses[0]['scroll'],1256,1800,start=108/30,end=4))

# The already resolved upper thread scrolls out above the new lower layout. These
# are two bounded static message components, never a reference frame sequence.
a=load(108)
for name,box in [('Marcus',[428,0,1287,184]),('Priya',[428,188,1287,413])]:
 ar=np.uint8(a[box[1]:box[3],box[0]:box[2]]).copy()
 if name=='Marcus':
  ar[:153,765-box[0]:1164-box[0]]=230
  ar[153:,765-box[0]:1164-box[0]]=255
 mask=binary_dilation(binary_fill_holes(ar.min(2)<242),iterations=1);rgba=np.dstack([ar,np.uint8(mask)*255]);src=asset('v18-handoff-'+name.lower(),rgba,box,'bounded static message block with screen background removed; internal copy bitmap; camera and lifecycle independently editable')
 q=image('v18-handoff-'+name,src,box[0],box[1]-poses[0]['scroll'],box[2]-box[0],box[3]-box[1],start=108/30,end=4)
 g['children'].insert(1,q)
# Header and thread move independently. The small occluded Marcus region becomes
# plain gray before it is uncovered, while the actual pill follows its own camera.
pill=np.uint8(a[76:184,765:1164]);mask=Image.new('L',(399,108));ImageDraw.Draw(mask).rounded_rectangle((0,0,398,107),radius=54,fill=255);pill=np.dstack([pill,np.array(mask)]);src=asset('v18-cabin-header-pill',pill,[765,76,1164,184],'bounded static native group-title pill UI; independently measured sticky-header camera')
avatar=np.uint8(a[:93,861:1063]);mask=Image.new('L',(202,93));ImageDraw.Draw(mask).ellipse((0,-110,201,92),fill=255);avatar=np.dstack([avatar,np.array(mask)]);ap=asset('v18-cabin-group-avatar',avatar,[861,0,1063,93],'genuine group avatar artwork; bounded partial circle, independent header camera')
hp=[{'frame':108,'y':0.},{'frame':109,'y':-69.},{'frame':110,'y':-125.}]
head=dict(type='group',id='v18-sticky-header',start=108/30,end=111/30,children=[image('v18-cabin-avatar',ap,861,-poses[0]['scroll'],202,93),image('v18-cabin-pill',src,765,76-poses[0]['scroll'],399,108)],keyframes={'y':[{'t':p['frame']/30,'value':p['y']-next(z['scroll'] for z in poses if z['frame']==p['frame'])+poses[0]['scroll']} for p in hp]})
g['children'].append(head)

# Wanted follow-up fades/bounces independently as the camera arrives.
want=next(x for x in thread['children'] if x['id']=='source-message-art-Want');art=np.array(Image.open(want['src']).convert('RGB')).astype(float);tp=(255-art[:,50:550]).mean(1);H=len(tp);ys=np.arange(450,1080);world=np.arange(1080)[None,:];idx=world-ys[:,None];valid=(idx>=0)&(idx<H);models=(tp[np.clip(idx,0,H-1)]*valid[:,:,None]).reshape(len(ys),-1);den=np.sum(models*models,1);wr=[]
for p in poses:
 f=p['frame'];obs=(255-load(f)[:,600:1100]).mean(1);dots=models@obs.ravel();alpha=dots/np.maximum(1,den);energy=valid@np.sum(obs*obs,1);err=np.maximum(0,energy-dots*dots/np.maximum(1,den))/np.maximum(energy,1);expected=502+p['scroll'];err[(ys<expected-20)|(ys>expected+80)|(alpha<.1)|(alpha>1.4)]=1e6;k=int(np.argmin(err));wr.append({'frame':f,'y':float(ys[k]-p['scroll']),'opacity':float(np.clip(alpha[k],0,1))})
want['keyframes']={'y':keys(wr,'y'),'opacity':keys(wr,'opacity')}
# Keep original fully resolved post120 artwork and poses exactly.
want['keyframes']['y'][-1]['value']=502;want['keyframes']['opacity'][-1]['value']=1.

# Track the whole phone's horizontal departure rather than holding its7.5s pose.
def rails(ar):
 p=ar[300:900].mean(axis=(0,2));labs,n=label(p<85);cc=[]
 for sl in find_objects(labs):
  if sl is None:continue
  x=sl[0];w=x.stop-x.start
  if 7<w<40:cc.append((x.start+x.stop)/2)
 return cc
native=np.array(Image.open(R/'outputs/06-gallery/frames-gsap/000225.png').convert('RGB')).astype(float);nrails=rails(native);baseleft=nrails[0];baseright=nrails[-1];exit=[]
for f in range(225,240):
 rr=rails(load(f));value=(rr[0]-baseleft if len(rr)>1 else rr[-1]-baseright) if rr else -1500;exit.append({'frame':f,'x':value-6})
# Actual X stays still through222; the earlier linear6.5→7.5 drift moved every
# letter and both metal rails5px too far left before the real exit began.
r195=rails(np.array(Image.open(D/'keyframes/006.50.png').convert('RGB')).astype(float));fullx=[]
for f in range(196,240):
 rr=rails(load(f));value=(rr[0]-r195[0] if len(rr)>1 else rr[-1]-r195[-1]) if rr else -1600;fullx.append({'frame':f,'x':value})
g['keyframes']['x']=[q for q in g['keyframes']['x'] if q['t']<=6.5]+keys(fullx,'x');xf={q['frame']:q['x'] for q in fullx}
# Composer cross and keyboard-color boundaries give independent physical camera
# cues; their actual7.5 composer offset is−91, not the old−102 estimate.
comp=next(q for q in g['children'] if q['id']=='rene-final11-group-61');kb=next(q for q in g['children'] if q['id']=='rene-final11-group-62');compmore=[];kbmore=[];lastplus=820.;lastkb=None
from scipy.ndimage import map_coordinates
for f in range(196,240):
 a=load(f);dx=xf[f];x0=int(round(470+dx));x1=int(round(520+dx));cross=[]
 if x0>=0 and x1<1920:
  labs,n=label(a[:,x0:x1].max(2)<70)
  for sl in find_objects(labs):
   if sl is None:continue
   yy,xx=sl
   if 24<xx.stop-xx.start<45 and 24<yy.stop-yy.start<45 and yy.start>600:cross.append(yy.start)
 if cross:lastplus=float(cross[0])
 else:lastplus-=.84
 compmore.append({'frame':f,'y':lastplus-886})
 cols=np.arange(800,1100)+dx;valid=(cols>=0)&(cols<1919)
 if valid.sum()>30:
  wy,wx=np.meshgrid(np.arange(850,1080),cols[valid],indexing='ij');colors=np.stack([map_coordinates(a[:,:,c],[wy,wx],order=1) for c in range(3)],2);mask=(colors[:,:,2]-colors[:,:,0]>2)&(colors.mean(2)<244)&(colors.mean(2)>180);rows=np.where(mask.sum(1)>valid.sum()*.5)[0]
  if len(rows):lastkb=float(rows.min()+850-1010)
 if lastkb is None:lastkb=-66.
 kbmore.append({'frame':f,'y':lastkb})
comp['keyframes']['y']=[q for q in comp['keyframes']['y'] if q['t']<=6.5]+keys(compmore,'y');kb['keyframes']['y']=[q for q in kb['keyframes']['y'] if q['t']<=6.5]+keys(kbmore,'y')
# The thread continues its slow vertical drift during the horizontal departure.
# Constrain the Done-template search to its actual settled neighborhood; the old
# unconstrained matcher twice attached it to the composer at222/223.
reference=load(225).mean(2);sr=rails(load(225));late=[];last=535.
for f in range(219,240):
 rr=rails(load(f));dx=(rr[0]-sr[0] if len(rr)>1 else rr[-1]-sr[-1]) if rr else -1600;cols=np.arange(600,1080);wc=cols+dx;valid=(wc>=0)&(wc<1919);cols=cols[valid];wc=wc[valid]
 if len(cols)<15:body=last-.7
 else:
  a=load(f).mean(2);wy=np.arange(1080)[:,None]+np.zeros((1,len(wc)));wx=np.zeros((1080,1))+wc[None,:]
  from scipy.ndimage import map_coordinates
  prof=np.maximum(0,250-map_coordinates(a,[wy,wx],order=1)).mean(1);tp=np.maximum(0,250-reference[535:656,cols]).mean(1);ener=np.r_[0,np.cumsum(prof*prof)];dots=correlate(prof,tp,mode='valid',method='fft');err=ener[121:]-ener[:-121]+np.sum(tp*tp)-2*dots;err[:515]=1e12;err[556:]=1e12;at=int(np.argmin(err));sub=0.
  if 0<at<len(err)-1:
   den=err[at-1]-2*err[at]+err[at+1]
   if den>0:sub=float(np.clip(.5*(err[at-1]-err[at+1])/den,-.5,.5))
  body=at+sub
 late.append({'frame':f,'y':body-1235,'done_body_y':body});last=body
thread['keyframes']['y']=[q for q in thread['keyframes']['y'] if q['t']<219/30]+keys(late,'y')
done=next(q for q in thread['children'] if q['id']=='rene-final11-group-37');done['keyframes']['y']=[q for q in done['keyframes']['y'] if q['t']<219/30]+[{'t':219/30,'value':0}]
get('g-1129')['start']=get('g-1129')['end'] # suppress its obsolete108–119 crossfade
(D/'handoff-v18-poses.json').write_text(json.dumps({'camera':poses,'wanted':wr,'phoneExit':fullx,'nativeRails225':nrails,'lateThread':late,'lateComposer':compmore,'lateKeyboard':kbmore},indent=2))
(D/'assets/handoff-v18-provenance.json').write_text(json.dumps(provenance,indent=2))
(D/'scene-handoff-v18.json').write_text(json.dumps(s,indent=2)+'\n');print('camera',poses);print('exit',exit)
(D/'handoff-v18-patch.json').write_text(json.dumps({'replace':{id:get(id) for id in ['g-1129','rene-final11-group-63']}},indent=2))
