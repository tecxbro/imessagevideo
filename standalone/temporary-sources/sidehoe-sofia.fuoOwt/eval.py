from pathlib import Path
from PIL import Image,ImageDraw
import sys
import numpy as np
p=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
previous=Path('/tmp/sidehoe-exit.H4euj0/tile-push-full')
output=p/sys.argv[1]
frames=range(329,340)
parts=(list(range(329,334)),list(range(334,340)))
for n,part in enumerate(parts):
 sheet=Image.new('RGB',(192*len(part),954),'white'); d=ImageDraw.Draw(sheet)
 for i,f in enumerate(part):
  crop=(194,0,806,1000)
  imgs=[Image.open(base/f'{f:06}.png').convert('RGB') for base in (source,previous,output)]
  a,b,c=[np.asarray(i,dtype=np.int16) for i in imgs]
  first,second=np.abs(a-b),np.abs(a-c)
  print(f,*(tuple(round(float(i.mean()),3) for i in [first,second,first[:225],second[:225],first[225:650],second[225:650],first[650:],second[650:]])))
  for j,im in enumerate(imgs):
   im=im.crop(crop); im.thumbnail((189,298),Image.Resampling.LANCZOS)
   x=i*192;y=j*318
   sheet.paste(im,(x,y+19)); d.text((x+4,y+3),f'{f} {("source","before","probe")[j]}',fill='black')
 sheet.save(p/f'{sys.argv[1]}-{n}.jpg',quality=94)
