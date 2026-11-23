from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter1d
import numpy as np,json,sys
p=Path(__file__).parent;sys.path.insert(0,str(p/'project'))
from render import interpolate
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-seam.lfpGEs/clean-frames')
j=json.loads((p/'project/scene.json').read_text())['tracks']
for f in range(313,326):
 print(f, 'camera',np.round(interpolate(j['sofiaMeasuredCamera'],f),2),
         'exposure',np.round(interpolate(j['sofiaExposure'],f),2))
 for d in [source,prior]:
  q=np.array(Image.open(d/f'{f:06}.png').convert('L'),dtype=float)
  row=np.median(q[100:430],axis=0)
  dark=[]
  for x,y in ((200,460),(570,830)):
   c=np.flatnonzero(row[x:y]<150)+x
   dark.append([int(c[0]),int(c[-1])] if len(c) else [])
  bot=[]
  for x in (335,390,470,535,605,670):
   signal=gaussian_filter1d(q[:,x],1.2)
   y=np.flatnonzero(signal<178)
   bot.append(int(y[-1]) if len(y) else None)
  print(d.name,dark,bot)
