from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).parent
for tag in ('source','prior'):
 i=Image.open(p/tag/'051.png')
 bbox=(376,376,624,624) if tag=='source' else (375,374,625,624)
 a=np.asarray(i.crop(bbox).resize((512,512),Image.Resampling.LANCZOS)).astype(float)
 rr,gg,bb=(a[:,:,k] for k in range(3))
 print(tag)
 for y in [80,120,130,134,140,150,164,170,180,190,200,205,210,220,228,235,246,257,268,278,286,294,307,322,338,351,364,380,392,403,410]:
  pos=np.flatnonzero((rr[y]>130)&(gg[y]>55))
  print(y,[(int(q[0]),int(q[-1])) for q in np.split(pos,np.flatnonzero(np.diff(pos)>1)+1) if len(q)>2], [[int(x) for x in list(a[y,x])] for x in [200,254,291]] if y in [150,205,268,294,322,351,380,392] else '')
 i.crop(bbox).resize((512,512)).save(p/f'badge-{tag}.png')
