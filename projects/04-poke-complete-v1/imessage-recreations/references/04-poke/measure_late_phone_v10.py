"""Independent conversation pan, reply entry and whole-phone fade in original frames."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from scipy.fft import rfft,irfft,next_fast_len
p=Path(__file__).parent;d=p/'measurements-v8/decoded';source={n:np.array(Image.open(d/f'{n:06}.png').convert('RGB'))for n in range(840,888)};rows=[]
def largest(mask):
 labels,_=ndimage.label(mask);found=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
  if w>600 and 1.8<w/max(1,h)<4:found.append((int((labels[sl]==i).sum()),[xx.start,yy.start,xx.stop,yy.stop]))
 return max(found)[1]if found else None
for n,a in source.items():
 a=a.astype(np.int16)
 am=(a[:,:,0]>120)&(a[:,:,0]<210)&(a[:,:,1]-a[:,:,0]>1)&(a[:,:,1]-a[:,:,0]<10)&(a[:,:,2]-a[:,:,0]>7)&(a[:,:,2]-a[:,:,0]<25);b=largest(am);rgb=np.median(a[430:460,1110:1140],axis=(0,1));alpha=float(np.clip(np.median((255-rgb)/(255-np.array([158,163,174]))),0,1));r=dict(frame=n,time=n*1001/30000,phone_opacity=alpha,audio_bbox=b)
 if n<=870 and b:r.update(audio_x=b[0],audio_y=b[1])
 rows.append(r)
# Reply's first20native glyph rows remain visible above the keyboard at853.
a=source[870];crop=a[565:650,280:920];yy,xx=np.where(crop.max(2)<100);box=[int(xx.min()+280),int(yy.min()+565),int(xx.max()+281),int(yy.max()+566)];x,y,x2,y2=box

def profile(a):
 gray=a.mean(2);edges=np.linspace(0,gray.shape[1],21).astype(int);z=np.stack([gray[:,edges[i]:edges[i+1]].mean(1)for i in range(20)],1)
 return z-z.mean(1,keepdims=True)
t=profile(source[870][y:y+20,x:x2]);size=next_fast_len(1080+19);tf=rfft(t,n=size,axis=0);te=(t*t).sum();reply=[];all_reply=[]
for n,a in source.items():
 z=profile(a[:,x:x2]);corr=irfft((rfft(z,n=size,axis=0)*np.conj(tf)).sum(1),n=size)[:1061];energy=np.r_[0,np.cumsum((z*z).sum(1))];den=energy[20:]-energy[:-20];scores=np.where(den>100,corr/np.sqrt(np.maximum(1,den*te)),0);scores[:540]=0;scores[852:]=0;i=int(scores.argmax());pos=float(i)
 if 0<i<len(scores)-1:
  delta=scores[i-1]-2*scores[i]+scores[i+1]
  if abs(delta)>1e-8:pos+=float(np.clip(.5*(scores[i-1]-scores[i+1])/delta,-.5,.5))
 all_reply.append(dict(frame=n,score=float(scores[i]),y=pos-(y-544)))
 if scores[i]>.8 and n>=853:reply.append(dict(frame=n,time=n*1001/30000,y=pos-(y-544),score=float(scores[i])))
(p/'measurements-v8/late-phone-v10.json').write_text(json.dumps({'method':'Audio native gray-blue component measures chat camera through870; reply first20glyph-row spatial profile independently measures its entry; uniform phone alpha is solved from flat native blueRGB, not inferred from shrinking threshold bounds.','reply_reference_ink_bbox':box,'measurements':rows,'reply':reply,'reply_scores':all_reply},indent=2))
print('reply',reply[:5]);print('camera',[r for r in rows if r['frame']in[840,848,853,870,878,883,887]])
