"""Stitch one static flight app document and fit real camera/opacity/directional shutter.
Analysis frames never become runtime full-frame playback. Runtime keeps native actor/card transforms.
"""
from pathlib import Path
from functools import lru_cache
import json,hashlib,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage,fft
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';P=R/'verification/fidelity-review/05-flight';AS=REF/'assets/flight-document-review';AS.mkdir(exist_ok=True);ledger=[]
@lru_cache(maxsize=8)
def frame(f):
 p=P/'source'/f'{f-354:04d}.png' if f>=355 else P/'pre-source'/f'{f-349:04d}.png';return np.array(Image.open(p).convert('RGB')).astype('float32')
def save(arr,name,frames,bounds,notice):
 p=AS/(name+'.png');Image.fromarray(np.clip(arr,0,255).round().astype('uint8')).save(p);ledger.append(dict(id=name,asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceFrames=frames,sourceBounds=bounds,notice=notice));return str(p)
# Static app header/flight summary and sampled lower blue backdrop.
top=frame(366)[78:628,188:772].copy();topPath=save(top,'flight-top-ui',[366],[[188,78,772,628]],'Bounded static original app header/summary UI; bitmap internal copy, native camera/opacity.');H=1138;W=584;bg=np.zeros((H-550,W,3),dtype='float32');xnodes=[7,210,364,574]
for yy in range(H-550):
 y=yy+132;a=frame(387)[y];b=frame(399)[y];colors=np.array([np.median(a[190:201],axis=0),np.median(b[394:403],axis=0),np.median(a[547:558],axis=0),np.median(b[754:770],axis=0)])
 for c in range(3):bg[yy,:,c]=np.interp(np.arange(W),xnodes,colors[:,c])
 bg[yy,:2]=a[188:190];bg[yy,-2:]=b[770:772]
bgPath=save(bg,'flight-lower-background',[387,399],[[188,132,772,720]],'Static app blue backdrop interpolated across measured exposed strips at both carousel positions; faint unobserved cloud variation approximate.')
cards=[]
for name,f,b,w,h,x in [('basic',387,[204,132,543,622],339,490,25),('economy',399,[409,132,748,694],339,562,383)]:
 a=frame(f)[b[1]:b[3],b[0]:b[2]].copy();yy,xx=np.indices((h,w));r=31
 for cx,cy,zone in [(r,r,(xx<r)&(yy<r)),(w-r,r,(xx>=w-r)&(yy<r)),(r,h-r,(xx<r)&(yy>=h-r)),(w-r,h-r,(xx>=w-r)&(yy>=h-r))]:a[zone&((xx-cx)**2+(yy-cy)**2>(r-2)**2)]=255
 path=save(a,'flight-fare-'+name,[f],[b],'Bounded original fare card UI; native rounded clip, position and carousel pan; bitmap internal copy.');cards.append(dict(name=name,path=path,x=x,y=550,width=w,height=h,RGB=a))
# Opaque document RGB and antialiased native rounded-top alpha for measurement.
doc=np.concatenate((top,bg),axis=0);docA=np.ones((H,W),dtype='float32');m=Image.new('L',(W*4,H*4),0);ImageDraw.Draw(m).rounded_rectangle((0,0,W*4,2000*4),radius=64*4,fill=255);docA=np.asarray(m.resize((W,H),Image.Resampling.LANCZOS)).astype('float32')/255
for c in cards:
 mask=Image.new('L',(c['width']*4,c['height']*4),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,c['width']*4,c['height']*4),radius=31*4,fill=255);M=np.asarray(mask.resize((c['width'],c['height']),Image.Resampling.LANCZOS)).astype('float32')/255;x=c['x'];y=c['y'];lo=max(0,x);hi=min(W,x+c['width']);part=c['RGB'][:,lo-x:hi-x];alpha=M[:,lo-x:hi-x,None];doc[y:y+c['height'],lo:hi]=part*alpha+doc[y:y+c['height'],lo:hi]*(1-alpha)
save(doc,'diagnostic-doc-composite',[366,387,399],[],'Analysis composite only; runtime retains separate top/background/fare images and native clips.')
# Blur timing is measured against the clean351 UI, outside the app viewport.
clean=frame(351)/255;sigmas=np.arange(0,12.01,.5);blurred=[];left=[]
for sig in sigmas:
 a=ndimage.gaussian_filter(clean,(sig,sig,0),mode='nearest') if sig else clean;blurred.append(a);left.append(a[60:710,95:172].copy())
bgFit={};cache={}
for f in range(353,414):
 target=frame(f)[60:710,95:172]/255;errors=[float(((target-a)**2).mean()) for a in left];i=int(np.argmin(errors));sig=float(sigmas[i])
 if 0<i<len(errors)-1:
  den=errors[i-1]-2*errors[i]+errors[i+1]
  if den>1e-12:sig+=float(np.clip(.25*(errors[i-1]-errors[i+1])/den,-.5,.5))
 sig=round(sig,2);bgFit[f]=dict(frame=f,blur=sig,left_rgb_mse=errors[i]);
 if sig not in cache:cache[sig]=ndimage.gaussian_filter(clean,(sig,sig,0),mode='nearest') if sig else clean
