"""Fit the CTA's independent native words and per-glyph gray/blur→cyan reveal."""
from pathlib import Path
from functools import lru_cache
import ast,copy,json,sys,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage,signal
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
ROOT=Path('/workspace/imessage-recreations');REF=ROOT/'references/01-photonhq';P=ROOT/'verification/fidelity-review/01-intro';AS=REF/'assets/intro-review';base=json.loads((REF/'scene-intro-base-v4.json').read_text());byid={l['id']:l for l in base['layers']};extra=json.loads((P/'source-extra-map.json').read_text());ledger=[];measurements={}
@lru_cache(maxsize=10)
def frame(n):
 p=P/'source-onus-exit'/f'{n-509:04d}.png' if 510<=n<=525 else P/extra[str(n)];return np.array(Image.open(p).convert('RGB')),0,p

def region(n,box):
 a,_,_=frame(n);x0,y0,x1,y1=map(int,box);return a[max(0,y0):min(1080,y1),max(0,x0):min(1920,x1)]
# Reuse only pure source-word measurement functions, never execute the authoring script.
names={'neutral_alpha','bbox','black_box','tk','tracks','geometry','native_path','make_words','find_groups','fit_candidate','measure_words'};tree=ast.parse((REF/'build-intro-review.py').read_text());mod=ast.Module(body=[q for q in tree.body if isinstance(q,ast.FunctionDef) and q.name in names],type_ignores=[]);exec(compile(mod,'pure-word-functions','exec'),globals())
cta,gap=make_words(555,[300,350,1600,550],['Try','it','today','at'],'cta-entry-word');words=measure_words(cta,gap,range(516,555),lambda n:[300,350,1600,1080] if n<533 else [300,350,1600,555]);onus,gap2=make_words(510,[650,400,1270,700],['On','us.'],'cta-onus-exit');onusnodes=measure_words(onus,gap2,range(510,526),lambda n:[600,400,1320,850]);firstexit=min(t['obs'][-1]['frame']+1 for t in onus)
exitnodes=[]
for node in onusnodes:
 if node['end']>firstexit/30:node['start']=max(node['start'],firstexit/30);exitnodes.append(node)
# Canonical glyph shapes: source555 is fully settled; actual copy has17glyphs.
url=next(c for c in byid['group-786']['children'] if c['type']=='image');raw=np.array(Image.open(url['src']).convert('RGB'));x0,y0=int(url['x']),int(url['y']);chroma=(raw[:,:,2].astype(float)-raw[:,:,0])/255;labels,n=ndimage.label(chroma>.12,np.ones((3,3)));components=[]
for j,sl in enumerate(ndimage.find_objects(labels),1):
 if sl is not None and np.count_nonzero(labels[sl]==j)>10:components.append((sl[1].start,j,sl))
components.sort();assert len(components)==17,len(components);copytext='photon.codes/beta';_,inds=ndimage.distance_transform_edt(labels==0,return_indices=True);nearest=labels[tuple(inds)];grayink=(255-raw.mean(2))/255;glyphs=[]
for i,(_,j,sl) in enumerate(components):
 yy,xx=sl;norm=float(np.percentile(grayink[labels==j],90));alpha=np.clip(grayink/max(.001,norm),0,1)*(nearest==j);alpha[chroma<.005]=0;box=[max(0,xx.start-2),max(0,yy.start-2),min(raw.shape[1],xx.stop+2),min(raw.shape[0],yy.stop+2)];A=alpha[box[1]:box[3],box[0]:box[2]].astype('float32');gx,gy=x0+box[0],y0+box[1];d,stats=trace_alpha(A,gx,gy);glyphs.append(dict(index=i,char=copytext[i],A=A,x=gx,y=gy,d=d,obs=[]));ledger.append(dict(id=f'cta-url-glyph-{i}',kind='native glyph outlines',semanticText=copytext[i],sourceFrame=555,sourceBounds=[gx,gy,gx+A.shape[1],gy+A.shape[0]],**stats))

