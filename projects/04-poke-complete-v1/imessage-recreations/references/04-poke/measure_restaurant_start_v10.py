"""Restaurant entry from exact original heading, before late legacy visibility gate."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.fft import rfft,irfft,next_fast_len
p=Path(__file__).parent;d=p/'measurements-v8/decoded';reference=np.array(Image.open(d/'000583.png').convert('RGB'));roi=(315,405,968,452);x,y,x2,y2=roi

def profile(a):
    gray=a.astype(float).mean(2);edges=np.linspace(0,gray.shape[1],21).astype(int);b=np.stack([gray[:,edges[i]:edges[i+1]].mean(1)for i in range(20)],1)
    return b-b.mean(1,keepdims=True)
t=profile(reference[y:y2,x:x2]);h=t.shape[0];size=next_fast_len(1080+h-1);tf=rfft(t,n=size,axis=0);te=(t*t).sum();rows=[]
for n in range(568,584):
 a=np.array(Image.open(d/f'{n:06}.png').convert('RGB'));z=profile(a[:,x:x2]);corr=irfft((rfft(z,n=size,axis=0)*np.conj(tf)).sum(1),n=size)[:1080-h+1];energy=np.r_[0,np.cumsum((z*z).sum(1))];den=energy[h:]-energy[:-h];score=np.where(den>100,corr/np.sqrt(np.maximum(1,den*te)),0);i=int(score.argmax());pos=float(i)
 if 0<i<len(score)-1:
  v=score[i-1]-2*score[i]+score[i+1]
  if abs(v)>1e-8:pos+=float(np.clip(.5*(score[i-1]-score[i+1])/v,-.5,.5))
 border=float(np.median(np.r_[a[:,:20].ravel(),a[:,-20:].ravel()]));row=dict(frame=n,time=n*1001/30000,score=float(score[i]),scrim_opacity=1-border/255)
 if score[i]>.94:row['sheet_y']=pos-(405-317.503592314697)
 rows.append(row)
(p/'measurements-v8/restaurant-entry-v10.json').write_text(json.dumps({'method':'Original653x47heading spatial ink profile, not white card threshold or legacy19.3s start. Exact source frames568–583.','measurements':rows},indent=2));print(rows)
