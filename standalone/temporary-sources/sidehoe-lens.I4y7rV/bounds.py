from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import label,binary_closing
s=json.load(open(Path(__file__).parent/'project/scene.json'))
for k in ['assistantMeasuredPosition','assistantBevelDepth','assistantPinPose','assistantIslandBox','assistantBodyFocus','assistantRowPose','assistantPinControls']:
 print(k,[x for x in s['tracks'][k] if 134<=x[0]<=139])
for f in range(134,138):
 print('frame',f)
 for key in ('/tmp/sidehoe-hyperframes.wG3QA2/source-stage','/tmp/sidehoe-thread-audit.oxTJaL/frames'):
  a=np.asarray(Image.open(Path(key)/f'{f:06}.png').convert('L'))
  print(end=('source ' if 'source' in key else ' prior '))
  for x,y,r,b in ((340,510,665,825),(325,307,685,455),(370,451,629,560)):
   g=a[y:b,x:r]; m=binary_closing(g<155,iterations=3); l,n=label(m)
   indexes=np.bincount(l.ravel()); indexes[0]=0
   if max(indexes,default=0):
    mask=(l==indexes.argmax()) if y!=451 else (l>0)
    j,i=np.where(mask); print((i.min()+x,j.min()+y,i.max()+x,j.max()+y, len(i)),end=' ')
  print()
