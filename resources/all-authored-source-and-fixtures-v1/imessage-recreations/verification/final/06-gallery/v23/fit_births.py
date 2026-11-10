from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys
from scipy.ndimage import shift
R=Path('/workspace/imessage-recreations');D=R/'verification/final/06-gallery/v23';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(R/'outputs/06-gallery/final-v22/scene.json'));parent=next(n for n in s['layers'] if n['id']=='g-1306');nodes={n['id']:n for n in parent['children']};results=[];prior={(q['name'],q['frame']):q for q in json.load(open(D/'birth-fits-origin649-trial.json'))};births={'Fuji':714,'Wait':734,'Order':745,'Done':770,'Remember':781}
for name,center in [('Fuji',714),('Wait',735),('Order',747),('Done',765),('Remember',780)]:
 n=nodes['phone-v17-message-'+name];A=np.array(Image.open(R/'outputs/06-gallery/final-v22'/n['src']).convert('RGB')).astype(float);w,h=n['width'],n['height'];blue=name in ['Wait','Order']
 if blue:
  ink=np.maximum(0,A[:,:,2]-A[:,:,0]);mask=ink>50
 else:
  ink=np.maximum(0,250-A.mean(2));mask=(ink>40)&(A.max(2)-A.min(2)<20)
 # Integer/subpixel shift model of the independently bounded original UI material.
 for f in range(births[name],births[name]+14):
  if f>796:continue
  src=np.array(Image.open(D/f'source-birth/{f-679:06d}.png').convert('RGB')).astype(float)
  py=rp.state(parent,f/30)['y'];x0=620+n['x']-648;base=n['y']+py-320;y0=int(np.floor(base));frac=base-y0
  best=None
  pred=prior.get((name,f),{}).get('dy',[28,19,13.5,10.25,7.75,5.75,4.25,3.25,2.5,1.75,1.25,.75,.5,.25][f-births[name]])
  for dy in np.arange(max(0,pred-2),pred+2.01,.25):
   Y=int(np.floor(y0+dy));fy=frac+dy-np.floor(dy)
   if Y<0 or Y+h>src.shape[0]:continue
   roi=src[Y:Y+h,int(x0):int(x0)+w]
   C=np.maximum(0,roi[:,:,2]-roi[:,:,0]) if blue else np.maximum(0,250-roi.mean(2))
   T=shift(ink,(fy,0),order=1,mode='constant');M=shift(mask.astype(float),(fy,0),order=0,mode='constant')>.5
   if not blue:M &= roi.max(2)-roi.min(2)<25
   alpha=float(np.clip((T[M]*C[M]).sum()/max(1,(T[M]**2).sum()),0,1.2))
   error=float(np.mean((C[M]-alpha*T[M])**2))
   # Null source is a valid zero-opacity state, with no pose claim.
   quality=float((T[M]*C[M]).sum()/max(1,np.sqrt((T[M]**2).sum()*(C[M]**2).sum())))
   score=float((T[M]*C[M]).sum()**2/max(1,(T[M]**2).sum()))
   if best is None or score>best['score']:
    best=dict(alpha=alpha,dy=float(dy),mse=error,correlation=quality,score=score)
  results.append(dict(name=name,frame=f,parentY=py,**best))
(D/'birth-fits.json').write_text(json.dumps(results,indent=2))
for name in ['Fuji','Wait','Order','Done','Remember']:
 print(name)
 for q in results:
  if q['name']==name:print(q['frame'],round(q['alpha'],3),q['dy'],round(q['mse'],1),round(q['correlation'],3))
# Source-only native crop strip establishes the measured onset visually.
for name,center in [('Fuji',714),('Wait',735),('Order',747),('Done',765),('Remember',780)]:
 n=nodes['phone-v17-message-'+name];rows=list(range(center-5,center+5));im=Image.new('RGB',(700,120*len(rows)),'#ccc');dr=ImageDraw.Draw(im)
 for j,f in enumerate(rows):
  a=Image.open(D/f'source-birth/{f-679:06d}.png');py=rp.state(parent,f/30)['y'];box=(int(620+n['x']-648)-10,int(n['y']+py-320)-5,int(620+n['x']-648+n['width'])+10,int(n['y']+py-320+n['height'])+45);a=a.crop(box);a.thumbnail((650,95));im.paste(a,(40,j*120+20));dr.text((4,j*120+3),str(f),fill='black')
 im.save(D/f'{name}-birth-strip.jpg',quality=94)
