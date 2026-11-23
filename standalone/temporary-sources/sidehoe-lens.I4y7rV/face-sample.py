from PIL import Image
from pathlib import Path
import numpy as np
import sys,json
p=Path(__file__).parent
a=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=p/'combined-frames'
j=json.loads((p/'tile-probe/project/scene.json').read_text())['tracks']
def lookup(key,f):
 return next(z[1:] for z in j[key] if z[0]==f)
levels=np.array([.07,.09,.12,.15,.20,.27,.345,.415,.51,.57,.68,.82,.98])
for y in levels:
 print(f'{y:.3f}',end=' ')
 for x in (.09,.17,.50,.82,.91):
  for d in (a,b):
   data=[]
   for f in range(605,615):
    center,cy,w=lookup('blueOrbit',f)
    aspect=lookup('calendarTileTreatment',f)[-1]
    h=round(292*aspect)
    rim_y=cy-(128+h-256)*w/256
    xp=round(center+((x-.5)*w))
    yp=round(rim_y+y*h*w/256)
    rgb=np.array(Image.open(d/f'{f:06}.png'),dtype=float)[yp-2:yp+3,xp-3:xp+4,:3]
    if np.median(rgb[:,:,0])>217 and .30<y<.77: continue
    data.append(np.median(rgb,axis=(0,1)))
   print(','.join(map(str,np.rint(np.median(data,axis=0)).astype(int))),end=' ')
 print()
