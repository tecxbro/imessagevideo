from pathlib import Path
from PIL import Image
import numpy as np
from scipy.optimize import nnls
import json
from functools import lru_cache

R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-boarding';BASE=R/'outputs/05-linq/final-v11'
scene=json.load(open(BASE/'scene.json'));root=next(l for l in scene['layers']if l['id']=='g-942');content=next(l for l in root['children']if l['id']=='root-boarding-native-content')
image=np.array(Image.open(P/'template-native/0.000.png').convert('RGB')).astype(float)/255
black=image[:,:960];white=image[:,960:];alpha=np.clip(1-(white-black).mean(axis=2),0,1);color=np.clip(black/np.maximum(alpha[:,:,None],1e-7),0,1);color[alpha<1e-5]=0
Image.fromarray(np.uint8(np.clip(np.dstack((color,alpha)),0,1)*255+.5)).save(P/'canonical-native-rgba.png')
lin=lambda a:np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
srgb=lambda a:np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)
encoded=color*alpha[:,:,None];linear=lin(color)*alpha[:,:,None]
ys=np.arange(0,720,3);xs=np.arange(0,960,4);YX,XX=np.meshgrid(ys,xs,indexing='ij');yy=YX.ravel();xx=XX.ravel()
def sample(keys,t):
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return keys[-1]['value']
@lru_cache(maxsize=2)
def frame_data(frame):
 Y=round(sample(root['keyframes']['y'],frame/30));X=round(sample(content['keyframes']['x'],frame/30));source=np.array(Image.open(P/'source'/f'{frame-1181:04d}.png').convert('RGB')).astype(float)/255;native=np.array(Image.open(R/'outputs/05-linq/frames-gsap'/f'{frame:06d}.png').convert('RGB')).astype(float)/255
 field=next(l for l in root['children']if l['id']==f'root-boarding-color-field-{frame}');texture=np.array(Image.open(BASE/field['src']).convert('RGBA')).astype(float)/255;z=np.arange(720)-Y-round(field['y']);valid=(z>=0)&(z<len(texture));B=native.copy();v=texture[np.clip(z,0,len(texture)-1)];a=v[:,:,3:]*valid[:,None,None];B=B*(1-a)+v[:,:,:3]*a
 return Y,X,source,native,B

def fit(frame,mode,delta_x):
 Y,X,source,native,B=frame_data(frame)
 # Infer physically observed exposure support from actual white glyph and
 # white-card edge extents. Background fit noise must not create distant UI ghosts.
 ranges=[]
 if Y-103>=25 and Y-78<695:
  y0=max(0,Y-128);y1=min(720,Y-53);fg=lin(source[y0:y1,45:330]);bg=lin(B[y0:y1,45:330]);D=1-bg;cov=((fg-bg)*D).sum(2)/np.maximum(1e-8,(D*D).sum(2));hits=np.where((cov>.08).any(1))[0]
  if len(hits):ranges.append((y0+int(hits.min())+103-2,y0+int(hits.max())+78+2))
 edge=Y+382
 if 40<edge<700:
  y0=max(0,edge-36);y1=min(720,edge+40);fg=np.median(lin(source[y0:y1,120:840]),axis=1);bg=np.median(lin(B[y0:y1,120:840]),axis=1);D=1-bg;cov=((fg-bg)*D).sum(1)/np.maximum(1e-8,(D*D).sum(1));on=np.where(cov>.05)[0];full=np.where(cov>.98)[0]
  if len(on)and len(full):ranges.append((y0+int(on.min())-382-2,y0+int(full.min())-382+2))
 background=B[yy,xx];backgroundModel=lin(background)if mode=='linear'else background;target=lin(source[yy,xx])if mode=='linear'else source[yy,xx];offsets=np.arange(-50,51,2)if frame<=1188 else np.arange(-24,25)if frame<=1194 else np.arange(-16,17);
 if ranges:
  lo=min(r[0]for r in ranges)-Y;hi=max(r[1]for r in ranges)-Y;offsets=offsets[(offsets>=lo)&(offsets<=hi)]
 columns=[];premul=linear if mode=='linear'else encoded
 for offset in offsets:
  iy=yy-(Y+offset)+200;ix=xx-(X+delta_x);valid=(iy>=0)&(iy<1400)&(ix>=0)&(ix<960)&(yy>=Y-154);iy=np.clip(iy,0,1399);ix=np.clip(ix,0,959);al=alpha[iy,ix]*valid;delta=(premul[iy,ix]-backgroundModel*al[:,None])*valid[:,None];columns.append(delta.astype('float32'))
 columns=np.stack(columns,axis=2);variable=(columns.max(axis=2)-columns.min(axis=2)).max(axis=1)>.025;A=columns[variable].reshape((-1,len(offsets))).astype(float);T=(target-backgroundModel)[variable].reshape(-1);regular=np.diff(np.eye(len(offsets)),axis=0)*.01;AA=np.vstack((A,np.ones((1,len(offsets)))*20,regular));TT=np.r_[T,20,np.zeros(len(offsets)-1)];weights,residual=nnls(AA,TT,maxiter=2000);weights/=weights.sum();keep=np.argsort(weights)[-41:];keep=sorted(keep[weights[keep]>1e-5]);w=weights[keep];w/=w.sum();prediction=backgroundModel+np.einsum('pcn,n->pc',columns[:,:,keep],w);prediction=srgb(prediction)if mode=='linear'else prediction;error=float(abs(prediction-source[yy,xx]).mean()*255);baseline=float(abs(native[yy,xx]-source[yy,xx]).mean()*255)
 return dict(frame=frame,mode=mode,baseY=Y,baseX=X,deltaX=delta_x,sampledMAE=error,sampledBaselineMAE=baseline,samples=[dict(offset=int(offsets[i]),weight=float(v))for i,v in zip(keep,w)],variablePixels=int(variable.sum()),supportRanges=ranges)

mode_trials=[]
for mode in ['encoded','linear']:
 for dx in range(-3,4):
  row=fit(1191,mode,dx);mode_trials.append(row);print('MODE',mode,dx,row['sampledMAE'],len(row['samples']),flush=True)
best=min(mode_trials,key=lambda r:r['sampledMAE']);chosen=best['mode'];results=[]
for frame in range(1185,1200):
 if frame==1191:row=best
 else:row=min((fit(frame,chosen,dx)for dx in range(-3,4)),key=lambda r:r['sampledMAE'])
 results.append(row);print('FIT',frame,row['mode'],row['deltaX'],row['sampledBaselineMAE'],row['sampledMAE'],len(row['samples']),flush=True)
(P/'exposure-fit-v2.json').write_text(json.dumps(dict(modeTrials=mode_trials,chosenMode=chosen,frames=results,note='Measured native exposure kernel from isolated SVG vector template; no source-frame runtime layer. Preserve1190/1195 controls unless explicitly accepted.'),indent=2))
