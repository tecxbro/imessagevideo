from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import label,find_objects,binary_closing
D=Path('/tmp/sidehoe-optical.0heyYI')
o=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
t=np.array(json.loads((D/'settle-project/scene.json').read_text())['tracks']['sendCursor'])
for f in range(381,404):
 x,y=[np.interp(f,t[:,0],t[:,i]) for i in [1,2]]
 a=np.asarray(Image.open(o/f'{f:06}.png').convert('RGB'))
 x0,y0=max(0,round(x-24)),max(0,round(y-30))
 x1,y1=min(1000,round(x+105)),min(1000,round(y+137))
 ar=a[y0:y1,x0:x1].astype('int16')
 r,g,b=np.moveaxis(ar,2,0)
 gr=np.median(ar,axis=-1)
 achro=(np.abs(r-b)<13)&(np.abs(g-r)<10)
 n=[]
 for gray in (60,125,170,215):
  m=achro&(gr<gray)
  l,k=label(binary_closing(m,iterations=2))
  out=[]
  for i,(dy,dx) in enumerate(find_objects(l),1):
   aa=l[dy,dx]==i
   count=aa.sum()
   if count<50 or dy.stop-dy.start<12:continue
   top=np.argwhere(aa[:min(6,aa.shape[0])])
   out.append((count,(x0+dx.start,y0+dy.start,x0+dx.stop,y0+dy.stop),round(np.mean(top[:,1])+x0+dx.start,1),int(np.quantile(gr[dy,dx][aa],.25))))
  n.append(sorted(out,reverse=True)[:2])
 print(f,x,y,n)