def energy_map(T,h,w):
 s=np.pad(np.cumsum(np.cumsum((T*T).astype('float64'),axis=0),axis=1),((1,0),(1,0)));return s[h:,w:]-s[:-h,w:]-s[h:,:-w]+s[:-h,:-w]

def template(A,sx,sy,sigma):
 W=max(1,round(A.shape[1]*sx));H=max(1,round(A.shape[0]*sy));r=np.asarray(Image.fromarray(A,'F').resize((W,H),Image.Resampling.BILINEAR));pad=int(np.ceil(3*sigma))+2;r=np.pad(r,pad);r=ndimage.gaussian_filter(r,sigma,mode='constant') if sigma>0 else r;return r.astype('float32'),pad,W/A.shape[1],H/A.shape[0]

def match(T,A,sx,sy,sigma,limits=None):
 M,pad,rx,ry=template(A,sx,sy,sigma);h,w=M.shape
 if h>T.shape[0] or w>T.shape[1]:return None
 corr=signal.fftconvolve(T,M[::-1,::-1],mode='valid');e=energy_map(T,h,w);score=np.where(e>1e-8,corr/np.sqrt(np.maximum(1e-10,e*float((M*M).sum()))),-1)
 if float(score.max())>1.01:raise ValueError('NCC exceeds1; inspect precision before accepting a fit')
 if limits:
  lx,hx,ly,hy=limits;ys=np.arange(score.shape[0])[:,None]+pad;xs=np.arange(score.shape[1])[None,:]+pad;score=np.where((xs>=lx)&(xs<=hx)&(ys>=ly)&(ys<=hy),score,-1)
 iy,ix=np.unravel_index(np.argmax(score),score.shape);return dict(score=float(score[iy,ix]),ix=int(ix),iy=int(iy),px=int(ix+pad),py=int(iy+pad),M=M,sx=rx,sy=ry,sigma=float(sigma))

def best_match(T,A,scales,sigmas,limits=None):
 best=None
 for sx,sy in scales:
  for sig in sigmas:
   q=match(T,A,float(sx),float(sy),float(sig),limits)
   if q and (best is None or q['score']>best['score']):best=q
 return best

# The first p is isolated on the left; use it to measure the common camera.
pilot=[];cameras={};g=glyphs[0];proi=[420,530,720,1080]
for n in range(526,555):
 S=region(n,proi).astype('float32');T=(255-S.mean(2))/255
 if T.max()<.012:continue
 best=best_match(T,g['A'],[(s,s) for s in np.arange(.85,1.351,.05)],[0,1,2,3,4,6,8,10,12])
 if not best or best['score']<.76:continue
 s=(best['sx']+best['sy'])/2;fine=best_match(T,g['A'],[(v,v) for v in np.arange(max(.75,s-.04),s+.041,.01)],np.arange(max(0,best['sigma']-1),best['sigma']+1.01,.5))
 if fine and fine['score']>best['score']:best=fine
 best['tx']=proi[0]+best['px']-best['sx']*g['x'];best['ty']=proi[1]+best['py']-best['sy']*g['y'];cameras[n]=best;pilot.append({k:v for k,v in best.items() if k!='M'}|{'frame':n});print('p',n,round(best['score'],3),round(best['sx'],3),round(best['sigma'],2),flush=True)
