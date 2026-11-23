from pathlib import Path
from PIL import Image
from scipy.ndimage import label,find_objects,binary_closing,gaussian_filter1d
import numpy as np,json,sys
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-surface.oiqQZp/final-frames')
scene=json.loads((p/'project/scene.json').read_text())
keys=scene['tracks']
for f in range(390,404):
 print(f,end=' ')
 for d in [src,old]:
  a=np.array(Image.open(d/f'{f:06}.png').convert('RGB'),int)
  rec=[]
  for k in ('sendReplyBox','sendSuggestionBox'):
   x,y,r,b=map(round,interpolate(keys[k],f))
   patch=a[max(0,y-35):b+10,x-18:r+12]
   q=patch[:,:,2]-patch[:,:,0]
   sample=patch[(q>np.percentile(q,80))& (q>15)]
   p0=q.max()*.49
   yy,xx=np.where((q>p0)&(q>15))
   if len(xx):
    rec.append([x-18+xx.min(),y-35+yy.min(),x-18+xx.max()+1,y-35+yy.max()+1,np.median(sample,axis=0).astype(int).tolist()])
   else:rec.append(None)
  print(rec,end=' ')
 print()
