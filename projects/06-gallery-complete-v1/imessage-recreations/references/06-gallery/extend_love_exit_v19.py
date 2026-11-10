"""Retain the last clipped e until its actual source-native disappearance."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'native-late-v19';s=json.loads((D/'scene-soccer-v19.json').read_text());node=next(q for q in s['layers'] if q['id']=='v19-love-measured-letters');ref=np.array(Image.open(F/'000891.png').convert('RGB')).mean(2);K=(255-ref[526:697,938:1234])/255;yy0,xx0=np.where(ref[526:697,938:1234]<200);refRight=float(xx0.max()+1+938);poses=[];previousY=node['keyframes']['y'][-1]['value'];wy,wx=np.mgrid[440:715:2,0:260:2]
for f in range(947,971):
 source=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).mean(2);ys,xs=np.where(source[440:715,:260]<200)
 if len(xs)<5:break
 dx=float(xs.max()+1-refRight);target=(255-source[440:715:2,:260:2])/255
 def residual(v):
  x,y=v;model=map_coordinates(K,[wy-526-y,wx-938-x],order=1,mode='constant',cval=0);return (model-target).ravel()
 fit=least_squares(residual,[dx,previousY],bounds=([dx-2,previousY-3],[dx+2,previousY+3]),max_nfev=45,diff_step=.0001,ftol=.0001,xtol=.0001);dx,dy=map(float,fit.x);previousY=dy;poses.append(dict(frame=f,x=dx,y=dy,opacity=1.,mse=float(np.mean(fit.fun**2))))
for key in ['x','y','opacity']:node['keyframes'][key]+=[dict(t=p['frame']/30,value=p[key],ease='linear') for p in poses]
node['end']=(poses[-1]['frame']+1)/30;(D/'love-exit-extension-v19.json').write_text(json.dumps(poses,indent=2));(D/'scene-soccer-v19.json').write_text(json.dumps(s,indent=2)+'\n');patch=json.loads((D/'soccer-v19-patch.json').read_text());patch['append']=[node if q['id']==node['id'] else q for q in patch['append']];(D/'soccer-v19-patch.json').write_text(json.dumps(patch,indent=2));print('extended',poses)
