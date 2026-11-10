"""Fit independent menu camera and staggered list births from native control/photo anchors."""
from pathlib import Path
from PIL import Image
import json
import numpy as np
from scipy.signal import fftconvolve
p=Path(__file__).parent;s=json.loads((p/'final-v12.scene.json').read_text());phone=next(x for x in s['layers'] if x['id']=='p03-204');menu=next(x for x in phone['children'] if x['id']=='p03-203');body=next(x for x in menu['children'] if x['id']=='p03-202');rows=json.loads((p/'menu-v13-measurements.json').read_text());rows={r['frame']:r for r in rows};templates=[Image.open(p/body['children'][i*7+3]['src']).convert('RGB') for i in range(6)];records=[];hw={q['frame']:q for q in json.loads((p/'late-hardware-v13-measurements.json').read_text())}
def sample(track,t):
 if t<=track[0]['t']:return track[0]['value']
 for a,b in zip(track,track[1:]):
  if t<=b['t']:
   u=(t-a['t'])/(b['t']-a['t']);return a['value']*(1-u)+b['value']*u
 return track[-1]['value']
def oldpose(f):
 t=f/30;return {k:sample(phone['keyframes'][k],t) for k in ['x','y','scaleX']}
def match(image,template,x,y,scale):
 w=round(176*scale/2);h=w
 if w<12:return None
 # Match at half resolution in a bounded search, using white-subtracted RGB.
 r=np.array(template.resize((w,h),Image.Resampling.BILINEAR),dtype=float);d=(253-r)/255;mask=(r.max(2)-r.min(2)>20)|(r.mean(2)<140);d*=mask[:,:,None];den=(d*d).sum()
 xx=round(x/2);yy=round(y/2);x0=max(0,xx-18);x1=min(960,xx+w+19);y0=max(0,yy-30);y1=min(540,yy+h+31)
 if x1-x0<w or y1-y0<h:return None
 reg=(253-image[y0:y1,x0:x1])/255;dot=sum(fftconvolve(reg[:,:,c],d[::-1,::-1,c],mode='valid') for c in range(3));energy=sum(fftconvolve(reg[:,:,c]**2,mask[::-1,::-1].astype(float),mode='valid') for c in range(3));cos=dot/np.sqrt(np.maximum(energy*den,1e-9));iy,ix=np.unravel_index(cos.argmax(),cos.shape);amp=dot[iy,ix]/max(den,1e-9)
 return {'x':float((x0+ix)*2),'y':float((y0+iy)*2),'cosine':float(cos[iy,ix]),'opacity':float(np.clip(amp,0,1))}
prev=None
for f in range(618,735):
 a=np.array(Image.open(p/'lunch-native'/f'{f-609:03}.png').resize((960,540),Image.Resampling.LANCZOS),dtype=float);c=rows[f]['check'];old=oldpose(f)
 if c and f<731 and c['box'][1]>2:
  scale=(c['diameter']+1.125)/75;x=c['cx']-694.5*scale;y=c['cy']-244.5*scale;anchor='check'
 elif c and f>=731:
  scale=(c['diameter']+1.125)/75;x=c['cx']-694.5*scale;y=c['cy']-244.5*scale;anchor='closing-check'
 elif prev:
  po=oldpose(f-1);scale=prev['scale']*old['scaleX']/po['scaleX'];x=prev['x']+(old['x']-po['x']);y=prev['y']+(old['y']-po['y']);anchor='predicted'
 else:scale=old['scaleX'];x=old['x'];y=old['y']+1200*scale;anchor='old'
 if anchor=='predicted' and f<731:scale=hw[f]['scale']*.9937
 matches=[]
 # Fit actual photo scale once the cyan check has scrolled above the viewport.
 if anchor=='predicted' and 682<=f<731:
  candidates=[]
  visible=[i for i in range(6) if -20<y+(348+236*i)*scale<1000][:3]
  for factor in [.97,.985,1,1.015]:
   ss=scale*factor;mm=[]
   for i in visible:
    q=match(a,templates[i],x+553*ss,y+(348+236*i)*ss,ss)
    if q:mm.append(q['cosine'])
   candidates.append((float(np.mean(sorted(mm,reverse=True)[:2])) if mm else 0,ss))
  scale=max(candidates)[1]
 for i,im in enumerate(templates):
  py=y+(348+236*i)*scale;px=x+553*scale
  if py<-176*scale or py>1080:matches.append(None);continue
  q=match(a,im,px,py,scale);matches.append(q)
 good=[(i,q) for i,q in enumerate(matches) if q and q['cosine']>.75 and q['opacity']>.65]
 if good and anchor=='predicted':
  x=float(np.median([q['x']-553*scale for i,q in good]));y=float(np.median([q['y']-(348+236*i)*scale for i,q in good]));anchor='photos'
 # Source list births are asynchronous; hidden rows remain absent until detected.
 birth=[624,627,630,633,636,639];presence=[]
 for i,q in enumerate(matches):
  if f<birth[i]:presence.append(0)
  else:presence.append(1)
 r={'frame':f,'t':f/30,'x':x,'y':y,'scale':scale,'anchor':anchor,'matches':matches,'row_presence':presence};records.append(r);prev=r
(p/'menu-world-v13-measurements.json').write_text(json.dumps(records,indent=2));print([(r['frame'],r['anchor'],round(r['x']),round(r['y']),round(r['scale'],3)) for r in records if r['frame'] in [618,619,620,624,640,651,666,680,700,729,731,734]])
