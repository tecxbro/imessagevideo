from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import uniform_filter1d,gaussian_filter1d
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-flight';REF=R/'references/05-linq';D=json.load(open(REF/'flight-document-camera-refined-review.json'));cam={q['frame']:q for q in D['camera']};doc=np.array(Image.open(REF/'assets/flight-document-review/diagnostic-doc-composite.png').convert('RGB')).astype('float32')/255;doc=doc[:,24:560:8];lin=lambda v:np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);srgb=lambda v:np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055);L=lin(doc);models=[]
for kind,vals in [('box',range(21,102,4)),('gaussian',range(8,37,2))]:
 for s in vals:models.append((kind,s,srgb(uniform_filter1d(L,s,axis=0,mode='nearest')if kind=='box'else gaussian_filter1d(L,s,axis=0,mode='nearest'))))
results=[]
for f in range(370,380):
 S=np.array(Image.open(P/'source'/f'{f-354:04d}.png').convert('RGB')).astype('float32')/255;q=cam[f];best=None;y0=max(80,round(q['y']+85));ys=np.arange(y0,700,2);T=S[ys,212:748:8]
 for kind,s,B in models:
  for Y in range(round(q['y'])-8,round(q['y'])+9):
   iy=ys-Y
   if iy.min()<0 or iy.max()>=len(B):continue
   d=T-B[iy];mse=float((d*d).mean());mae=float(abs(d).mean()*255);v=dict(frame=f,y=Y,kernel=kind,spread=s,mse=mse,mae=mae)
   if best is None or mse<best['mse']:best=v
 results.append(best);print(best,flush=True);q['previous_shutter']={k:q[k]for k in ['y','kernel','spread']};q.update({k:best[k]for k in ['y','kernel','spread']})
D['linear_shutter_fit']=results;(REF/'flight-document-camera-linear-review.json').write_text(json.dumps(D,indent=2))
