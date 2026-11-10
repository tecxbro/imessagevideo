"""Fit three independently flying menu Memoji from isolated authentic artwork."""
from pathlib import Path
from PIL import Image
import json
import numpy as np
from scipy.signal import fftconvolve
p=Path(__file__).parent;s=json.loads((p/'final-v12.scene.json').read_text());specs=[('alice','p03-205',636,[700,0,1110,300]),('bob','p03-206',637,[350,250,900,1000]),('laptop','p03-207',638,[1250,200,1700,1080])];records={}
for name,ident,birth,bounds in specs:
 layer=next(x for x in s['layers'] if x['id']==ident);im=Image.open(p/layer['src']).convert('RGBA');white=Image.new('RGBA',im.size,(253,253,253,255));white.alpha_composite(im);im=white.convert('RGB')
 if name=='laptop':
  im=im.crop((31,27,124,122));im.save(p/'assets/laptop-person-menu-core-v13.png');layer['width']=94;layer['height']=96
 last=None;out=[]
 for f in range(birth,702):
  a=np.array(Image.open(p/'lunch-native'/f'{f-609:03}.png').resize((960,540),Image.Resampling.LANCZOS),dtype=float);best=None
  bb=bounds if last is None or f<=651 else [last['x']-130,last['y']-130,last['x']+last['width']+130,last['y']+last['height']+130]
  x0=max(0,round(bb[0]/2));y0=max(0,round(bb[1]/2));x1=min(960,round(bb[2]/2));y1=min(540,round(bb[3]/2));reg=(253-a[y0:y1,x0:x1])/255
  for ratio in ([.7,.85,1,1.15] if name=='laptop' else [.85,1,1.15]):
   w=round(layer['width']*ratio/2);h=round(layer['height']*ratio/2);r=np.array(im.resize((w,h),Image.Resampling.BILINEAR),dtype=float);d=(253-r)/255;mask=(r.max(2)-r.min(2)>12)|(r.mean(2)<110);d*=mask[:,:,None];den=(d*d).sum()
   if reg.shape[0]<h or reg.shape[1]<w:continue
   dot=sum(fftconvolve(reg[:,:,c],d[::-1,::-1,c],mode='valid') for c in range(3));energy=sum(fftconvolve(reg[:,:,c]**2,mask[::-1,::-1].astype(float),mode='valid') for c in range(3));cos=dot/np.sqrt(np.maximum(energy*den,1e-9));iy,ix=np.unravel_index(cos.argmax(),cos.shape);amp=dot[iy,ix]/max(den,1e-9);score=float(cos[iy,ix]);q={'frame':f,'t':f/30,'x':float((x0+ix)*2),'y':float((y0+iy)*2),'width':w*2,'height':h*2,'cosine':score,'opacity':float(np.clip(amp,0,1))}
   if best is None or score>best['cosine']:best=q
  if best is None:continue
  if best['cosine']>.85 and best['opacity']>.3:
   last=best
  else:
   best['opacity']=0
  # Reject false re-detection after the source characters fade into the sheet.
  if f>=702:best['opacity']=0
  out.append(best)
 records[name]={'id':ident,'birth':birth,'fits':out,'src':'assets/laptop-person-menu-core-v13.png' if name=='laptop' else layer['src']};print(name,[(q['frame'],round(q['x']),round(q['y']),round(q['cosine'],2),round(q['opacity'],2)) for q in out if q['frame'] in [640,645,651,660,666,680,690,695]],flush=True)
(p/'menu-avatar-v13-measurements.json').write_text(json.dumps(records,indent=2))
