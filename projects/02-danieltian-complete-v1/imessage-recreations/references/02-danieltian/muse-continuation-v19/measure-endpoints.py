from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import map_coordinates
R=Path(__file__).resolve().parent;ROOT=R.parents[2];SRC=R.parent/'assets/middle-every-frame';raw=np.array(Image.open(ROOT/'outputs/02-danieltian/final-v18/assets/c5968c7a63d20083211360f8af2a8a2ea732595908c62ab0a129f917f4ecbcaf.png').convert('RGBA')).astype(float);K=np.pad((253-raw[:,:,:3])*raw[:,:,3:]/255,((8,8),(8,8),(0,0)));m={q['frame']:q['clone'] for q in json.load(open(R/'overlap-measurements.json'))['frames']};priors={665:[m[666]['x']-.4,m[666]['y']+14,m[666]['scale']+.003],670:[m[669]['x']+.267,m[669]['y']-15,m[669]['scale']-.0005],675:[m[676]['x']-.4,m[676]['y']+20,m[676]['scale']+.003],680:[m[679]['x']+.333,m[679]['y']-11,m[679]['scale']-.0006],700:[m[701]['x']-.4,m[701]['y']+14,m[701]['scale']+.001],705:[m[704]['x']+.333,m[704]['y']-15,m[704]['scale']-.0006]};rows=[]
for n,(x0,y0,s0) in priors.items():
 source=np.array(Image.open(SRC/f'source-{n:04}.png').convert('RGB')).astype(float);x1=int(x0)-8;x2=int(x0+127*s0)+9;y1=max(0,int(y0)-10);y2=min(1080,int(y0+128*s0)+11);S=253-source[y1:y2,x1:x2];yy,xx=np.indices(S.shape[:2]);X=xx+x1+.5;Y=yy+y1+.5;best=None
 for dx in [-3,-2,-1,0,1,2,3]:
  for dy in [-6,-4,-2,0,2,4,6]:
   for ds in [-.005,0,.005]:
    x=x0+dx;y=y0+dy;s=s0+ds;coords=np.array([(Y-y)/s-.5+8,(X-x)/s-.5+8]);T=np.stack([map_coordinates(K[:,:,c],coords,order=1,mode='constant',cval=0) for c in range(3)],axis=-1);dot=float((S*T).sum());norm=float((T*T).sum());alpha=max(0,dot/norm);gain=alpha*alpha*norm
    if best is None or gain>best['squaredErrorGain']:best=dict(x=x,y=y,scale=s,alphaLS=alpha,ncc=float(dot/np.sqrt(norm*max(1e-20,(S*S).sum()))),squaredErrorGain=gain,blankMAE=float(abs(S).mean()),photoMAE=float(abs(S-alpha*T).mean()),l1Change=float(abs(S-alpha*T).mean()-abs(S).mean()),roi=[x1,y1,x2,y2])
 rows.append(dict(frame=n,bestPhotoProjection=best));print(n,best)
(R/'endpoint-matched-support.json').write_text(json.dumps(dict(frames=rows,method='Read-only bank±3x/±6y/±.005scale at camera-continuation poses. Original isolated artwork contrast projection, explicit source viewport crop. Positive tiny alpha is not sufficient: NCC and L1 change distinguish coherent visible photo support from block/noise residue. No scene mutations.'),indent=2))
