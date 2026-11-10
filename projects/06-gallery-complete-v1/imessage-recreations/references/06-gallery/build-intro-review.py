"""Measured Rene0–3.6 opening: independent message poses and explicit frame54 edit.
Bounded original static app/message artwork; native camera/alpha/lifetimes. No full-frame playback.
"""
from pathlib import Path
from functools import lru_cache
import json,hashlib,copy
import numpy as np
from PIL import Image,ImageDraw
from scipy import signal,ndimage
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';P=R/'verification/fidelity-review/06-intro';AS=REF/'assets/intro-review';AS.mkdir(exist_ok=True);ledger=[];measure={}
@lru_cache(maxsize=8)
def frame(f):return np.array(Image.open(P/'source'/f'{f+1:04d}.png').convert('RGB')).astype('float32')
def box(mask):
 y,x=np.where(mask);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def ink(a,white=238):return np.clip((white-a.mean(2))/(white-15),0,1).astype('float32')
def art(f,b,name,semantic,mask=None):
 a=frame(f)[b[1]:b[3],b[0]:b[2]].copy();alpha=np.clip((255-a.min(2))/255,0,1);alpha[alpha<2/255]=0
 if mask is not None:alpha*=mask
 rgb=np.where(alpha[:,:,None]>0,(a-255*(1-alpha[:,:,None]))/np.maximum(1e-5,alpha[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),alpha[:,:,None]*255),2).round().astype('uint8');p=AS/(name+'.png');Image.fromarray(rgba).save(p);ledger.append(dict(id=name,sourceFrame=f,sourceBounds=b,sourceSHA256=hashlib.sha256((P/'source'/f'{f+1:04d}.png').read_bytes()).hexdigest(),asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),semanticText=semantic,editability='Bounded original static product UI/message artwork; native independent pose, alpha and lifetime; bitmap internals.'));return dict(type='image',id=name,src=str(p),x=b[0],y=b[1],width=b[2]-b[0],height=b[3]-b[1],semanticText=semantic,sourceFrame=f,sourceBounds=b)
def energy(T,h,w):
 s=np.pad((T.astype('float64')**2).cumsum(0).cumsum(1),((1,0),(1,0)));return s[h:,w:]-s[:-h,w:]-s[h:,:-w]+s[:-h,:-w]
def match(T,A,s):
 w=max(2,round(A.shape[1]*s));h=max(2,round(A.shape[0]*s));M=np.asarray(Image.fromarray(A,'F').resize((w,h),Image.Resampling.BILINEAR));
 if h>T.shape[0] or w>T.shape[1]:return None
 den=energy(T,h,w)*float((M*M).sum());corr=signal.fftconvolve(T,M[::-1,::-1],mode='valid');scores=np.where(den>1e-7,corr/np.sqrt(np.maximum(1e-9,den)),-1)
 if float(scores.max())>1.01:raise ValueError('Impossible normalized correlation')
 y,x=np.unravel_index(np.argmax(scores),scores.shape);a=float((T[y:y+h,x:x+w]*M).sum()/max(1e-8,float((M*M).sum())));return dict(score=float(scores[y,x]),x=int(x),y=int(y),sx=w/A.shape[1],sy=h/A.shape[0],alpha=min(1.0,a),s=s)
def fit(f,A,roi,guess,spread=.07):
 T=ink(frame(f)[roi[1]:roi[3],roi[0]:roi[2]]);qs=[q for s in np.linspace(guess*(1-spread),guess*(1+spread),5) if (q:=match(T,A,float(s))) is not None]
 if not qs:return None
 q=max(qs,key=lambda q:q['score']);best=q
 for s in np.linspace(max(.2,q['s']-.025),q['s']+.025,5):
  q=match(T,A,float(s))
  if q and q['score']>best['score']:best=q
 best['x']+=roi[0];best['y']+=roi[1];return best
# Rough physical text scale from independent gray message bounds, excluding the header by left edge.
rough={}
for f in range(1,108):
 a=frame(f);m=(a.max(2)<242)&(a.min(2)>210)&(a.max(2)-a.min(2)<6);m=ndimage.binary_closing(m,iterations=2);lab,n=ndimage.label(m);cs=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if 300<xx.start<740 and w>250 and 50<h<400 and yy.start>180:cs.append((yy.start,w))
 rough[f]=(sorted(cs)[0][1]/438) if cs else (rough.get(f-1,2.46))
