"""Measure only the static photo carousel's native subpixel registration."""
from pathlib import Path
import json,copy
from PIL import Image
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;INPUT=ROOT/'outputs/05-linq/final-v14/scene.json';s=json.loads(INPUT.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((INPUT.parent/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s);g=next(q for q in s['layers'] if q['id']=='rich-group-14');viewport=next(q for q in g['children'] if q['id']=='v10-restaurant-photo-viewport');rail=viewport['children'][0];history=[]
def value(q,k,t,default=0):
 ks=q.get('keyframes',{}).get(k)
 if not ks:return q.get(k,default)
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if a['t']<=t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
for f in range(1060,1150):
 t=f/30;dy=value(g,'y',t);op=value(g,'opacity',t,1);top=max(0,int(310+dy));bottom=min(720,int(630+dy));row=dict(frame=f,dx=0.,dy=0.,oldX=value(rail,'x',t))
 if op>.8 and bottom-top>50:
  a=np.asarray(Image.open(D/'measurements/native-transition'/f'{f:06}.png').convert('RGB')).astype(np.float32)/255;b=np.asarray(Image.open(ROOT/'outputs/05-linq/frames-gsap'/f'{f:06}.png').convert('RGB')).astype(np.float32)/255;yy,xx=np.mgrid[top:bottom:4,204:765:4];target=a[top:bottom:4,204:765:4]
  def residual(v):
   dx0,dy0=v;p=np.stack([map_coordinates(b[:,:,c],[yy-dy0,xx-dx0],order=1,mode='nearest') for c in range(3)],2);return (p-target).ravel()
  best=min((float(np.mean(residual([x,0])**2)),x) for x in range(-10,11));fit=least_squares(residual,[best[1],0.],bounds=([-12,-2],[12,2]),diff_step=.015,max_nfev=35,ftol=.0004,xtol=.0004);row.update(dx=float(fit.x[0]),dy=float(fit.x[1]),oldRoiMAE=float(np.abs(residual([0,0])).mean()*255),newRoiMAE=float(np.abs(residual(fit.x)).mean()*255))
 history.append(row);print(row,flush=True)
rail['keyframes']['x']=[dict(t=r['frame']/30,value=r['oldX']+r['dx'],ease='linear') for r in history]
for q in rail['children']:q.setdefault('keyframes',{})['y']=[dict(t=r['frame']/30,value=q.get('y',0)+r['dy'],ease='linear') for r in history]
viewport['clip']['x']=195;viewport['clip']['width']=578
(D/'restaurant-camera-v15-measurements.json').write_text(json.dumps(history,indent=2)+'\n');(D/'restaurant-camera-v15-patch.json').write_text(json.dumps(dict(replace={'rich-group-14':g}),indent=2)+'\n');(D/'scene-restaurant-v15.json').write_text(json.dumps(s,indent=2)+'\n')
