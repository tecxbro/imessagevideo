"""Compute a bounded material correction from native authored pixels only.
Reference pixels calibrate two color-model scalars; none enters the texture math.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;P=ROOT/'outputs/05-linq/final-v14/scene.json';s=json.loads(P.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((P.parent/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s);g=next(q for q in s['layers'] if q['id']=='broad-v5-group-20');f=259;t=f/30;K=lambda k:next(v['value'] for v in g['keyframes'][k] if abs(v['t']-t)<1e-8);beta=K('opacity');x=K('x');y=K('y');M=np.asarray(Image.open(ROOT/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB')).astype(float)/255;B=np.asarray(Image.open(ROOT/'verification/05-board-native-backdrop-v15/8.633.png').convert('RGB')).astype(float)/255;S=np.clip((M-(1-beta)*B)/beta,0,1);R=np.asarray(Image.open(D/f'measurements/native-transition/{f:06}.png').convert('RGB')).astype(float)/255;yy,xx=np.mgrid[0:720,0:960];mask=(xx>=x+24)&(xx<x+632)&(yy>=40)&(yy<440)&~((xx>385)&(xx<452)&(yy>265)&(yy<355));mask &= ((xx%2)==0)&((yy%2)==0)
# Power encoding is inferred as one physical color model, never a pixel lookup.
def prediction(a,gamma):return np.maximum(0,a*S**gamma+(1-a)*B**gamma)**(1/gamma)
def residual(v):return (prediction(*v)[mask]-R[mask]).ravel()
fit=least_squares(residual,[.67,2.2],bounds=([0,1.5],[1,3.5]),diff_step=.005,max_nfev=60);alpha,gamma=map(float,fit.x);desired=prediction(alpha,gamma)
# Minimal bounded RGBA correction over the still-editable native board.
delta=desired-M;need=np.where(delta>=0,delta/np.maximum(1-M,1e-9),-delta/np.maximum(M,1e-9));coverage=np.maximum(0,need.max(2));board=(xx>=x)&(xx<x+658)&(yy>=y)&(yy<y+720);coverage*=board;C=np.clip(M+delta/np.maximum(coverage[:,:,None],1e-9),0,1);rgba=np.dstack([C,np.minimum(1,coverage)]);box=[max(0,int(np.floor(x))),max(0,int(np.floor(y))),min(960,int(np.ceil(x+658))),min(720,int(np.ceil(y+720)))];x0,y0,x1,y1=box;out=D/'assets/derived-linear-board-material-259.png';Image.fromarray(np.uint8(np.round(rgba[y0:y1,x0:x1]*255))).save(out);node=dict(type='image',id='v15-board-linear-material-test-259',src=str(out),x=x0,y=y0,width=x1-x0,height=y1-y0,start=259/30,end=260/30);at=s['layers'].index(g)+1;s['layers'].insert(at,node);(D/'scene-linear-board-test-v15.json').write_text(json.dumps(s,indent=2)+'\n');report=dict(frame=f,oldGammaOpacity=beta,linearAlpha=alpha,powerGamma=gamma,oldGlobalMAE=float(np.abs(M-R).mean()*255),predictedGlobalMAE=float(np.abs(np.where(board[:,:,None],desired,M)-R).mean()*255),maxCorrectionOpacity=float(coverage.max()),bounds=box,derivation='M and B are independently authored native renders; S is recovered from known gamma-space native opacity. Reference pixels supply only global alpha/gamma scalars. Texture generation has no reference-pixel input.');(D/'linear-board-test-v15.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
