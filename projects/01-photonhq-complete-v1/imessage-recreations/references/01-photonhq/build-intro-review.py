"""Rebuild source01 intro with neutral per-word measurements and bounded gradient art."""
from pathlib import Path
from functools import lru_cache
import json,copy,hashlib,sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
ROOT=Path('/workspace/imessage-recreations');REF=ROOT/'references/01-photonhq';P=ROOT/'verification/fidelity-review/01-intro';AS=REF/'assets/intro-review';AS.mkdir(exist_ok=True)
base=json.loads((REF/'scene-intro-base-v4.json').read_text());byid={l['id']:l for l in base['layers']};ledger=[];measurements={}
@lru_cache(maxsize=24)
def frame(n):
 if 42<=n<=55:p=P/'source-full-early-pill'/f'{n-41:04d}.png';y=0
 elif 192<=n<=203:p=P/'source-full-free-entry'/f'{n-191:04d}.png';y=0
 else:p=P/'source-crops'/f'{n+1:04d}.png';y=350
 return np.array(Image.open(p).convert('RGB')),y,p

def region(n,box):
 a,oy,_=frame(n);x0,y0,x1,y1=map(int,box);out=np.full((y1-y0,x1-x0,3),255,np.uint8);ya,yb=max(y0,oy),min(y1,oy+a.shape[0]);xa,xb=max(0,x0),min(1920,x1)
 if xb>xa and yb>ya:out[ya-y0:yb-y0,xa-x0:xb-x0]=a[ya-oy:yb-oy,xa:xb]
 return out

def neutral_alpha(n,box):
 a=region(n,box).astype(float);alpha=np.clip((255-a.mean(2))/255,0,1);alpha[a.max(2)-a.min(2)>12]=0;return alpha

def bbox(m,x0=0,y0=0):
 yy,xx=np.where(m)
 return [int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)] if len(xx) else None

def black_box(n,box):
 a=neutral_alpha(n,box);pk=float(a.max());m=a>max(.025,pk*.5);b=bbox(m,box[0],box[1]);return b,pk,a

def color_box(n,box,relative=.20):
 a=region(n,box).astype(float);c=np.maximum(0,a[:,:,2]-a[:,:,0]);c[a[:,:,2]<a[:,:,1]-3]=0;pk=float(c.max());b=bbox(c>max(5,pk*relative),box[0],box[1]);return b,pk,c

def tk(values):return [dict(t=n/30,value=float(v),ease='linear') for n,v in values]
def tracks(obs):return {k:tk([(q['frame'],q[k]) for q in obs]) for k in ['x','y','scaleX','scaleY','opacity']}
def geometry(b,cb,opacity=1):
 sx=(b[2]-b[0])/(cb[2]-cb[0]);sy=(b[3]-b[1])/(cb[3]-cb[1]);return dict(x=b[0]-cb[0]*sx,y=b[1]-cb[1]*sy,scaleX=sx,scaleY=sy,opacity=float(np.clip(opacity,0,1)))

def native_path(n,box,text,id):
 aa=neutral_alpha(n,box);b=bbox(aa>.5,box[0],box[1]);roi=[max(box[0],b[0]-2),max(box[1],b[1]-2),min(box[2],b[2]+2),min(box[3],b[3]+2)];alpha=neutral_alpha(n,roi);d,stats=trace_alpha(alpha,roi[0],roi[1]);ledger.append(dict(id=id,kind='native glyph outlines',semanticText=text,sourceFrame=n,sourceBounds=roi,coreBounds=b,sourceSHA256=hashlib.sha256(frame(n)[2].read_bytes()).hexdigest(),**stats));return dict(type='path',id=id,d=d,fill='#000000',semanticText=text,sourceFrame=n,sourceBounds=roi,editability='Native editable glyph contours; original semantic copy retained, not live font text.'),b,aa

def art(n,box,name,text):
 box=[max(0,int(box[0])),max(0,int(box[1])),min(1920,int(box[2])),min(1080,int(box[3]))];a=region(n,box);path=AS/(name+'.png');Image.fromarray(a).save(path);ledger.append(dict(id=name,kind='bounded original gradient word graphic',semanticText=text,sourceFrame=n,sourceBounds=box,asset=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),editability='Independent bitmap gradient/glyph-color artwork; native pose/lifetime editable.'))
 return dict(type='image',id='intro-art-'+name,src=str(path),x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1],semanticText=text,sourceFrame=n,sourceBounds=box)

