from pathlib import Path
from PIL import Image
import numpy as np,json,sys
p=Path(__file__).parent;sys.path.insert(0,str(p/'project'))
from render import interpolate
d=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),Path('/tmp/sidehoe-surface.oiqQZp/final-frames')]
t=json.loads((p/'project/scene.json').read_text())['tracks']
for f in range(392,403):
 l,top,r,b=map(round,interpolate(t['sendSuggestionBox'],f))
 info=[]
 for path in d:
  a=np.asarray(Image.open(path/f'{f:06}.png').convert('RGB'),dtype=np.int16)
  one=[]
  for x0,x1 in ((r-340,r-185),(r-203,r-14)):
   y0,y1=b-3,b+87
   aclip=a[y0:y1,x0:x1]
   R,G,B=np.moveaxis(aclip,2,0)
   # Chip colour is distinguishable from the cursor and cyan bubble.
   gray=((G>=157)&(G<249)&(np.abs(R-G)<13)&(np.abs(B-G)<15))
   purple=((G>=170)&(G<247)&(B>G+5)&(R>G+5))
   mask=gray if x0<r-300 else purple
   yy,xx=np.where(mask)
   if yy.size:
    coords=np.percentile(np.r_[xx[None,:]+x0,yy[None,:]+y0],(2,98),axis=1).T.reshape(-1).round().astype(int).tolist()
    vals=np.median(aclip[mask],axis=0).round().astype(int).tolist()
    one.append([coords,vals])
   else:one.append(None)
  info.append(one)
 print(f,b,info)
