"""Check whether uniform diameter conceals a measurable affine portrait pose."""
import copy,json,math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize
import refine_portrait_cameras_helper_v18 as M
P=Path(__file__).parent;B=P/'portrait-helper-v18';data=json.load(open(B/'camera-fit.json'));frame=615;a=np.array(Image.open(M.F/f'{frame:06d}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS)).astype(np.float32);rows={id:next(r for r in rs if r['frame']==frame)for id,rs in data.items()};report=[]
for id in ['77','79']:
 r=rows[id];D=r['diameter'];initial=np.array([r['cx'],r['cy'],D,D,0.]);ts=M.templates[id];u,v=M.u,M.v
 def score(z,detail=False):
  cx,cy,W,H,deg=z;th=np.deg2rad(deg);xx=(cx+u*W*np.cos(th)-v*H*np.sin(th))/2;yy=(cy+u*W*np.sin(th)+v*H*np.cos(th))/2;valid=(xx>1)&(xx<959)&(yy>1)&(yy<539)
  for other,q in rows.items():
   if other!=id and q['diameter']>math.sqrt(W*H)*1.025:valid&=(xx-q['cx']/2)**2+(yy-q['cy']/2)**2>(q['diameter']*.5/2)**2
  obs=np.stack([map_coordinates(a[:,:,c],[yy[valid],xx[valid]],order=1)for c in range(3)],1);e=np.mean((ts[:,valid]-obs[None,:,:])**2,2);cost=np.mean(np.minimum(e,5000),axis=1);k=int(np.argmin(cost));mse=float(cost[k]);penalty=50*np.log(W/H)**2+.3*deg**2+10*(((cx-initial[0])/(D*.1))**2+((cy-initial[1])/(D*.1))**2)
  return (mse,float(M.blur_levels[k]))if detail else mse+penalty
 before=score(initial,True);bounds=[(initial[0]-D*.08,initial[0]+D*.08),(initial[1]-D*.08,initial[1]+D*.08),(D*.86,D*1.14),(D*.86,D*1.14),(-8,8)];fit=minimize(score,initial,method='Powell',bounds=bounds,options={'xtol':.03,'ftol':.0001,'maxiter':12});cx,cy,W,H,deg=fit.x;after,blur=score(fit.x,True);result={'id':id,'before':before,'after':after,'params':fit.x.tolist(),'blurFraction':blur};report.append(result);print(result,flush=True)
 for q in data[id]:
  if q['frame']==frame:q.update(cx=float(cx),cy=float(cy),width=float(W),height=float(H),diameter=float(math.sqrt(W*H)),rotation=float(deg),blurFraction=blur)
(B/'affine-diagnostic-cameras.json').write_text(json.dumps(data,indent=2)+'\n');(B/'affine-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
