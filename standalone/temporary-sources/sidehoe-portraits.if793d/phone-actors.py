from scipy.ndimage import label,find_objects,binary_closing
import numpy as np
from PIL import Image
from pathlib import Path
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-seam.lfpGEs/clean-frames')
for f in range(313,326):
 print(f,end=' ')
 for r in [src,old]:
  x,y=300,0
  q=np.asarray(Image.open(r/f'{f:06}.png').convert('RGB'),np.int16)[y:690,x:699]
  c=q[:,:,2]-q[:,:,0]
  lm,n=label(binary_closing(c>65,iterations=2))
  output=[]
  for i,(yy,xx) in enumerate(find_objects(lm),1):
   if (lm[yy,xx]==i).sum()<90:continue
   output.append((x+xx.start,y+yy.start,x+xx.stop,y+yy.stop))
  print(output,end=' ')
 print()
