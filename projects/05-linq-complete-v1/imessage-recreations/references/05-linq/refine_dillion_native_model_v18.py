"""Calibrate the same native word poses against the actual rendered path."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;R=D.parent.parent;s=json.loads((D/'scene-foodash-name-native-v18.json').read_text());g=next(q for q in s['layers']if q['id']=='rich-group-12');name=next(q for q in g['children']if q['id']=='v18-dillion-independent-name');hr=(246/249)*(255-np.array(Image.open(R/'verification/05-foodash-name-vector-template-v18/0.000.png').convert('RGB')).astype(float).mean(2));spec=json.loads((D/'dillion-name-v18-measurements.json').read_text());rows=[];offset=np.array([(i+.5)/4 for i in range(4)])
def val(k,f):return next(z['value']for z in g['keyframes'][k]if abs(z['t']*30-f)<1e-5)
for r in spec['rows']:
 f=r['frame'];a=np.array(Image.open(D/'measurements/native-transition'/f'{f:06d}.png').convert('RGB')).astype(float).mean(2);bb=r['sourceBlackBBox'];xx,yy=np.meshgrid(np.arange(max(0,bb[0]-5),min(960,bb[2]+5)),np.arange(max(0,bb[1]-5),min(720,bb[3]+5)));target=a[yy,xx];xx=xx.ravel();yy=yy.ravel();ox=np.tile(offset,4);oy=np.repeat(offset,4)
 def residual(v):
  x,y,sx,sy=v;u=((xx[None,:]+ox[:,None]-x)/sx)*4-.5;w=((yy[None,:]+oy[:,None]-y)/sy)*4-.5;pred=252-map_coordinates(hr,[w,u],order=1,mode='constant',cval=0,prefilter=False).mean(0)
  return(pred-target.ravel())/30
 initial=np.array(r['globalPose']);fit=least_squares(residual,initial,bounds=(initial+[-2,-2,-.05,-.05],initial+[2,2,.05,.05]),max_nfev=70,diff_step=[.0001,.0001,.0001,.0001]);x,y,sx,sy=fit.x;px,py,psx,psy=[val(k,f)for k in ['x','y','scaleX','scaleY']];z=dict(r);z.update(x=round(float((x-px)/psx),6),y=round(float((y-py)/psy),6),scaleX=round(float(sx/psx),6),scaleY=round(float(sy/psy),6),globalPose=list(map(float,fit.x)),nativeModelRMSE=float(np.sqrt(np.mean(residual(fit.x)**2))));rows.append(z)
for k in ['x','y','scaleX','scaleY']:name['keyframes'][k]=[{'t':r['frame']/30,'value':r[k],'ease':'linear'}for r in rows]
next(z for z in g['children']if z['id']=='v18-dillion-paper-mask')['fill']='#fcfcfc'
for z in g['children']:
 if z['id']in['v18-dillion-paper-mask','v18-dillion-independent-name']:z['end']=1035/30
spec.update(rows=rows,nativeModel='Actual browser-rendered outlined glyph at4x, integrated4x4coverage per native pixel; same immutable native path and solid fill, no opacity change.')
(D/'scene-foodash-name-native-v18b.json').write_text(json.dumps(s,indent=2)+'\n');(D/'dillion-name-v18-measurements-native.json').write_text(json.dumps(spec,indent=2)+'\n');print([(r['frame'],round(r['nativeModelRMSE'],4))for r in rows[::5]])
