"""Fit the notification's native affine camera/blur from its unique green badge."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import minimize
D=Path(__file__).resolve().parent;F=D/'native-transition-v18'
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float)
def field(a):
 g=np.maximum(a[:,:,1]-a[:,:,0]-5,0);g[(a[:,:,1]-a[:,:,2])<5]=0;g[:,:350]=0;g[:,750:]=0;g[430:]=0;return g
ref=load(663);rr=field(ref);yy,xx=np.indices(rr.shape);rx=float((xx*rr).sum()/rr.sum());ry=float((yy*rr).sum()/rr.sum());patch=rr[94:394,388:688];sigmas=[0,.5,1,2,3,5,8,12,20,30];tpl=np.stack([gaussian_filter(patch,z) for z in sigmas]);results=[]
for f in range(653,689):
 a=load(f);z=field(a);energy=z.sum()
 if energy<20:continue
 cx=float((xx*z).sum()/energy);cy=float((yy*z).sum()/energy);x0=max(350,int(cx-120));x1=min(750,int(cx+120));y0=max(0,int(cy-120));y1=min(430,int(cy+120));wy,wx=np.mgrid[y0:y1:2,x0:x1:2];obs=z[::2,::2] if False else z[wy,wx];denobs=max(1,np.sum(obs*obs))
 def cost(v,detail=False):
  sx,sy=v;coords=[(wy-cy)/sy+ry-94,(wx-cx)/sx+rx-388];models=np.stack([map_coordinates(t,coords,order=1,mode='constant',cval=0) for t in tpl]);den=np.maximum(1,np.sum(models*models,axis=(1,2)));alpha=np.clip(np.sum(models*obs,axis=(1,2))/den,0,1.2);err=np.sum((models*alpha[:,None,None]-obs)**2,axis=(1,2))/denobs;at=int(np.argmin(err))
  return (float(err[at]),float(alpha[at]),sigmas[at]) if detail else float(err[at])
 fit=minimize(cost,[1,1],method='Powell',bounds=[(.2,1.5),(.2,1.5)],options={'xtol':.002,'ftol':.0001,'maxiter':10});err,alpha,blur=cost(fit.x,True);sx,sy=map(float,fit.x);tx=cx-rx*sx;ty=cy-ry*sy;box=[356*sx+tx,62*sy+ty,1564*sx+tx,322*sy+ty];results.append({'frame':f,'sx':sx,'sy':sy,'x':tx,'y':ty,'opacity':min(1,alpha),'blur':blur,'bbox':box,'greenCenter':[cx,cy],'mse':err})
(D/'notification-v18-world-bounds.json').write_text(json.dumps(results,indent=2));print([r for r in results if r['frame'] in [654,655,657,660,663,681,684,686,688]])