# Canonical semantic messages. Source69 supplies stable first3, source99 supplies Rene.
configs=[('marcus',69,[594,540,1121,714],[704,604,1109,682],1,108,'Marcus: We’ve been talking about this trip since January'),('priya',69,[594,709,1187,879],[704,774,1176,850],29,108,'Priya: Someone just pick a weekend, I’m not the mom of this group'),('dan',69,[594,875,1134,1044],[704,940,1125,1018],54,108,'Dan: Not me, I organized the last one'),('rene',99,[594,850,1135,1004],[704,900,1128,981],76,108,'Rene: Oct17 is the first weekend all of you are free')];nodes=[];observed={}
for name,cf,cb,tb,first,last,text in configs:
 # Tight text core eliminates gray bubble/background from the correlation template.
 raw=ink(frame(cf)[tb[1]:tb[3],tb[0]:tb[2]]);bb=box(raw>.08);assert bb;A=raw[bb[1]:bb[3],bb[0]:bb[2]];tx=tb[0]+bb[0];ty=tb[1]+bb[1];node=art(cf,cb,'rene-intro-'+name,text);obs=[]
 for f in range(first,last):
  roi=[300,300,1500,1080] if name=='marcus' else ([300,600,1550,1080] if f<54 else [590,450 if name=='priya' else 600 if name=='dan' else 760,1300,1080]);guess=rough[f] if f<54 or name=='marcus' else rough[f];q=fit(f,A,roi,guess,spread=.09)
  if not q or q['score']<.70 or q['alpha']<.035:continue
  obs.append(dict(frame=f,correlation=q['score'],x=q['x']+q['sx']*(cb[0]-tx),y=q['y']+q['sy']*(cb[1]-ty),scaleX=q['sx'],scaleY=q['sy'],opacity=q['alpha']))
 assert obs,name
 node['x']=node['y']=0;node['start']=obs[0]['frame']/30;node['end']=108/30;node['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','opacity']};nodes.append(node);measure[name]=obs;observed[name]=(obs,dict(cb=cb,tx=tx,ty=ty,A=A));print(name,len(obs),obs[0]['frame'],min(q['correlation'] for q in obs),flush=True)
# iMessage/date is independently timed. Source69 static artwork follows measured word camera;
# header draws above it during scroll so the date naturally disappears behind navigation.
cf=69;cb=[855,484,1080,539];tb=[855,484,1080,539];raw=ink(frame(cf)[cb[1]:cb[3],cb[0]:cb[2]],white=250);bb=box(raw>.1);A=raw[bb[1]:bb[3],bb[0]:bb[2]];tx=cb[0]+bb[0];ty=cb[1]+bb[1];date=art(cf,cb,'rene-intro-date','iMessage / Today12:01AM');obs=[]
for f in range(23,108):
 if f>=76:continue
 roi=[600,100,1300,780];q=fit(f,A,roi,min(2.4,rough[f]),spread=.12)
 if not q or q['score']<.78 or q['alpha']<.03:continue
 obs.append(dict(frame=f,correlation=q['score'],x=q['x']+q['sx']*(cb[0]-tx),y=q['y']+q['sy']*(cb[1]-ty),scaleX=q['sx'],scaleY=q['sy'],opacity=q['alpha']))
if obs:
 date['x']=date['y']=0;date['start']=obs[0]['frame']/30;date['end']=(obs[-1]['frame']+1)/30;date['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','opacity']};nodes.insert(0,date);measure['date']=obs
# Before frame54 the source is a cropped screen. Hardware sides are separate from chat scroll.
pre=[];refm=next(q for q in measure['marcus'] if q['frame']==39)
for name,b in [('left',[170,0,250,1080]),('right',[1680,0,1755,1080])]:
 node=art(39,b,'rene-intro-precut-'+name,'Original cropped phone '+name+' hardware');obs=[]
 for f in range(28,54):
  m=next((q for q in measure['marcus'] if q['frame']==f),None)
  if m is None:continue
  sx=m['scaleX']/refm['scaleX'];sy=m['scaleY']/refm['scaleY'];x=m['x']-refm['x']*sx+b[0]*sx;y=m['y']-refm['y']*sy
  # Measured source opacity of the dark physical side at its predicted coordinate.
  xl=max(0,round(x));xh=min(1920,round(x+node['width']*sx));D=255-frame(f)[100:1000,xl:xh].min(2);alpha=min(1,float(np.percentile(D,99))/248) if D.size else 0;obs.append(dict(frame=f,x=x,y=y,scaleX=sx,scaleY=sy,opacity=alpha))
 node['x']=node['y']=0;node['start']=28/30;node['end']=54/30;node['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','opacity']};pre.append(node);measure['pre-hardware-'+name]=obs