if not cameras:raise ValueError('No URL p observations')
# Each later glyph independently loses blur, rises, and changes fromgray tocyan.
for n,cam in cameras.items():
 for i,g in enumerate(glyphs):
  sx,sy=cam['sx'],cam['sy'];ex=cam['tx']+sx*g['x'];ey=cam['ty']+sy*g['y'];roi=[max(0,int(np.floor(ex-50))),max(0,int(np.floor(ey-45))),min(1920,int(np.ceil(ex+sx*g['A'].shape[1]+50))),min(1080,int(np.ceil(ey+sy*g['A'].shape[0]+135)))];RGB=region(n,roi).astype('float32');T=(255-RGB.mean(2))/255;limits=[ex-roi[0]-9,ex-roi[0]+9,ey-roi[1]-12,ey-roi[1]+90];q=best_match(T,g['A'],[(sx,sy)],[0,.5,1,1.5,2,3,4,6,8,10,12],limits)
  if not q:continue
  M=q['M'];h,w=M.shape;target=(255-RGB[q['iy']:q['iy']+h,q['ix']:q['ix']+w]);den=max(1e-8,float((M*M).sum()));D=np.clip((target*M[:,:,None]).sum((0,1))/den,0,255);a=float(min(1,float(D.max())/60)) if q['score']>.65 else 0
  if a<.025:a=0
  F=np.clip(255-D/max(.001,a),0,255).round().astype(int);fill='#'+''.join(f'{v:02x}' for v in F);tx=roi[0]+q['px']-q['sx']*g['x'];ty=roi[1]+q['py']-q['sy']*g['y'];g['obs'].append(dict(frame=n,x=tx,y=ty,scaleX=q['sx'],scaleY=q['sy'],opacity=a,fill=fill,blur=q['sigma']/max(.1,(q['sx']+q['sy'])/2),correlation=q['score'],sourceRGBContrast=D.tolist()))
urlnodes=[]
for g in glyphs:
 obs=g['obs'];assert obs,g['char'];node=dict(type='path',id=f'cta-url-glyph-{g["index"]}',d=g['d'],fill=obs[-1]['fill'],semanticText=g['char'],sourceFrame=555,editability='Native editable glyph contour with measured per-frame color, blur, opacity and pose.',start=obs[0]['frame']/30,end=555/30,keyframes={k:tk([(q['frame'],q[k]) for q in obs]) for k in ['x','y','scaleX','scaleY','opacity','blur']});node['keyframes']['fill']=[dict(t=q['frame']/30,value=q['fill'],ease='linear') for q in obs];urlnodes.append(node)
# Merge only after fitting, so a concurrent own intro measurement cannot be lost.
spec=json.loads((REF/'intro-review-elements.json').read_text());held=copy.deepcopy(byid['group-786']);held['start']=555/30;spec['replacements']['group-786']=held;oldOn=copy.deepcopy(byid['text-783-source-outline']);oldOn['end']=min(oldOn['end'],firstexit/30);spec['replacements'][oldOn['id']]=oldOn;spec.setdefault('gate_overrides',{}).update({'group-27':{'start':8},'group-786':{'start':555/30},'text-783-source-outline':{'end':oldOn['end']}});spec.setdefault('insert_before',{})['group-786']=[dict(type='group',id='cta-measured-entry',start=min(c['start'] for c in words+urlnodes),end=555/30,children=words+urlnodes)]
if exitnodes:spec['insert_before']['text-783-source-outline']=[dict(type='group',id='cta-onus-exit',start=firstexit/30,end=max(c['end'] for c in exitnodes),children=exitnodes)]
spec['assets']+=ledger;spec['measurements'].update(measurements);spec['measurements']['URL-camera']=pilot
for g in glyphs:spec['measurements'][f'cta-url-glyph-{g["index"]}']=g['obs']
spec['changed_frame_ranges']=[[0,239],[min(firstexit,518),554]];spec['notice']='Intro+CTA native prototype pending checkpoints. All black copy and CTA URL glyphs are native outlines. URL gray-to-cyan color/blur/pose is fitted per glyph;19s settled original CTA and other holds retained.';(REF/'intro-review-elements.json').write_text(json.dumps(spec,indent=2));(P/'cta-native-measurements.json').write_text(json.dumps(dict(camera=pilot,words=measurements,firstOnusExit=firstexit,glyphs=[dict(index=g['index'],char=g['char'],observations=g['obs']) for g in glyphs]),indent=2));print('CTA merged',spec['changed_frame_ranges'],'pframes',len(cameras),flush=True)