print('background',[(f,bgFit[f]['blur']) for f in [353,354,355,356,357,360,366,372,387,413]],flush=True)
# Sampled native RGB profiles, with cached FFTs of reversed document signals.
strips=[(24,32),(264,280),(544,555)];Dcolor=np.concatenate([((doc/255)*docA[:,:,None])[:,l:r].mean(1) for l,r in strips],axis=1);Dalpha=np.concatenate([np.repeat(docA[:,l:r].mean(1)[:,None],3,1) for l,r in strips],axis=1);Nfft=fft.next_fast_len(H+720-1);ones=np.ones((720,Dcolor.shape[1]));Fone=fft.rfft(ones,n=Nfft,axis=0);kernels=[dict(kind='none',value=0)]+[dict(kind='gaussian',value=v) for v in [.5,1,2,4,6,8,12,16,24,32,48]]+[dict(kind='box',value=v) for v in [9,17,25,41,57,81,113,145]];K=[]
for k in kernels:
 if k['kind']=='gaussian':C=ndimage.gaussian_filter1d(Dcolor,k['value'],axis=0,mode='constant');A=ndimage.gaussian_filter1d(Dalpha,k['value'],axis=0,mode='constant')
 elif k['kind']=='box':C=ndimage.uniform_filter1d(Dcolor,k['value'],axis=0,mode='constant');A=ndimage.uniform_filter1d(Dalpha,k['value'],axis=0,mode='constant')
 else:C=Dcolor;A=Dalpha
 rev=lambda v:fft.rfft(v[::-1],n=Nfft,axis=0);K.append(dict(**k,FC=rev(C),FA=rev(A),FC2=rev(C*C),FA2=rev(A*A),FCA=rev(C*A)))
validY=np.arange(-520,501);indices=H-1+validY;denCache={};camera=[]
for f in range(355,414):
 Bfull=cache[bgFit[f]['blur']];B=np.concatenate([Bfull[:,188+l:188+r].mean(1) for l,r in strips],axis=1);S=np.concatenate([(frame(f)/255)[:,188+l:188+r].mean(1) for l,r in strips],axis=1);T=S-B;FT=fft.rfft(T,n=Nfft,axis=0);FTB=fft.rfft(T*B,n=Nfft,axis=0);FB=fft.rfft(B,n=Nfft,axis=0);FB2=fft.rfft(B*B,n=Nfft,axis=0);tt=float((T*T).sum());best=None
 for ki,k in enumerate(K):
  key=(bgFit[f]['blur'],ki)
  if key not in denCache:denCache[key]=fft.irfft((Fone*k['FC2']+FB2*k['FA2']-2*FB*k['FCA']).sum(1),n=Nfft)[indices]
  D=np.maximum(1e-10,denCache[key]);N=fft.irfft((FT*k['FC']-FTB*k['FA']).sum(1),n=Nfft)[indices];op=np.clip(N/D,0,1);err=tt-2*op*N+op*op*D;i=int(np.argmin(err));q=dict(frame=f,y=float(validY[i]),opacity=float(op[i]),kernel=k['kind'],spread=float(k['value']),profile_mse=float(err[i]/T.size),correlation=float(N[i]/np.sqrt(max(1e-12,D[i]*tt))),backgroundBlur=bgFit[f]['blur'])
  if best is None or q['profile_mse']<best['profile_mse']:best=q
 camera.append(best)
 if f in [355,356,357,358,360,366,370,371,372,373,374,376,380,387,399,413]:print('camera',best,flush=True)
# Dense carousel positions from its blank white header row once vertical scrolling settles.
for q in camera:
 f=q['frame'];pan=0.0
 if f>=380:
  y=int(round(q['y']+610));y=max(0,min(719,y));a=frame(f);r=a[max(0,y-1):min(720,y+2),188:772,0].mean(0);xs=np.where(r>225)[0];groups=np.split(xs,np.where(np.diff(xs)>1)[0]+1) if len(xs) else [];groups=[g for g in groups if len(g)>80]
  if groups:
   g=min(groups,key=lambda g:g[0]);last=int(g[-1]);e=last
   if last+1<len(r):
    low=float(np.median(r[min(len(r)-1,last+2):min(len(r),last+8)]));mid=(255+low)/2;frac=(r[last]-mid)/max(1e-6,r[last]-r[last+1]);e=last+np.clip(frac,0,1)+.5
   pan=float(188+e-552)
 q['panX']=pan
print('pan',[(q['frame'],q['panX']) for q in camera if q['frame'] in [380,383,385,387,393,399,405,413]],flush=True)
# Store only static UI asset descriptors and measured native states.
assets=dict(top=topPath,lowerBackground=bgPath,cards=[{k:v for k,v in c.items() if k!='RGB'} for c in cards],documentWidth=W,documentHeight=H,viewport=[188,0,584,720],topRadius=64,cardRadius=31)
(REF/'flight-document-camera-review.json').write_text(json.dumps(dict(assets=assets,camera=camera,background=list(bgFit.values()),provenance=ledger,notice='Static bounded app UI document/card assets with native camera, carousel pan, opacity and sampled directional shutter. Source353–354 background blur correction included by owner authorization. No full source-frame playback.'),indent=2));print('fit complete',len(camera),flush=True)
