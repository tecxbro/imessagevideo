from pathlib import Path
import json,importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,binary_fill_holes
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';s=json.loads((D/'scene-chess-v12.json').read_text());g=next(q for q in s['layers'] if q['id']=='g-366')['children'][1];art=np.array(Image.open(g['children'][0]['src']).convert('RGBA')).astype(np.float32);rgb=art[:,:,:3];alpha=art[:,:,3]/255;tintMask=binary_fill_holes(rgb.min(2)<243).astype(np.float32);poses=[];wy,wx=np.mgrid[205:715:2,80:650:2];oldY={round(q['t']*30):q['value'] for q in g['keyframes']['y']}
for f in range(340,352):
 a=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32);target=a[205:715:2,80:650:2]
 def residual(v):
  sc,x,y,dark=v;coords=[(wy-y)/sc,(wx-x)/sc];aa=map_coordinates(alpha,coords,order=1,mode='constant',cval=0);ar=np.stack([map_coordinates(rgb[:,:,c],coords,order=1,mode='constant',cval=255) for c in range(3)],2);tint=map_coordinates(tintMask,coords,order=1,mode='constant',cval=0);pred=255*(1-aa[:,:,None])+ar*(1-dark*tint[:,:,None])*aa[:,:,None];return (pred-target).ravel()/255
 y=oldY[f];fit=least_squares(residual,[1,91,y,.05],bounds=([.91,83,y-20,0],[1.02,114,y+20,.35]),max_nfev=80,diff_step=.002,ftol=.0001,xtol=.0001);sc,x,y,dark=map(float,fit.x);poses.append(dict(frame=f,scale=sc,x=x,y=y,dark=dark,cost=float(np.mean(fit.fun**2))));print(f,fit.x,flush=True)
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);path,stats=trace.trace_alpha(tintMask,0,0)
old=g['keyframes'];g['keyframes'].update(x=[dict(t=339/30,value=91)]+[dict(t=p['frame']/30,value=p['x']) for p in poses],scaleX=[dict(t=339/30,value=1)]+[dict(t=p['frame']/30,value=p['scale']) for p in poses],scaleY=[dict(t=339/30,value=1)]+[dict(t=p['frame']/30,value=p['scale']) for p in poses],y=[q for q in old['y'] if q['t']<340/30]+[dict(t=p['frame']/30,value=p['y']) for p in poses]);g['children'].append(dict(type='path',id='v12-flight-native-tap-darken',d=path,fill='#000000',keyframes={'opacity':[dict(t=339/30,value=0)]+[dict(t=p['frame']/30,value=p['dark']) for p in poses]}))
(D/'flight-tap-v12-poses.json').write_text(json.dumps(poses,indent=2));(D/'scene-chess-tap-v12.json').write_text(json.dumps(s,indent=2)+'\n')
