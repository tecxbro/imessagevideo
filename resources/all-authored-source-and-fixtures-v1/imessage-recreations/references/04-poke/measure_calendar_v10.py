"""Register native calendar heading glyphs; avoid ambiguous blue-edge aliases."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.fft import rfft,irfft,next_fast_len
p=Path(__file__).parent;decoded=p/'measurements-v8/decoded';templates=[]

def profile(a):
    gray=a.astype(float).mean(axis=2);edges=np.linspace(0,gray.shape[1],21).astype(int)
    bins=np.stack([gray[:,edges[i]:edges[i+1]].mean(axis=1)for i in range(20)],axis=1)
    return bins-bins.mean(axis=1,keepdims=True)
for name,frame,box,local_y in [('Dinner',184,[243,596,693,638],101),('Thursday',184,[241,805,676,855],310),('Friday',212,[243,675,592,725],791)]:
    a=np.array(Image.open(decoded/f'{frame:06}.png').convert('RGB'));x,y,x2,y2=box;t=profile(a[y:y2,x:x2]);size=next_fast_len(1080+t.shape[0]-1)
    templates.append(dict(name=name,x=x,x2=x2,local_y=local_y,template=t,size=size,fft=rfft(t,n=size,axis=0),energy=float((t*t).sum())))
rows=[]
for n in range(168,261):
    a=np.array(Image.open(decoded/f'{n:06}.png').convert('RGB'));choices=[]
    for t in templates:
        s=profile(a[:,t['x']:t['x2']]);h=t['template'].shape[0];fft=rfft(s,n=t['size'],axis=0);corr=irfft((fft*np.conj(t['fft'])).sum(axis=1),n=t['size'])[:1080-h+1];energy=np.r_[0,np.cumsum((s*s).sum(axis=1))];norm=energy[h:]-energy[:-h];score=np.where(norm>100, corr/np.sqrt(np.maximum(1,norm*t['energy'])),0);idx=int(score.argmax());y=float(idx)
        if 0<idx<len(score)-1:
            den=score[idx-1]-2*score[idx]+score[idx+1]
            if abs(den)>1e-8:y+=float(np.clip(.5*(score[idx-1]-score[idx+1])/den,-.5,.5))
        if score[idx]>.94:choices.append(dict(heading=t['name'],score=float(score[idx]),ink_y=y,sheet_y=y-t['local_y']))
    if choices:
        best=max(choices,key=lambda c:c['score']);rows.append(dict(frame=n,time=n*1001/30000,sheet_y=best['sheet_y'],best=best,all_matches=choices))
(p/'measurements-v8/calendar-glyph-camera-v10.json').write_text(json.dumps({'method':'Exact original heading glyph spatial profiles in20horizontal bins, zero row mean; per-native-frame normalized FFT registration. Measured heading-local offsets from original184/212, not candidate glyph dimensions.','measurements':rows},indent=2))
for n in[173,175,176,177,180,184,212,219,240,259,260]:print(next((r for r in rows if r['frame']==n),None))
