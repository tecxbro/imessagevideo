"""Fit chess static-file alignment; exclude both native moving-pawn columns."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize
D=Path(__file__).resolve().parent;P=D/'measurements/object-poses-v10';F=D/'measurements/native-transition'
ref=np.array(Image.open(F/'000246.png').convert('RGB')).astype(float)[:,152:810]
old=json.loads((P/'first-board.json').read_text());features={x['frame']:x for x in json.loads((D/'measurements/transition-features.json').read_text())};cb=features[246]['board_top_bounds'];cc=(cb[0]+cb[2])/2
blue={x['frame']:x for x in json.loads((P/'flight-question.json').read_text())['poses']}
v,u=np.mgrid[30:500:4,20:638:4];mask=~((u>316)&(u<490));u=u[mask].ravel();v=v[mask].ravel();out=[]
for row in old:
 f=row['frame'];a=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float);bb=features[f].get('board_top_bounds');x0=152. if f<254 else (152+(bb[0]+bb[2])/2-cc if bb[0]>0 else bb[2]-(cb[2]-152));y0=row['y']
 m=(u+x0>7)&(u+x0<953)&(v+y0<713)
 if f in blue and blue[f]['y'] is not None:m&=~((u+x0>322)&(v+y0>blue[f]['y']))
 uu,vv=u[m],v[m];t=255-ref[vv,uu];den=np.sum(t*t)
 def objective(z,detail=False):
  x,y=z;p=255-np.stack([map_coordinates(a[:,:,c],[vv+y,uu+x],order=1,mode='constant',cval=255) for c in range(3)],1);alpha=np.sum(t*p)/den;err=np.mean((p-alpha*t)**2)
  return (err,alpha) if detail else err
 fit=minimize(objective,[x0,y0],method='Powell',bounds=[(x0-5,x0+5),(y0-4,y0+4)],options={'xtol':.03,'ftol':.0001,'maxiter':15})
 err,alpha=objective(fit.x,True);out.append({'frame':f,'x':float(fit.x[0]),'y':float(fit.x[1]),'alpha':float(np.clip(alpha,0,1)),'mse':float(err)})
(P/'first-board-affine.json').write_text(json.dumps(out,indent=2));print([x for x in out if x['frame'] in [209,210,219,246,258,260,265]])
