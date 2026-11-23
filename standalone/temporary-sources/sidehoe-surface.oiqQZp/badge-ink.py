from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import label,find_objects,binary_closing
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
s=json.loads((p/'project/scene.json').read_text())
track={f:box for f,*box in s['tracks']['closingMeasuredBox']}
for f in (704,706,709,712):
 print(f,track.get(f))
 if f not in track:continue
 x,y,w,h=track[f]
 xy=(x-w/2,y-h/2,x+w/2,y+h/2)
 for d in (src,old):
  img=Image.open(d/f'{f:06}.png').convert('RGB').transform((512,512),Image.Transform.EXTENT,xy,Image.Resampling.BICUBIC)
  a=np.asarray(img,dtype='int16')
  r,g,b=np.moveaxis(a,2,0)

  for x0,y0,x1,y1 in ((209,145,297,200),(202,198,306,237),(196,237,316,260),(196,260,316,284),(135,200,172,235),(335,202,375,236)):
   q=a[y0:y1,x0:x1,:].mean(axis=2)
   y,x=np.where(q<100)
   if len(x) : print((x0+int(x.min()),y0+int(y.min()),x0+int(x.max())+1,y0+int(y.max())+1,len(x)),end=' ')
  print()
