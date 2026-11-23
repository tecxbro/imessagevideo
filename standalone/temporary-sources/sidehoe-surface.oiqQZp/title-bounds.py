from pathlib import Path
from PIL import Image,ImageFont
import numpy as np
p=Path(__file__).parent
for k in ['/System/Library/Fonts/SFNS.ttf','/System/Library/Fonts/HelveticaNeue.ttc','/System/Library/Fonts/Helvetica.ttc','/System/Library/Fonts/Avenir Next.ttc']:
 for i in range(17):
  try:
   f=ImageFont.truetype(k,180,index=i)
   print(Path(k).name,i,f.getname(), [(a['name'],a['minimum'],a['default'],a['maximum']) for a in f.get_variation_axes()] if Path(k).name=='SFNS.ttf' else '')
  except OSError: break
for f in (188,190,193,196,200,207):
 for root in ('/tmp/sidehoe-hyperframes.wG3QA2/source-stage','/tmp/sidehoe-lens.I4y7rV/combined-frames'):
  q=np.asarray(Image.open(Path(root)/f'{f:06}.png').convert('RGB'),int)
  ma=(q[:,:,0]<160)&(q[:,:,1]<142)&(q[:,:,2]<167)
  ys=np.where(ma[:,265:700].sum(axis=1)>8)[0]
  ys=ys[(ys>210)&(ys<630)]
  split=[s for s in np.split(ys,np.where(np.diff(ys)>1)[0]+1) if len(s)>7]
  print(f,Path(root).name, [(int(s[0]),int(s[-1])) for s in split])
  for band in split[:2]:
   mask=ma[band,:]
   xs=np.where(mask.sum(axis=0)>1)[0]
   print([(int(g[0]),int(g[-1])) for g in np.split(xs,np.where(np.diff(xs)>8)[0]+1) if len(g)>0],end=' ')
  print()
