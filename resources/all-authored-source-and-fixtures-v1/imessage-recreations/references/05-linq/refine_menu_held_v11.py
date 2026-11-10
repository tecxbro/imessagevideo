from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';s=json.loads((D/'scene-menu-middle-v11.json').read_text());poses=json.loads((D/'menu-v11-optics-poses.json').read_text());by={p['frame']:p for p in poses};g=next(q for q in s['layers'] if q['id']=='g-119');viewport=g['children'][1];doc=viewport['children'][0]
for wrapper in doc['children']:
 row=wrapper['children'][0]['children'][0]['children'][0];base={k:row.get(k,1 if k.startswith('scale') else 0) for k in ['x','y','scaleX','scaleY']};ar=np.array(Image.open(row['src']).convert('RGB')).astype(np.float32);hh,ww=ar.shape[:2];tracks={k:[dict(t=117/30,value=base.get(k,1))] for k in ['x','y','scaleX','scaleY']};tracks['opacity']=[dict(t=117/30,value=1)]
 wrapper.setdefault('keyframes',{})['blur']=[dict(t=117/30,value=1,ease='hold'),dict(t=118/30,value=0,ease='hold')]
 for f in range(118,127):
  p=by[f];source=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32);sx0=p['scale']*row['width']/ww;sy0=p['scale']*row['height']/hh;x0=p['x']+p['scale']*row['x'];y0=p['docY']+p['scale']*row['y'];cardtop=p['cardY']+38*p['cardScaleY'];cardbottom=p['cardY']+650*p['cardScaleY'];lo=max(0,round(y0)-10,round(cardtop)+3);hi=min(720,round(y0+hh*sy0)+10,round(cardbottom)-1);lx=max(0,round(x0)-8);rx=min(960,round(x0+ww*sx0)+9)
  if hi<=lo:continue
  yy,xx=np.mgrid[lo:hi:2,lx:rx:2];target=source[lo:hi:2,lx:rx:2]
  def residual(v):
   sx,sy,x,y,alpha=v;coords=[(yy-y)/sy,(xx-x)/sx];pred=np.stack([map_coordinates(ar[:,:,c],coords,order=1,mode='constant',cval=255) for c in range(3)],2);return ((255-alpha*(255-pred))-target).ravel()/255
  a0=p['opacity'];fit=least_squares(residual,[sx0,sy0,x0,y0,a0],bounds=([sx0*.97,sy0*.94,x0-9,y0-9,.02],[sx0*1.03,sy0*1.06,x0+9,y0+9,1.08]),max_nfev=45,diff_step=.003,ftol=.0003,xtol=.0003);sx,sy,x,y,alpha=map(float,fit.x)
  for k,v in [('x',(x-p['x'])/p['scale']),('y',(y-p['docY'])/p['scale']),('scaleX',ww*sx/(p['scale']*row['width'])),('scaleY',hh*sy/(p['scale']*row['height'])),('opacity',min(1.1,alpha/max(.001,p['opacity'])))]:tracks[k].append(dict(t=f/30,value=v,ease='linear'))
 row['keyframes']=tracks
(D/'scene-menu-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n');print('held row fits complete')