# Composer plus provides a reliable independent pose; field/placeholder/microphone follow it.
cb=[300,960,1625,1080];node=art(39,cb,'rene-intro-precut-composer','Plus / iMessage composer / microphone');tb=[335,1004,400,1080];raw=ink(frame(39)[tb[1]:tb[3],tb[0]:tb[2]]);bb=box(raw>.15);A=raw[bb[1]:bb[3],bb[0]:bb[2]];tx=tb[0]+bb[0];ty=tb[1]+bb[1];obs=[]
for f in range(29,54):
 q=fit(f,A,[200,880,650,1080],rough[f]/rough[39],spread=.12)
 if not q or q['score']<.70 or q['alpha']<.025:continue
 obs.append(dict(frame=f,x=q['x']+q['sx']*(cb[0]-tx),y=q['y']+q['sy']*(cb[1]-ty),scaleX=q['sx'],scaleY=q['sy'],opacity=q['alpha'],correlation=q['score']))
if obs:
 node['x']=node['y']=0;node['start']=obs[0]['frame']/30;node['end']=54/30;node['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','opacity']};nodes.append(node);measure['composer']=obs
# Actual native full-phone header/hardware begins at an edit on54, not a slow zoom.
reference=frame(69);cam=[]
for f in range(54,108):
 a=frame(f);dark=a.max(2)<90;ct=dark[100:].sum(0);xs=np.where(ct>200)[0];left=xs[xs<900];right=xs[xs>1000];L=int(left.max());RR=int(right.min());s=(RR-L)/(1358-567);x=L-567*s
 # First dense dark row is the top bezel (before the island/status UI).
 counts=dark[:350,max(0,int(x+550*s)):min(1920,int(x+1375*s))].sum(1);ys=np.where(counts>max(30,100*s))[0];top=int(ys.min());y=top-93*s;cam.append(dict(frame=f,x=x,y=y,scaleX=s,scaleY=s,sourceInnerBezel=[L,RR],sourceTop=top))
# Ring with a transparent screen hole. This contains no foreground UI.
b=[530,80,1395,1080];mask=Image.new('L',(b[2]-b[0],b[3]-b[1]),255);draw=ImageDraw.Draw(mask);draw.rounded_rectangle((568-b[0],110-b[1],1358-b[0],2000-b[1]),radius=95,fill=0);hardware=art(69,b,'rene-intro-postcut-hardware','Original phone bezel only, transparent screen',np.array(mask)/255)
# Header panel is one bounded static UI element; native camera stays independent of messages.
bh=[568,110,1358,449];hm=Image.new('L',(bh[2]-bh[0],bh[3]-bh[1]),0);ImageDraw.Draw(hm).rounded_rectangle((0,0,bh[2]-bh[0],2000),radius=95,fill=255);header=art(69,bh,'rene-intro-postcut-header','Status bar / group avatar / Cabin trip / navigation',np.array(hm)/255)
post=[]
for node in [hardware,header]:
 bx,by=node['x'],node['y'];node['x']=node['y']=0;node['start']=54/30;node['end']=108/30;node['keyframes']={k:[dict(t=q['frame']/30,value=(q[k]+bx*q['scaleX'] if k=='x' else q[k]+by*q['scaleY'] if k=='y' else q[k]),ease='linear') for q in cam] for k in ['x','y','scaleX','scaleY']};post.append(node)
measure['post-camera']=cam
# Header is above chat and date. The screen's white fill is native geometry.
children=[dict(type='rect',id='rene-intro-white-screen',x=560,y=110,width=800,height=1900,radius=95,fill='#ffffff',start=54/30,end=108/30)]+pre+nodes+post
spec={'replace_ids':['g-1079'],'gate_overrides':{'g-1129':{'start':108/30}},'insert_before':{'g-1129':[dict(type='group',id='rene-measured-intro-before36',start=0,end=108/30,children=children)]},'changed_frame_ranges':[[0,107]],'measurements':measure,'assets':ledger,'notice':'Measured0–3.6 native camera/state prototype; independent bounded static UI/message artwork with explicit edit54. Bitmap internal copy and hardware inference limits disclosed. No whole-frame/video playback. Parent/builder handoff108–119 still required.'}
(REF/'intro-review-elements.json').write_text(json.dumps(spec,indent=2));(REF/'intro-review-provenance.json').write_text(json.dumps(dict(assets=ledger,notice=spec['notice']),indent=2));print('done',len(children),'assets',len(ledger))
