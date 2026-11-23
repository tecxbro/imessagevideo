from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import label,binary_closing
from scipy.optimize import least_squares
r=Path(__file__).parent
for f in range(397,409):
 print(f)
 for path in ('/tmp/sidehoe-hyperframes.wG3QA2/source-stage','/tmp/sidehoe-thread-audit.oxTJaL/frames'):
  rgb=np.asarray(Image.open(Path(path)/f'{f:06}.png').convert('RGB'),float)
  for x0,y0,x1,y1 in ((320,70,1000,555),(100,560,920,1000)):
   a=rgb[y0:y1,x0:x1]
   r,g,b=a.transpose(2,0,1)
   m=binary_closing(((b-r>18)|(g-r>18)),iterations=3)
   l,n=label(m); counts=np.bincount(l.ravel()); counts[0]=0
   for j in sorted(np.argsort(counts)[-4:],key=lambda j: np.where(l==j)[0].min()):
    if counts[j]<380: continue
    y,x=np.where(l==j)
    print((x.min()+x0,y.min()+y0,x.max()+x0,y.max()+y0),end=' ')
  print()