# Frame0 is a decoded fully composed source artifact before the intended reset.
intro=[];p0,_,_=native_path(0,[0,400,970,680],'Introducing','intro-black-artifact-0');intro.append(dict(type='group',id='intro-artifact-0',start=0,end=1/30,children=[p0]));bb,_,_=color_box(0,[970,400,1920,680]);ab=art(0,[bb[0]-3,bb[1]-3,bb[2]+3,bb[3]+3],'photon-artifact-0','Photon2.0');ab.update(start=0,end=1/30);intro.append(ab)
p,cb,_=native_path(15,[0,400,970,680],'Introducing','intro-black-main');obs=[]
for n in range(1,45):
 b,pk,aa=black_box(n,[0,400,970,680])
 if b and b[2]-b[0]>100 and b[3]-b[1]>20:obs.append(dict(frame=n,sourceBounds=b,**geometry(b,cb,pk)))
p.update(start=obs[0]['frame']/30,end=(obs[-1]['frame']+1)/30,keyframes=tracks(obs));intro.append(p);measurements['Introducing']=obs
# The short gradient typing reveal changes individual glyph colors/coverage; it is
# retained as bounded word poses, separately from the native black-word path.
for n in range(1,15):
 b,pk,_=color_box(n,[970,400,1920,700])
 if not b or pk<7:continue
 a=art(n,[b[0]-3,b[1]-3,b[2]+3,b[3]+3],f'photon-typing-{n}','Photon2.0 typing reveal');a.update(start=n/30,end=(n+1)/30);intro.append(a)
bcb,bpk,_=color_box(15,[970,400,1920,700]);a=art(15,[bcb[0]-3,bcb[1]-3,bcb[2]+3,bcb[3]+3],'photon-held','Photon2.0');obs=[]
for n in range(15,45):
 b,pk,_=color_box(n,[970,400,1920,700])
 if b and pk>7:
  v=geometry(b,bcb,min(1,pk/bpk));v['x']+=a['x']*v['scaleX'];v['y']+=a['y']*v['scaleY'];obs.append(dict(frame=n,sourceBounds=b,**v))
a.update(start=15/30,end=45/30,x=0,y=0,keyframes=tracks(obs));intro.append(a);measurements['Photon2.0']=obs
replacements={'group-3':dict(type='group',id='group-3',start=0,end=1.5,children=intro)}

