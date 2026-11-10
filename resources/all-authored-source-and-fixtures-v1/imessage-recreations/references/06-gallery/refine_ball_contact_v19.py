"""Resolve two contact frames using interior sphere texture registration."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening,binary_closing,map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'native-late-v19';s=json.loads((D/'scene-soccer-v19.json').read_text());node=next(q for q in s['layers'] if q['id']=='v19-soccer-measured-ball');p=json.loads((D/'soccer-v19-measurements.json').read_text());by={r['frame']:r for r in p['ball']};art=np.array(Image.open(node['children'][0]['src']).convert('RGBA')).astype(np.float32);alpha=art[:,:,3]/255;premult=art[:,:,:3]*alpha[:,:,None];v,u=np.mgrid[7:150:3,7:150:3];valid=(u-77.5)**2+(v-77.5)**2<70**2;u=u[valid];v=v[valid];records=[]
for f in [925,926]:
 a=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32);gray=a.mean(2);yy,xx=np.indices(gray.shape);mask=(gray>65)&(gray<245)&(a.max(2)-a.min(2)<70)&(xx>180)&(xx<650)&(yy>300)&(yy<680);mask=binary_closing(binary_opening(mask,iterations=2),iterations=3);ys,xs=np.where(mask);cx=(xs.min()+xs.max())/2;cy=(ys.min()+ys.max())/2;scale=(by[924]['scale']+by[927]['scale'])/2;x0=cx-78*scale;y0=cy-78*scale
 def residual(values):
  x,y,theta=values;angle=np.deg2rad(theta);sx=np.cos(angle)*(u-77.5)+np.sin(angle)*(v-77.5)+77.5;sy=-np.sin(angle)*(u-77.5)+np.cos(angle)*(v-77.5)+77.5;aa=map_coordinates(alpha,[sy,sx],order=1,mode='constant',cval=0);rgb=np.stack([map_coordinates(premult[:,:,c],[sy,sx],order=1,mode='constant',cval=0) for c in range(3)],1);model=rgb+255*(1-aa[:,None]);target=np.stack([map_coordinates(a[:,:,c],[y+v*scale,x+u*scale],order=1,mode='constant',cval=255) for c in range(3)],1);return ((model-target)/255).ravel()
 angles=np.arange(0,360,10);cost=[np.mean(residual([x0,y0,t])**2) for t in angles];theta=float(angles[int(np.argmin(cost))]);fit=least_squares(residual,[x0,y0,theta],bounds=([x0-18,y0-18,theta-15],[x0+18,y0+18,theta+15]),max_nfev=100,diff_step=.0005,ftol=.00005,xtol=.00005);x,y,theta=map(float,fit.x);theta+=360*round((by[f-1]['rotation']-theta)/360);by[f].update(x=x,y=y,scale=scale,rotation=theta,observed=True,renderX=x+78*(scale-1),renderY=y+78*(scale-1));records.append(dict(frame=f,x=x,y=y,rotation=theta,scale=scale,mse=float(np.mean(fit.fun**2))))
for key,col in [('x','renderX'),('y','renderY'),('scaleX','scale'),('scaleY','scale'),('rotation','rotation')]:node['keyframes'][key]=[dict(t=r['frame']/30,value=r[col],ease='linear') for r in p['ball']]
(D/'ball-contact-v19-measurements.json').write_text(json.dumps(records,indent=2));(D/'soccer-v19-measurements.json').write_text(json.dumps(p,indent=2));(D/'scene-soccer-v19.json').write_text(json.dumps(s,indent=2)+'\n');patch=json.loads((D/'soccer-v19-patch.json').read_text());patch['append']=[node if q['id']==node['id'] else q for q in patch['append']];(D/'soccer-v19-patch.json').write_text(json.dumps(patch,indent=2));print(records)
