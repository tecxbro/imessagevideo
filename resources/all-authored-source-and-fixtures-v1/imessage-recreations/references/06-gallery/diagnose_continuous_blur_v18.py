"""Measure continuous photo blur; coarse65px blur steps grow large on near faces."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize_scalar
import refine_portrait_cameras_helper_v18 as M
P=Path(__file__).parent;B=P/'portrait-helper-v18';data=json.load(open(B/'camera-fit.json'));frame=615;a=np.array(Image.open(M.F/f'{frame:06d}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS)).astype(np.float32);rows={id:next(r for r in rs if r['frame']==frame)for id,rs in data.items()};report=[]
for id in ['77','79','new-blond-male','87','95']:
 r=rows[id];D=r['diameter'];xx=(r['cx']+M.u*D)/2;yy=(r['cy']+M.v*D)/2;valid=(xx>1)&(xx<959)&(yy>1)&(yy<539)
 for other,q in rows.items():
  if other!=id and q['diameter']>D*1.025:valid&=(xx-q['cx']/2)**2+(yy-q['cy']/2)**2>(q['diameter']*.5/2)**2
 obs=np.stack([map_coordinates(a[:,:,c],[yy[valid],xx[valid]],order=1)for c in range(3)],1);oc=255-obs;v=M.v[valid];u=M.u[valid];photo=M.template_photos[id]
 def cost(local,detail=False):
  im=np.array(photo.filter(ImageFilter.GaussianBlur(float(local)))).astype(np.float32);tpl=np.stack([map_coordinates(im[:,:,c],[(v+.5)*65+17.5,(u+.5)*65+17.5],order=1,mode='nearest')for c in range(3)],1);tc=255-tpl;alpha=float(np.clip(np.sum(tc*oc)/max(1,np.sum(tc*tc)),0,1));mse=float(np.mean(np.minimum(np.mean((oc-alpha*tc)**2,1),5000)));return(mse,alpha)if detail else mse
 best=minimize_scalar(cost,bounds=(0,15),method='bounded',options={'xatol':.015});mse,alpha=cost(best.x,True);report.append({'id':id,'old_mse':r['mse'],'new_mse':mse,'old_world_blur':r['blurFraction']*D,'new_world_blur':best.x/65*D,'alpha':alpha,'blurFraction':float(best.x/65)});print(report[-1],flush=True)
 for q in data[id]:
  if q['frame']==frame:q['blurFraction']=float(best.x/65);q['opacity']=alpha
(B/'continuous-blur-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');(B/'continuous-blur-diagnostic-cameras.json').write_text(json.dumps(data,indent=2)+'\n')
