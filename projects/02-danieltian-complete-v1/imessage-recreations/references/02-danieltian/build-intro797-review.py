"""Native title word timing/camera plus isolated 3D icon artwork for source02 opening."""
from pathlib import Path
from functools import lru_cache
import json,hashlib,sys,copy
import numpy as np
from PIL import Image
from scipy import ndimage,signal
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations');REF=R/'references/02-danieltian';P=R/'verification/fidelity-review/02-intro';AS=REF/'assets/intro797-review';AS.mkdir(exist_ok=True);ledger=[];measure={}
@lru_cache(maxsize=8)
def frame(f):return np.array(Image.open(P/'source'/f'{f+1:04d}.png').convert('RGB')).astype('float32')
def alpha(f,b):
 a=frame(f)[b[1]:b[3],b[0]:b[2]];v=np.clip((255-a.mean(2))/255,0,1);v[a.max(2)-a.min(2)>12]=0;v[v<2/255]=0;return v

def bbox(m,x=0,y=0):
 yy,xx=np.where(m);return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+1+x),int(yy.max()+1+y)] if len(xx) else None
rows=[dict(roi=[200,400,1750,550],tokens=['Introducing','Agent','to','Agent'],births=[6,8,11,13]),dict(roi=[150,550,1770,700],tokens=['in','iMessage','Group','Chats'],births=[15,17,20,22])];words=[]
for ri,row in enumerate(rows):
 b=row['roi'];a=alpha(30,b);xs=np.where((a>.5).any(0))[0];inds=sorted(np.argsort(np.diff(xs))[-3:]);edges=[b[0]]+[int((xs[i]+xs[i+1])/2)+b[0] for i in inds]+[b[2]];row['word_indices']=[]
 for wi,(lo,hi,text,birth) in enumerate(zip(edges,edges[1:],row['tokens'],row['births'])):
  A=a[:,lo-b[0]:hi-b[0]];cb=bbox(A>.5,lo,b[1]);bb=[cb[0]-2,cb[1]-2,cb[2]+2,cb[3]+2];d,stats=trace_alpha(alpha(30,bb),bb[0],bb[1]);id=f'intro797-row{ri}-word{wi}';node=dict(type='path',id=id,d=d,fill='#000000',semanticText=text,sourceFrame=30,sourceBounds=bb,editability='Native editable semantic glyph outline, independent native pose/lifetime; not live font text.');words.append(dict(node=node,cb=cb,birth=birth,observations=[]));row['word_indices'].append(len(words)-1);ledger.append(dict(id=id,sourceFrame=30,sourceBounds=bb,kind='native semantic word contours',**stats))
# Entry contains independently staggered complete words, with a horizontal overshoot.
for f in range(6,24):
 for row in rows:
  live=[i for i in row['word_indices'] if words[i]['birth']<=f]
  if not live:continue
  b=row['roi'];a=alpha(f,b);xs=np.where((a>.5).any(0))[0];assert len(xs),(f,b)
  gaps=np.diff(xs);ix=sorted(np.argsort(gaps)[-(len(live)-1):]) if len(live)>1 else [];edges=[b[0]]+[int((xs[i]+xs[i+1])/2)+b[0] for i in ix]+[b[2]]
  for i,lo,hi in zip(live,edges,edges[1:]):
   w=words[i];cb=w['cb'];bb=bbox(a[:,lo-b[0]:hi-b[0]]>.5,lo,b[1]);sx=(bb[2]-bb[0])/(cb[2]-cb[0]);sy=(bb[3]-bb[1])/(cb[3]-cb[1]);w['observations'].append(dict(frame=f,sourceBounds=bb,x=bb[0]-cb[0]*sx,y=bb[1]-cb[1]*sy,scaleX=sx,scaleY=sy))
entry=[]
for w in words:
 n=copy.deepcopy(w['node']);obs=w['observations'];n['start']=w['birth']/30;n['end']=24/30;n['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY']};entry.append(n);measure[n['id']]=obs
# After all words arrive the title breathes as one camera around its combined bounds.
cb=bbox(alpha(30,[150,400,1770,700])>.5,150,400)
def camera(f):
 bb=bbox(alpha(f,[150,400,1770,700])>.5,150,400);sx=(bb[2]-bb[0])/(cb[2]-cb[0]);sy=(bb[3]-bb[1])/(cb[3]-cb[1]);return dict(frame=f,sourceBounds=bb,x=bb[0]-cb[0]*sx,y=bb[1]-cb[1]*sy,scaleX=sx,scaleY=sy)
