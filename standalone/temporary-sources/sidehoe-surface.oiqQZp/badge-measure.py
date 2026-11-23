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
  mask=(r>132)&(r-g>13)&(r>g)&(r>=b)
  mask[:111,:]=0;mask[448:,:]=0;mask[:,:60]=0;mask[:,452:]=0
  cc,n=label(binary_closing(mask,iterations=2))
  print(d.name,[(sl[1].start,sl[0].start,sl[1].stop,sl[0].stop,(cc[sl]==i).sum()) for i,sl in enumerate(find_objects(cc),1) if (cc[sl]==i).sum()>250])
  sample=[(256,20),(70,120),(256,112),(256,141),(221,178),(272,202),(129,197),(319,251),(236,342),(255,357),(276,320),(255,392),(255,398)]
  print([np.rint(np.median(a[yy-1:yy+2,xx-1:xx+2],axis=(0,1))).astype(int).tolist() for xx,yy in sample])
