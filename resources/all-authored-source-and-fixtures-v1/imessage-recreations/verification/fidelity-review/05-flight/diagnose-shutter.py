from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import uniform_filter1d,gaussian_filter1d,map_coordinates
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-flight';A=R/'references/05-linq/assets/flight-document-review';D=json.load(open(R/'references/05-linq/flight-document-camera-refined-review.json'));cam={q['frame']:q for q in D['camera']};doc=np.array(Image.open(A/'diagnostic-doc-composite.png').convert('RGB'))/255
lin=lambda v:np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
srgb=lambda v:np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055)
# Region where document is fully opaque throughout exposure. Avoid unknown BG/edge.
for f in [372,374]:
 S=np.array(Image.open(P/'source'/f'{f-354:04d}.png').convert('RGB'))/255;Y=cam[f]['y'];best=[]
 for mode in ['sRGB','linear']:
  C=doc if mode=='sRGB'else lin(doc);b=None
  for kind in ['box','gaussian']:
   for spread in range(17,102,4)if kind=='box'else range(10,45,2):
    B=uniform_filter1d(C,spread,axis=0,mode='nearest')if kind=='box'else gaussian_filter1d(C,spread,axis=0,mode='nearest');B=B if mode=='sRGB'else srgb(B)
    for dy in range(-8,9,2):
     y=int(Y+dy);y0=max(80,int(y+70));y1=700;sy0=y0-y;sy1=y1-y
     if sy0<0 or sy1>len(B):continue
     err=np.abs(S[y0:y1,212:748]-B[sy0:sy1,24:560]).mean()*255;q=(float(err),kind,spread,y)
     if b is None or q[0]<b[0]:b=q
  best.append((mode,b))
 print(f,best,flush=True)
