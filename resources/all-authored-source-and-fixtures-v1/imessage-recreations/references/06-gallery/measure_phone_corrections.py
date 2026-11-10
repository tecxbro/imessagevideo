"""Measure scroll/reveal and camera, keeping native motion separate from UI artwork."""
from pathlib import Path
import subprocess,json
import numpy as np
from scipy.signal import correlate
from PIL import Image
D=Path(__file__).resolve().parent
ref4=np.asarray(Image.open(D/'keyframes/004.00.png').convert('RGB')).astype(float)
template=(255-ref4[502:798,600:1100].mean(axis=2)).mean(axis=1);L=len(template);energy=float(np.dot(template,template))
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','4','-i',str(D/'source.mp4'),'-t',str(76/30),'-vf','crop=1080:1080:420:0','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE)
thread=[]
for f in range(120,196):
 raw=p.stdout.read(1080*1080*3)
 if len(raw)!=1080*1080*3:raise RuntimeError('Short thread decode')
 a=np.frombuffer(raw,np.uint8).reshape(1080,1080,3).astype(float);profile=(255-a[:1000,180:680].mean(axis=2)).mean(axis=1)
 sums=np.r_[0,np.cumsum(profile*profile)];sse=sums[L:]-sums[:-L]+energy-2*correlate(profile,template,mode='valid',method='fft');at=int(np.argmin(sse));sub=0.
 if 0<at<len(sse)-1:
  denom=sse[at-1]-2*sse[at]+sse[at+1]
  if denom>0:sub=float(np.clip(.5*(sse[at-1]-sse[at+1])/denom,-.5,.5))
 roi=a[300:850,:110];warm=np.maximum(0,roi[:,:,0]-roi[:,:,1]);warm[roi[:,:,0]<roi[:,:,2]*1.05]=0;weights=warm.sum(axis=1);sat=float(weights.sum());center=float(np.dot(np.arange(300,850),weights)/sat) if sat else None
 plus=np.max(a[760:970,50:110],axis=2)<100;yy,xx=np.nonzero(plus);plus_top=int(yy.min()+760) if len(yy)>30 else None
 kb=a[850:,380:680];km=(kb[:,:,2]-kb[:,:,0]>2)&(kb.mean(axis=2)<244)&(kb.mean(axis=2)>180);kr=np.where(km.sum(axis=1)>150)[0];keyboard_top=int(kr.min()+850) if len(kr) else None
 thread.append({'frame':f,'scroll_y':at+sub-502,'template_mse':float(sse[at]/energy),'priya_saturation':sat,'priya_center_y':center,'plus_top':plus_top,'keyboard_top':keyboard_top})
p.wait();assert p.returncode==0
(D/'native-thread-motion-v17.json').write_text(json.dumps(thread,indent=2))
ref=np.asarray(Image.open(D/'keyframes/026.50.png').convert('RGB')).astype(float)[:,620:1302]
def hardware_profile(a):return (255-np.concatenate([a[:,:46],a[:,-46:]],axis=1).mean(axis=2)).mean(axis=1)
t=hardware_profile(ref)[:320];den=float(np.mean(t*t));candidate=np.arange(-80,701)
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','23','-i',str(D/'source.mp4'),'-t',str(128/30),'-vf','crop=682:1080:620:0','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE)
phone=[]
for f in range(690,818):
 raw=p.stdout.read(682*1080*3)
 if len(raw)!=682*1080*3:raise RuntimeError('Short phone decode')
 a=np.frombuffer(raw,np.uint8).reshape(1080,682,3).astype(float);prof=hardware_profile(a);scores=[]
 for shift in candidate:
  lo=max(0,shift);hi=min(1080,shift+320);offset=lo-shift;scores.append(np.mean((prof[lo:hi]-t[offset:offset+hi-lo])**2))
 at=int(np.argmin(scores));sub=0.
 if 0<at<len(scores)-1:
  div=scores[at-1]-2*scores[at]+scores[at+1]
  if div>0:sub=float(np.clip(.5*(scores[at-1]-scores[at+1])/div,-.5,.5))
 phone.append({'frame':f,'camera_y':float(candidate[at]+sub),'normalized_mse':float(scores[at]/den)})
p.wait();assert p.returncode==0
(D/'native-birthday-camera-v17.json').write_text(json.dumps(phone,indent=2))
print('THREAD',[x for x in thread if x['frame'] in [120,132,138,144,150,156,165,180,195]])
print('PHONE',[x for x in phone if x['frame'] in [690,705,720,735,750,765,780,795,810,817]])