# Split the canonical isolated phrase at its three actual spaces, then identify
# each visible source word by normalized glyph-shape correlation.
def make_words(n,roi,tokens,prefix):
 aa=neutral_alpha(n,roi);xs=np.where((aa>.5).any(0))[0];gaps=np.diff(xs);inds=sorted(np.argsort(gaps)[-(len(tokens)-1):]);splits=[(int(xs[i])+int(xs[i+1]))//2 for i in inds];bounds=[roi[0]]+[v+roi[0] for v in splits]+[roi[2]];templates=[]
 internal=max([float(gaps[i]) for i in range(len(gaps)) if i not in inds],default=6);space=min([float(gaps[i]) for i in inds],default=25);gap_threshold=(internal+space)/2
 for i,(lo,hi,text) in enumerate(zip(bounds,bounds[1:],tokens)):
  box=[lo,roi[1],hi,roi[3]];path,cb,_=native_path(n,box,text,prefix+'-'+str(i));alpha=neutral_alpha(n,cb);templates.append(dict(node=path,cb=cb,alpha=alpha,text=text,obs=[]))
 return templates,gap_threshold

def find_groups(n,roi,gap):
 aa=neutral_alpha(n,roi);m=aa>.06;lab,num=ndimage.label(m,np.ones((3,3)));good=np.zeros(m.shape,bool)
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;h=yy.stop-yy.start;w=xx.stop-xx.start
  if 5<=h<=125 and w>=2 and np.count_nonzero(lab[sl]==j)>5:good[sl]|=lab[sl]==j
 xs=np.where(good.any(0))[0]
 if not len(xs):return []
 cut=[0]+[i+1 for i,v in enumerate(np.diff(xs)) if v>gap]+[len(xs)];out=[]
 for lo,hi in zip(cut,cut[1:]):
  x0,x1=int(xs[lo]),int(xs[hi-1]+1);sub=aa[:,x0:x1];peak=float(sub.max());core=sub>max(.025,peak*.5);bb=bbox(core,roi[0]+x0,roi[1])
  if bb and bb[2]-bb[0]>6 and bb[3]-bb[1]>6:out.append(dict(box=bb,alpha=neutral_alpha(n,bb),peak=peak))
 return out

def fit_candidate(template,cand):
 cb=template['cb'];b=cand['box'];w,h=b[2]-b[0],b[3]-b[1];A=template['alpha'];B=cand['alpha'];pred=np.asarray(Image.fromarray(A.astype('float32'),'F').resize((w,h),Image.Resampling.BILINEAR));den=np.sqrt((pred*pred).sum()*(B*B).sum());score=float((pred*B).sum()/max(1e-9,den));v=geometry(b,cb,cand['peak']);mode='full'
 # Native viewport clipping is a visible intersection, not a request to shrink
 # the original word. Retain the measured scale and anchor its opposite edge.
 if b[0]<=1 or b[2]>=1919:
  sy=h/(cb[3]-cb[1]);last=template['obs'][-1] if template['obs'] else None;ratio=(last['scaleX']/last['scaleY']) if last else 1;sx=sy*ratio;cw=min(A.shape[1],max(1,round(w/max(.01,sx))));piece=A[:,-cw:] if b[0]<=1 else A[:,:cw];pr=np.asarray(Image.fromarray(piece.astype('float32'),'F').resize((w,h),Image.Resampling.BILINEAR));sc=float((pr*B).sum()/max(1e-9,np.sqrt((pr*pr).sum()*(B*B).sum())))
  if sc>score:
   score=sc;mode='left-clipped' if b[0]<=1 else 'right-clipped';v=dict(x=(b[2]-cb[2]*sx if b[0]<=1 else b[0]-cb[0]*sx),y=b[1]-cb[1]*sy,scaleX=sx,scaleY=sy,opacity=cand['peak'])
 return score,v,mode

def measure_words(templates,gap,frames,roi_fn):
 for n in frames:
  roi=roi_fn(n);cs=find_groups(n,roi,gap);rank=[]
  for ci,c in enumerate(cs):
   for ti,t in enumerate(templates):
    score,v,mode=fit_candidate(t,c)
    if score>.73:rank.append((score,ci,ti,v,mode,c['box']))
  usedc=set();usedt=set();chosen=[]
  for score,ci,ti,v,mode,bb in sorted(rank,reverse=True,key=lambda q:q[0]):
   if ci in usedc or ti in usedt:continue
   usedc.add(ci);usedt.add(ti);chosen.append((ti,ci,score,v,mode,bb))
  # Words preserve left-to-right semantic order; discard a crossing low-score match.
  for ti,ci,score,v,mode,bb in chosen:
   if any((tj-ti)*(cj-ci)<0 and sj>score for tj,cj,sj,*_ in chosen):continue
   templates[ti]['obs'].append(dict(frame=n,sourceBounds=bb,correlation=score,clip=mode,**v))
 for t in templates:
  if not t['obs']:raise RuntimeError('No source observations for '+t['text'])
  node=t['node'];obs=t['obs'];node.update(start=obs[0]['frame']/30,end=(obs[-1]['frame']+1)/30,keyframes=tracks(obs));measurements[node['id']]=obs
 return [t['node'] for t in templates]

phr,gap=make_words(120,[0,420,1920,700],['With','just','one','click'],'intro-click-word');phnodes=measure_words(phr,gap,range(76,127),lambda n:[0,420,1920,700]);replacements['text-9-source-outline']=dict(type='group',id='text-9-source-outline',children=phnodes,start=min(c['start'] for c in phnodes),end=max(c['end'] for c in phnodes))

def icon_left(n):
 a=region(n,[0,350,1920,800]).astype(float);m=(a.max(2)-a.min(2)>50)&(a.min(2)<220)&(a.max(2)>140);m=ndimage.binary_closing(m,iterations=2);lab,num=ndimage.label(m,np.ones((3,3)));xs=[]
 for sl in ndimage.find_objects(lab):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w>28 and h>28 and .65<w/h<1.4:xs.append(xx.start)
 return min(xs) if xs else 1920

def your_roi(n):return [0,420,max(300,icon_left(n)-12),700]
yr=your_roi(150);yours,gap=make_words(150,yr,['Your','agent','is','everywhere'],'intro-your-word');ynodes=measure_words(yours,gap,range(123,174),your_roi);replacements['text-10-source-outline']=dict(type='group',id='text-10-source-outline',children=ynodes,start=min(c['start'] for c in ynodes),end=max(c['end'] for c in ynodes))

# Pill geometry is measured relative to its own contrast, then alpha is measured
# separately; unrelated square channel icons cannot extend its lifetime.
pill=copy.deepcopy(byid['group-6-source-pill']);canon=60

def pill_bounds(n):
 a=region(n,[0,150,1600,900]).astype(float);c=np.maximum(0,a[:,:,2]-a[:,:,0]);pk=float(c.max());m=(c>max(6,pk*.20))&(a[:,:,2]>a[:,:,1]-4);lab,num=ndimage.label(m,np.ones((3,3)));cands=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w>120 and h>50 and w/h>1.5:cands.append((w*h,[xx.start,yy.start+150,xx.stop,yy.stop+150],float(c[sl].max())))
 if not cands:return None
 _,bb,peak=max(cands);return bb,peak
pc,pp=pill_bounds(canon);obs=[]
for n in range(40,126):
 q=pill_bounds(n)
 if not q:continue
 b,pk=q;opacity=min(1,pk/pp);opacity=1 if opacity>.92 else opacity;v=geometry(b,pc,opacity);v['x']+=pill['x']*v['scaleX'];v['y']+=pill['y']*v['scaleY'];obs.append(dict(frame=n,sourceBounds=b,peak_chroma=pk,**v))
pill.update(x=0,y=0,start=obs[0]['frame']/30,end=(obs[-1]['frame']+1)/30,keyframes=tracks(obs));replacements[pill['id']]=pill;measurements['pill']=obs

free,gap=make_words(225,[0,400,1920,750],['And','it’s','for','everyone.'],'intro-free-word');fnodes=measure_words(free,gap,range(192,240),lambda n:[0,350,1920,1080] if n<=203 else [0,400,1920,750]);blue=[]
for n in range(192,204):
 # At entry the word's lower gradient is masked dynamically. Keep only the
 # independently bounded gradient word pose, never a full title/frame.
 b,pk,_=color_box(n,[700,400,1050,1080],relative=.04)
 if b and pk>15 and n>=196:
  a=art(n,[b[0]-3,b[1]-3,b[2]+3,b[3]+3],f'free-entry-{n}','free gradient entry');a.update(start=n/30,end=(n+1)/30);blue.append(a)
cb,pk,_=color_box(225,[700,400,1050,750],relative=.2);a=art(225,[cb[0]-3,cb[1]-3,cb[2]+3,cb[3]+3],'free-held','free');obs=[]
for n in range(204,240):
 b,k,_=color_box(n,[650,400,1100,750],relative=.2)
 if b:
  v=geometry(b,cb,min(1,k/pk));v['x']+=a['x']*v['scaleX'];v['y']+=a['y']*v['scaleY'];obs.append(dict(frame=n,sourceBounds=b,**v))
a.update(x=0,y=0,start=204/30,end=8,keyframes=tracks(obs));blue.append(a);measurements['free-gradient']=obs
newfree=dict(type='group',id='intro-free-before8',start=196/30,end=8,children=fnodes+blue);keptfree=copy.deepcopy(byid['group-27']);keptfree['start']=8;replacements['group-27']=keptfree
spec=dict(replacements=replacements,insert_before={'group-27':[newfree]},changed_frame_ranges=[[0,162],[196,239]],assets=ledger,measurements=measurements,notice='Intro review prototype pending native comparison. All black copy is native per-word glyph outlines. Short original bounded gradient-word entry/typing poses are bitmap, native pose/lifetime editable. Pill underlay remains the accepted symmetric inference. Wall/end layers and free zoom8+ are preserved.')
(REF/'intro-review-elements.json').write_text(json.dumps(spec,indent=2));(P/'measurements.json').write_text(json.dumps(measurements,indent=2));summary=[]
for k,ms in measurements.items():summary.append(dict(element=k,first=ms[0]['frame'],last=ms[-1]['frame'],observations=len(ms),min_correlation=min((q.get('correlation',1) for q in ms))))
(P/'measurement-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print('assets',len(ledger),'replacements',list(replacements))
