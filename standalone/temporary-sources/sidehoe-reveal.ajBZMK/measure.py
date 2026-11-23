from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from scipy.optimize import least_squares
root=Path(__file__).parent
scene=json.loads((root/'project/scene.json').read_text())
pos=dict((f,(x,y,w)) for f,x,y,w in scene['tracks']['assistantMeasuredPosition'])
def atlas(f,label):
 return np.asarray(Image.open(root/label/f'{f-133:03}.png')).astype('float32')
def circle(a, x_range,y_range, field):
 x0,x1=x_range; y0,y1=y_range
 r,g,b=np.moveaxis(a[y0:y1,x0:x1],2,0)
 if field=='left':
  mask=(r-b>26)&(g-b>15)&(r<243)
 elif field=='right':
  mask=(b-r>27)&(b-g>16)&(r<185)
 else:
  mask=(r<135)&(g<130)&(b<145)
 yy,xx=np.indices(mask.shape)
 outer=mask & (((xx+x0-np.mean(x_range))/(x1-x0))**2+((yy+y0-np.mean(y_range))/(y1-y0))**2<.24)
 inds=np.argwhere(outer)
 if len(inds)<120:return ()
 t,bottom=np.percentile(inds[:,0]+y0,[1,99])
 l,r=np.percentile(inds[:,1]+x0,[1,99])
 return np.round([l,t,r,bottom,*(inds.mean(axis=0)[::-1]+[x0,y0])],1).tolist()
for f in range(134,162):
 x,y,w=pos[f]
 print('FRAME',f,end=' ')
 for tag in ('source','prior'):
  a=atlas(f,tag)
  yy=np.mean(a,axis=2)
  line_med=np.minimum(252,yy[:y-24,280:726])
  diff=np.clip(250-line_med,0,255)
  curve=np.mean(diff,axis=1)
  detected=np.flatnonzero(curve>max(.45,curve.max()*.065))
  title=[]
  for part in np.split(detected,np.flatnonzero(np.diff(detected)>2)+1):
   if len(part)<4:continue
   xs=np.flatnonzero(diff[part].mean(axis=0)>max(2.,curve.max()*.15))
   if xs.size:
    title.append((int(xs[0]+280),int(part[0]),int(xs[-1]+281),int(part[-1]+1),int(np.quantile(line_med[np.ix_(part,xs)],.10))))
  local_y=int(y+402)
  circ=[circle(a,box,(max(0,local_y-110),min(1000,local_y+111)),theme) for box,theme in [((120,330),'left'),((377,625),'middle'),((682,889),'right')]]
  name=gaussian_filter1d(np.mean(np.clip(235-yy[:,224:290],0,200),axis=1),2.2)
  ticks=[(int(i),int(name[i])) for i in find_peaks(name,prominence=7,distance=19)[0] if i>y+530]
  print(tag[0],title,circ,ticks,end=' | ')
 print()
