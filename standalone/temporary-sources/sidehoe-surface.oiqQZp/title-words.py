from pathlib import Path
from PIL import Image,ImageFont
import numpy as np
p=Path(__file__).parent
for f in (188,190,193,196,200,207):
 for root in ('/tmp/sidehoe-hyperframes.wG3QA2/source-stage','/tmp/sidehoe-lens.I4y7rV/combined-frames'):
  q=np.asarray(Image.open(Path(root)/f'{f:06}.png').convert('RGB'),int)
  ma=(q[:,:,0]<160)&(q[:,:,1]<142)&(q[:,:,2]<167)
  ys=np.where(ma[:,265:700].sum(axis=1)>8)[0]
  ys=ys[(ys>210)&(ys<630)]
  split=[np.arange(a,b) for a,b in {188:[(440,485),(505,567)],190:[(435,481),(500,563)],193:[(429,473),(491,554)],196:[(418,466),(483,545)],200:[(396,446),(462,524)],207:[(327,376),(389,446)]}[f]]
  print(f,Path(root).name, [(int(s[0]),int(s[-1])) for s in split])
  for band in split[:2]:
   mask=ma[band,:]
   xs=np.where(mask.sum(axis=0)>1)[0]
   print([(int(g[0]),int(g[-1])) for g in np.split(xs,np.where(np.diff(xs)>4)[0]+1) if len(g)>0],end=' ')
  print()
