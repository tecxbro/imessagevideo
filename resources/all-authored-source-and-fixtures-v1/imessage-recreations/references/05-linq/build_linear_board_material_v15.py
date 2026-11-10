"""Offline color shader over authored native components, never reference frames.
Reference RGB is used ONLY to estimate one physical opacity per frame and to
validate adoption. The texture is a mathematical function of native M/B pixels,
known native opacity, and one fixed effective transfer exponent.
"""
from pathlib import Path
import json,copy,hashlib
from PIL import Image
import numpy as np
from scipy.optimize import minimize_scalar
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;s=json.loads((D/'scene-restaurant-pawn-v15.json').read_text());g=next(q for q in s['layers'] if q['id']=='broad-v5-group-20');gamma=1.870844377621079;rows=[];nodes=[];artdir=D/'assets/derived-board-material-v15';artdir.mkdir(exist_ok=True);yy,xx=np.mgrid[0:720,0:960]
K=lambda key,f:next(v['value'] for v in g['keyframes'][key] if abs(v['t']-f/30)<1e-8)
for f in range(209,266):
 beta=K('opacity',f);x=K('x',f);y=K('y',f);name=f'{f/30:.3f}.png';mp=ROOT/'verification/05-board-native-pawn-v15'/name;bp=ROOT/'verification/05-board-native-backdrop-v15'/name;M=np.asarray(Image.open(mp).convert('RGB')).astype(np.float32)/255;B=np.asarray(Image.open(bp).convert('RGB')).astype(np.float32)/255;R=np.asarray(Image.open(D/'measurements/native-transition'/f'{f:06}.png').convert('RGB')).astype(np.float32)/255;row=dict(frame=f,oldGammaOpacity=float(beta),oldMAE=float(np.abs(M-R).mean()*255),adopted=False)
 if beta<=.001 or beta>.995:
  row['reason']='Invisible or opaque native material requires no blend correction';rows.append(row);continue
 S=np.clip((M-(1-beta)*B)/beta,0,1);mask=(xx>=x+24)&(xx<x+632)&(yy>=max(0,y+40))&(yy<min(720,y+440))&~((xx>x+330)&(xx<x+405)&(yy>y+120)&(yy<y+365));mask &= ((xx%4)==0)&((yy%4)==0);sl=S[mask]**gamma;bl=B[mask]**gamma;rl=R[mask]
 def cost(alpha):return float(np.mean((np.maximum(0,alpha*sl+(1-alpha)*bl)**(1/gamma)-rl)**2))
 fit=minimize_scalar(cost,bounds=(0,1),method='bounded',options={'xatol':1e-6});a=float(fit.x);desired=np.maximum(0,a*S**gamma+(1-a)*B**gamma)**(1/gamma);board=(xx>=x)&(xx<x+658)&(yy>=y)&(yy<y+720);pred=np.where(board[:,:,None],desired,M);new=float(np.abs(pred-R).mean()*255);row.update(physicalOpacity=a,modelMAE=new,effectiveExponent=gamma)
 if new>=row['oldMAE']-.005:
  row['reason']='Measured scalar model did not improve this frame';rows.append(row);continue
 # Everything below depends only on authored pixels and measured scalar a.
 delta=desired-M;need=np.where(delta>=0,delta/np.maximum(1-M,1e-7),-delta/np.maximum(M,1e-7));coverage=np.maximum(0,need.max(2))*board;C=np.clip(M+delta/np.maximum(coverage[:,:,None],1e-7),0,1);rgba=np.dstack([C,np.minimum(1,coverage)]);box=[max(0,int(np.floor(x))),max(0,int(np.floor(y))),min(960,int(np.ceil(x+658))),min(720,int(np.ceil(y+720)))];x0,y0,x1,y1=box;out=artdir/f'computed-material-{f:06}.png';Image.fromarray(np.uint8(np.round(rgba[y0:y1,x0:x1]*255))).save(out);nodes.append(dict(type='image',id=f'v15-linear-material-{f}',src=str(out),x=x0-x,y=y0-y,width=x1-x0,height=y1-y0,start=f/30,end=(f+1)/30,materialOnly=True,derivedFrom='Authored native board/question render and scalar color model; no reference pixels.'));row.update(adopted=True,texture=str(out),nativeRenderSHA256=hashlib.sha256(mp.read_bytes()).hexdigest(),nativeBackdropSHA256=hashlib.sha256(bp.read_bytes()).hexdigest(),maxCorrectionOpacity=float(coverage.max()));rows.append(row);print(row,flush=True)
# One shared native camera moves app artwork, editable pawn components, and its
# dependent material together. The correction does not replace those components.
wrapper=dict(type='group',id='v15-first-board-material-camera',start=g['start'],end=g['end'],keyframes={k:copy.deepcopy(g['keyframes'][k]) for k in ['x','y']},children=[g]+nodes);g['x']=0;g['y']=0;g['keyframes'].pop('x');g['keyframes'].pop('y');s['layers'][s['layers'].index(g)]=wrapper
(D/'board-material-v15-measurements.json').write_text(json.dumps(dict(effectiveExponent=gamma,physicalMeaning='Approximate measured transfer model; the original working color space is not asserted.',calibration='Source pixels calibrate only scalar opacity and validate error. Texture output is computed from authored M/B native pixels.',editability='Outer app/pawn cameras and geometry remain native. Regenerate dependent material after changing its internal content or backdrop.',frames=rows),indent=2)+'\n');(D/'scene-final-v15-prototype.json').write_text(json.dumps(s,indent=2)+'\n');print('computed materials',len(nodes),'of57frames')
