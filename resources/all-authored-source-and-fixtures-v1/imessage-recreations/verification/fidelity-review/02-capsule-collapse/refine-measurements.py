from pathlib import Path
import json, numpy as np
from PIL import Image
from scipy import ndimage, signal
R=Path('/workspace/imessage-recreations'); P=R/'verification/fidelity-review/02-capsule-collapse'; S=json.load(open(R/'outputs/02-danieltian/final-v12/scene.json')); M=json.load(open(P/'measurements.json')); source={f:np.array(Image.open(P/'source'/f'{f-521:04d}.png').convert('RGB')) for f in range(522,553)}
def find(l,id):
 if l['id']==id:return l
 for c in l.get('children',[]):
  found=find(c,id)
  if found:return found
bodies={name:np.array(Image.open(R/'outputs/02-danieltian/final-v12'/find(next(l for l in S['layers']if l['id']=='pb-capsule-'+name),'pb-'+name+'-body')['src']).convert('RGB')) for name in ['lyft','airbnb','resy']}
for row in M['frames']:
 for name,p in row['providers'].items():
  X=p['x']; Y=p['y']; top=Y-12; region=source[row['frame']][top:Y+130,X-5:X+620]; neutral=(region.max(2)-region.min(2)<5)&(region.min(2)<246)&(region.min(2)>185); labs,n=ndimage.label(ndimage.binary_closing(neutral,structure=np.ones((3,3))));options=[]
  for i,box in enumerate(ndimage.find_objects(labs),1):
   if box is None:continue
   ys,xs=box; h=ys.stop-ys.start;w=xs.stop-xs.start
   if h>80 and w>100 and xs.start<15: options.append((int((labs[box]==i).sum()),xs.start,ys.start,w,h))
  if options:
   _,xx,yy,w,h=max(options); p['bodyY']=top+yy-1+(1 if name=='lyft' else 0);p['bodyX']=X-5+xx;p['bodyBorderHeight']=h
  else:p['bodyY']=None;p['bodyX']=658
  if p['bodyY']is not None:
   C=bodies[name]; X=p['bodyX'];Y=p['bodyY']; widths=[]
   for dy in range(5,18):
    a=C[dy]; b=source[row['frame']][Y+dy,X:X+620];aMask=(a.max(1)-a.min(1)<5)&(a.min(1)<245)&(a.min(1)>195);bMask=(b.max(1)-b.min(1)<5)&(b.min(1)<245)&(b.min(1)>195)
    if aMask.any()and bMask.any():widths.append(int(np.where(bMask)[0][-1]-np.where(aMask)[0][-1]+604))
   p['curveWidth']=float(np.median(widths))if widths else p['width']
  else:p['curveWidth']=None
# True search position uses strong glyph mask NCC; capsule rows are outside ROI.
q=next(l for l in S['layers']if l['id']=='pb-result-search')['children'][0]; template=np.array(Image.open(R/'outputs/02-danieltian/final-v12'/q['src']).convert('RGB')).astype(float)/255; T=1-template.mean(2); T[T<3/255]=0; h,w=T.shape; searches=[]
for f in range(525,540):
 target=source[f][230:420,370:1550].astype(float)/255; A=1-target.mean(2); A[A<3/255]=0; corr=signal.fftconvolve(A,T[::-1,::-1],mode='valid');integ=np.pad((A*A).cumsum(0).cumsum(1),((1,0),(1,0))); energy=integ[h:,w:]-integ[:-h,w:]-integ[h:,:-w]+integ[:-h,:-w]; scores=corr/np.sqrt(np.maximum(1e-12,energy*(T*T).sum())); y,x=np.unravel_index(scores.argmax(),scores.shape);searches.append(dict(frame=f,x=370+int(x),y=230+int(y),correlation=float(scores[y,x])))
M['searches']=searches;(P/'measurements-refined.json').write_text(json.dumps(M,indent=2))
for row in M['frames']:
 if row['frame']>=526:print(row['frame'],[(n,p['bodyX'],p['bodyY'],p['curveWidth'])for n,p in row['providers'].items()])
print('SEARCHES',searches)
