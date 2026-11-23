from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).parent
d=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),Path('/tmp/sidehoe-surface.oiqQZp/final-frames'),p/'calendar']
for f in (394,395,396,397,399,400,401,402,403,407,408,409):
 z=[]
 for q in d:
  two=[]
  for r in [f-1,f]:
   g=Image.open(q/f'{r:06}.png').convert('L').resize((64,36),Image.Resampling.BOX)
   two.append(np.asarray(g,dtype=np.int16))
  z.append(np.abs(two[0]-two[1]).reshape(6,6,8,8).mean((1,3)))
 a,b,c=z
 print(f,'difference',round(a.mean(),3),round(b.mean(),3),round(c.mean(),3))
 if f in [396,401,408]:
  print(np.round(a-c,1))
