from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.optimize import nnls
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';P=R/'verification/fidelity-review/05-flight';D=json.load(open(REF/'flight-document-camera-linear-review.json'));doc=np.array(Image.open(REF/'assets/flight-document-review/diagnostic-doc-composite.png').convert('RGB')).astype(float)/255;lin=lambda v:np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);docL=lin(doc);by={q['frame']:q for q in D['camera']};fit=[]
for f in range(370,380):
 q=by[f];Y=q['y'];S=np.array(Image.open(P/'source'/f'{f-354:04d}.png').convert('RGB')).astype(float)/255;ys=np.arange(max(110,Y+120),min(700,len(docL)+Y-51),3).astype(int);xs=np.arange(24,560,12);offsets=np.arange(-50,51,2);T=lin(S[ys[:,None],188+xs[None,:]]).reshape(-1);columns=[]
 for off in offsets:columns.append(docL[(ys-Y-off)[:,None].astype(int),xs[None,:]].reshape(-1))
 A=np.array(columns).T;AA=np.vstack((A,np.ones((1,len(offsets)))*20,np.diff(np.eye(len(offsets)),axis=0)*.05));BB=np.r_[T,20,np.zeros(len(offsets)-1)];w,res=nnls(AA,BB,maxiter=1000);w/=w.sum();keep=np.argsort(w)[-41:];keep=sorted(keep[w[keep]>.00001]);ww=w[keep];ww/=ww.sum();samples=[dict(offset=int(offsets[i]),weight=float(v))for i,v in zip(keep,ww)];q['exposureSamples']=samples;err=float(abs(A[:,keep]@ww-T).mean());fit.append(dict(frame=f,linear_mae=err,samples=samples,mean_offset=float(sum(z['offset']*z['weight']for z in samples))));print(f,'linearMae',err,'nonzero',len(samples),'meanoffset',fit[-1]['mean_offset'],flush=True)
D['nonuniform_shutter_fit']=fit;(REF/'flight-document-camera-exposure-review.json').write_text(json.dumps(D,indent=2))
