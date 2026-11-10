from pathlib import Path
import json,subprocess
import numpy as np
from scipy.signal import correlate
from PIL import Image
D=Path(__file__).resolve().parent;rows=json.loads((D/'native-thread-motion-v17.json').read_text());known={x['frame']:x for x in rows}
def prof(a):return np.maximum(0,250-a[:,:480].mean(axis=2)).mean(axis=1)
ref=np.asarray(Image.open(D/'keyframes/006.50.png').convert('RGB')).astype(float);pt=prof(ref[393:524,600:1500]);norm=float(np.dot(pt,pt));L=len(pt)
ref7=np.asarray(Image.open(D/'keyframes/007.50.png').convert('RGB')).astype(float);dt=prof(ref7[535:656,600:1500]);dn=float(np.dot(dt,dt));DL=len(dt)
def fit(profile,t,n,lo,hi):
 size=len(t);dot=correlate(profile,t,mode='valid',method='fft');sums=np.r_[0,np.cumsum(profile*profile)];sq=sums[size:]-sums[:-size];alpha=dot/n;error=np.maximum(0,sq-dot*dot/n)/n;valid=(np.arange(len(dot))>=lo)&(np.arange(len(dot))<=hi)&(alpha>.1);error[~valid]=1e9;at=int(np.argmin(error));sub=0.
 if 0<at<len(error)-1 and max(error[at-1],error[at+1])<1e8:
  dd=error[at-1]-2*error[at]+error[at+1]
  if dd>0:sub=float(np.clip(.5*(error[at-1]-error[at+1])/dd,-.5,.5))
 return at+sub,float(np.clip(alpha[at],0,1)),float(error[at])
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','4.8','-i',str(D/'source.mp4'),'-t',str(82/30),'-vf','crop=900:900:600:0','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE);out=[]
for f in range(144,226):
 raw=p.stdout.read(900*900*3)
 if len(raw)!=900*900*3:raise RuntimeError('Short event decode')
 a=np.frombuffer(raw,np.uint8).reshape(900,900,3).astype(float);profile=prof(a);prior=known.get(f);lo=max(0,798+prior['scroll_y']+20) if prior else 0;py,pa,pe=fit(profile,pt,norm,lo,760)
 scroll=prior['scroll_y'] if prior else py-863
 b=a[:,300:];sat=np.maximum(0,b[:,:,2]-b[:,:,0]);sat[b[:,:,2]<b[:,:,1]*1.05]=0;strong=sat>20;yy,xx=np.nonzero(strong);blue=None
 if len(xx)>1000:blue=[int(xx.min()+900),int(yy.min()),int(xx.max()+901),int(yy.max()+1)]
 dy,da,de=fit(profile,dt,dn,max(0,py+250),760)
 out.append({'frame':f,'scroll_y':scroll,'priya_body_y':py,'priya_alpha':pa,'priya_mse':pe,'book_blue_box':blue,'book_saturation':float(sat.sum()),'done_body_y':dy,'done_alpha':da,'done_mse':de})
p.wait();assert p.returncode==0
(D/'native-thread-events-v17.json').write_text(json.dumps(out,indent=2));print([x for x in out if x['frame'] in [148,149,150,165,174,180,195,204,210,225]])
