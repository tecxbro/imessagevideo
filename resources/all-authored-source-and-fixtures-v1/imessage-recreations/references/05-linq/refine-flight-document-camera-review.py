"""Separate true backdrop whitening, app entrance defocus, vertical scroll, and fare-carousel pan.
Raw late vertical-profile fits were confounded by horizontal card motion; title geometry resolves it.
"""
from pathlib import Path
from functools import lru_cache
import json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage,signal
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';P=R/'verification/fidelity-review/05-flight';data=json.loads((REF/'flight-document-camera-review.json').read_text());Ameta=data['assets'];W=584;H=1138
@lru_cache(maxsize=8)
def frame(f):
 p=P/'source'/f'{f-354:04d}.png' if f>=355 else P/'pre-source'/f'{f-349:04d}.png';return np.array(Image.open(p).convert('RGB')).astype('float32')/255
clean=frame(351);sigs=np.arange(0,16.01,.5);lefts=[]
for sig in sigs:
 z=ndimage.gaussian_filter(clean,(sig,sig,0),mode='nearest') if sig else clean;lefts.append(1-z[60:710,95:165])
bg=[];bgcache={}
for f in range(353,414):
 T=1-frame(f)[60:710,95:165];best=None
 for sig,D in zip(sigs,lefts):
  op=min(1,float((T*D).sum()/max(1e-8,(D*D).sum())));err=float(((T-op*D)**2).mean());q=dict(frame=f,blur=float(sig),opacity=op,mse=err)
  if best is None or err<best['mse']:best=q
 bg.append(best);key=(best['blur'],round(best['opacity'],6))
 if key not in bgcache:
  z=ndimage.gaussian_filter(clean,(best['blur'],best['blur'],0),mode='nearest') if best['blur'] else clean;bgcache[key]=1-best['opacity']*(1-z)
print('background',[(q['frame'],q['blur'],q['opacity']) for q in bg if q['frame'] in [353,354,355,357,360,366,372,387,413]],flush=True)
# Same static document, native rounded-top/card silhouettes.
top=np.array(Image.open(Ameta['top']).convert('RGB')).astype('float32')/255;lower=np.array(Image.open(Ameta['lowerBackground']).convert('RGB')).astype('float32')/255;doc=np.concatenate((top,lower),axis=0)
for c in Ameta['cards']:
 rgb=np.array(Image.open(c['path']).convert('RGB')).astype('float32')/255;mask=Image.new('L',(c['width']*4,c['height']*4),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,c['width']*4,c['height']*4),radius=31*4,fill=255);m=np.array(mask.resize((c['width'],c['height']),Image.Resampling.LANCZOS)).astype('float32')/255;x=c['x'];y=c['y'];lo=max(0,x);hi=min(W,x+c['width']);al=m[:,lo-x:hi-x,None];doc[y:y+c['height'],lo:hi]=doc[y:y+c['height'],lo:hi]*(1-al)+rgb[:,lo-x:hi-x]*al
mask=Image.new('L',(W*4,H*4),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,W*4,2000*4),radius=64*4,fill=255);alpha=np.array(mask.resize((W,H),Image.Resampling.LANCZOS)).astype('float32')/255;rgba=np.concatenate((doc*alpha[:,:,None],alpha[:,:,None]),2)
cam=data['camera'];by={q['frame']:q for q in cam};bgBy={q['frame']:q for q in bg}
def bgimage(f):
 q=bgBy[f];return bgcache[(q['blur'],round(q['opacity'],6))]
def shifted(arr,Y):
 z=np.arange(720)-Y;lo=np.floor(z).astype(int);fr=(z-lo)[:,None,None];i0=np.clip(lo,0,H-1);i1=np.clip(lo+1,0,H-1);a=arr[i0]*(1-fr)+arr[i1]*fr;valid=(z>=-1)&(z<H);a[~valid]=0
 # Interpolation beyond top/bottom is transparent, not repeated edge color.
 a[lo<0]*=np.clip(fr[lo<0],0,1)
 a[lo>=H-1]*=1-np.clip(fr[lo>=H-1],0,1)
 return a