groups=[]
for name,fs in [('artifact',list(range(3))),('held',list(range(24,64)))]:
 obs=[camera(f) for f in fs];measure[name]=obs;cs=[]
 for w in words:n=copy.deepcopy(w['node']);n['id']=name+'-'+n['id'];cs.append(n)
 groups.append(dict(type='group',id='intro797-'+name,start=min(fs)/30,end=(max(fs)+1)/30,children=cs,keyframes={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY']}))
# The late shrink/blur is measured jointly; thresholded word bounds would misread blur as scale.
roi=[150,400,1770,700];A=alpha(30,roi);core=bbox(A>.5);A=A[max(0,core[1]-3):core[3]+3,max(0,core[0]-3):core[2]+3];ax=roi[0]+core[0]-3;ay=roi[1]+core[1]-3

def energy(T,h,w):
 s=np.pad((T.astype('float64')**2).cumsum(0).cumsum(1),((1,0),(1,0)));return s[h:,w:]-s[:-h,w:]-s[h:,:-w]+s[:-h,:-w]
def fit(T,sc,sigma):
 M=np.asarray(Image.fromarray(A,'F').resize((max(1,round(A.shape[1]*sc)),max(1,round(A.shape[0]*sc))),Image.Resampling.BILINEAR));pad=int(3*sigma)+2;M=np.pad(M,pad);M=ndimage.gaussian_filter(M,sigma,mode='constant') if sigma else M;h,w=M.shape
 if h>T.shape[0] or w>T.shape[1]:return None
 C=signal.fftconvolve(T,M[::-1,::-1],mode='valid');D=energy(T,h,w)*float((M*M).sum());score=np.where(D>1e-7,C/np.sqrt(np.maximum(1e-9,D)),-1)
 if score.max()>1.01:raise ValueError('Impossible normalized correlation')
 y,x=np.unravel_index(np.argmax(score),score.shape);opacity=min(1,float((T[y:y+h,x:x+w]*M).sum()/max(1e-8,float((M*M).sum()))));sx=(M.shape[1]-2*pad)/A.shape[1];sy=(M.shape[0]-2*pad)/A.shape[0];return dict(correlation=float(score[y,x]),x=int(x)+150+pad-ax*sx,y=int(y)+340+pad-ay*sy,scaleX=sx,scaleY=sy,blur=sigma/(.5*(sx+sy)),opacity=opacity,s=sc,sigma=sigma)
obs=[]
for f in range(64,68):
 T=alpha(f,[150,340,1770,820]);best=None
 for sc in np.arange(.50,1.051,.05):
  for sig in [0,2,4,6,8,10,12,14]:
   q=fit(T,float(sc),sig)
   if q and (best is None or q['correlation']>best['correlation']):best=q
 for sc in np.arange(best['s']-.03,best['s']+.031,.01):
  for sig in np.arange(max(0,best['sigma']-1),best['sigma']+1.01,.5):
   q=fit(T,float(sc),float(sig))
   if q and q['correlation']>best['correlation']:best=q
 obs.append(dict(frame=f,**best));print('late',f,best,flush=True)
cs=[]
for w in words:n=copy.deepcopy(w['node']);n['id']='late-'+n['id'];cs.append(n)
groups.append(dict(type='group',id='intro797-late-camera',start=64/30,end=68/30,children=cs,keyframes={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','blur','opacity']}));measure['late-camera']=obs
# Isolated original 3D icon poses preserve spinning spheres and their changing shading.
icons=[]
for f in list(range(3))+list(range(15,68)):
 a=frame(f)
 for name,b,channel in [('messages',[150,520,900,750],'green'),('group',[750,500,1250,760],'multi')]:
  z=a[b[1]:b[3],b[0]:b[2]];chroma=z.max(2)-z.min(2);m=(z[:,:,1]-z[:,:,0]>16)&(z[:,:,1]-z[:,:,2]>9)&(z[:,:,1]>100) if channel=='green' else chroma>14
  bb=bbox(m,b[0],b[1])
  if not bb:continue
  bb=[max(b[0],bb[0]-6),max(b[1],bb[1]-6),min(b[2],bb[2]+6),min(b[3],bb[3]+6)];v=a[bb[1]:bb[3],bb[0]:bb[2]];al=(255-v.min(2))/255;al[al<2/255]=0;rgb=np.where(al[:,:,None]>0,(v-255*(1-al[:,:,None]))/np.maximum(1e-5,al[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),al[:,:,None]*255),2).round().astype('uint8');p=AS/f'{name}-{f}.png';Image.fromarray(rgba).save(p);id=f'intro797-icon-{name}-{f}';icons.append(dict(type='image',id=id,src=str(p),x=bb[0],y=bb[1],width=bb[2]-bb[0],height=bb[3]-bb[1],start=f/30,end=(f+1)/30,sourceFrame=f,sourceBounds=bb,semanticText='Messages icon' if name=='messages' else 'Spinning Group Chats spheres',editability='Bounded isolated original3D icon pose; native geometry/lifetime, bitmap internals.'));ledger.append(dict(id=id,sourceFrame=f,sourceBounds=bb,asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceSHA256=hashlib.sha256((P/'source'/f'{f+1:04d}.png').read_bytes()).hexdigest()))
replacement=dict(type='group',id='group-797',start=0,end=2.24,children=groups+entry+icons);spec=dict(id='group-797',replacement=replacement,changed_frame_ranges=[[0,67]],assets=ledger,measurements=measure,notice='Native independent semantic word entrances, observed0–2 composed artifact/reset3–5, measured held camera and late shrink/blur. Isolated original3D icon pose artwork has bitmap internals. No complete-frame/source-video playback.');(REF/'intro797-review-elements.json').write_text(json.dumps(spec,indent=2));(REF/'intro797-review-provenance.json').write_text(json.dumps(dict(assets=ledger,notice=spec['notice']),indent=2));print('icons',len(icons),'words',len(words))