# White summary patch gives physical opacity independent of incidental backdrop contrast.
for f in range(355,360):
 q=by[f];B=bgimage(f)[:,188:772];S=frame(f)[:,188:772];y0=max(0,round(q['y']+240));y1=min(720,y0+40);D=1-B[y0:y1,250:400];T=S[y0:y1,250:400]-B[y0:y1,250:400];op=float(np.clip((T*D).sum()/max(1e-8,(D*D).sum()),0,1));best=None
 for sig in [0,.5,1,2,3,4,5,6]:
  C=ndimage.gaussian_filter(rgba,(sig,sig,0),mode='constant') if sig else rgba
  for Y in np.arange(q['y']-4,q['y']+4.01,.5):
   V=shifted(C,float(Y));pred=B*(1-op*V[:,:,3:])+op*V[:,:,:3];err=float(((S-pred)**2).mean());r=dict(y=float(Y),opacity=op,kernel='isotropic',spread=float(sig),full_mse=err)
   if best is None or err<best['full_mse']:best=r
 q['raw_profile_fit']={k:q[k] for k in ['y','opacity','kernel','spread']};q.update(best);q['panX']=0.;print('entrance',f,best,flush=True)
for f in range(360,380):
 q=by[f];q['opacity']=1.;q['panX']=0.
 if q['spread']<=1:q['kernel']='none';q['spread']=0.
# Joint horizontal blur/position of a prefix, computed from the FULL word first,
# so a clipped viewport edge or later letter does not contaminate the template.
canon=frame(399)[154:194,430:624];Word=(1-canon.mean(2));Word[canon.max(2)-canon.min(2)>14]=0;Word[Word<3/255]=0;kernels=[]
for sx in [0,.5,1,2,3,4,6,8,12]:
 for sy in [0,.5,1]:kernels.append(('gaussian',sx,sy))
for L in [9,17,25,33,41]:kernels.append(('box',L,0))
models=[]
for kind,value,sy in kernels:
 pad=int(np.ceil(3*value))+2 if kind=='gaussian' else (int(value)-1)//2+2;M=np.pad(Word,((0,0),(pad,pad)));M=ndimage.gaussian_filter1d(M,sy,axis=0,mode='constant') if sy else M
 if kind=='gaussian' and value:M=ndimage.gaussian_filter1d(M,value,axis=1,mode='constant')
 if kind=='box':M=ndimage.uniform_filter1d(M,int(value),axis=1,mode='constant')
 M=M[:,:pad+140];models.append(dict(kind=kind,value=value,sy=sy,pad=pad,M=M))
for f in range(380,414):
 target=frame(f)[140:210,380:772];T=1-target.mean(2);T[target.max(2)-target.min(2)>14]=0;T[T<3/255]=0;best=None
 for m in models:
  M=m['M'];h,w=M.shape;C=signal.fftconvolve(T,M[::-1,::-1],mode='valid');I=np.pad((T.astype('float64')**2).cumsum(0).cumsum(1),((1,0),(1,0)));E=I[h:,w:]-I[:-h,w:]-I[h:,:-w]+I[:-h,:-w];D=E*float((M*M).sum());scores=np.where(D>1e-8,C/np.sqrt(np.maximum(1e-12,D)),-1);yy,xx=np.unravel_index(np.argmax(scores),scores.shape);score=float(scores[yy,xx]);delta=0.
  if score<.99999 and 0<xx<scores.shape[1]-1:
   l,c,r=map(float,scores[yy,xx-1:xx+2]);den=l-2*c+r
   if abs(den)>1e-9:delta=float(np.clip(.5*(l-r)/den,-.5,.5))
  q=dict(correlation=score,panX=float(380+xx+delta+m['pad']-592),y=float(140+yy-572),kernelX=m['kind'],spreadX=float(m['value']),residualYBlur=float(m['sy']))
  if best is None or score>best['correlation']:best=q
 q=by[f];q['raw_profile_fit']={k:q[k] for k in ['y','opacity','kernel','spread','panX']};q.update(best);q['opacity']=1.;q['kernel']='none';q['spread']=0.
 if f in [380,383,385,387,390,391,393,395,397,399,405,413]:print('carousel',f,best,flush=True)
for q in cam:q['backgroundBlur']=bgBy[q['frame']]['blur'];q['backgroundOpacity']=bgBy[q['frame']]['opacity']
data['camera']=cam;data['background']=bg;data['refinement_notice']='True white-field app opacity, entrance isotropic defocus, fixed opaque360+, measured horizontal carousel blur/pan resolves raw vertical-profile confounding. Background blur AND whitening measured against clean351; no source-frame playback.';(REF/'flight-document-camera-refined-review.json').write_text(json.dumps(data,indent=2));print('refined complete',flush=True)
