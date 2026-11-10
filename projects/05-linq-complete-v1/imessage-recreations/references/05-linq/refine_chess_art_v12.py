"""Settled app artwork, isolated queen and measured native camera/piece tracks."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,binary_closing,binary_fill_holes,gaussian_filter
from scipy.optimize import minimize_scalar,least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';A=D/'assets';s=json.loads((D/'scene-chess-tap-v12.json').read_text());g=next(q for q in s['layers'] if q['id']=='broad-v5-group-41');img,queen=g['children'][:2]
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
ref=load(891);base=ref[:,237:721].copy();# h4 and f4 are the same dark board material.
base[363:420,412:469]=ref[363:420,538:595];basePath=A/'v12-chess-settled-without-queen.png';Image.fromarray(np.uint8(base)).save(basePath);img['src']=str(basePath)
qa=ref[363:423,649:707].copy();m=(qa.max(2)-qa.min(2)<38)&(qa.min(2)>145);m=binary_fill_holes(binary_closing(m,iterations=1));qp=A/'v12-black-queen-static.png';Image.fromarray(np.dstack([np.uint8(qa),m.astype(np.uint8)*255])).save(qp);queen.update(src=str(qp),width=58,height=60);alpha=m.astype(np.float32);premult=qa*alpha[:,:,None]
# Grid-profile correlation is insensitive to scrim intensity and particle hue.
# It uses the actual settled app's pixels, not an ideal sharp rectangle edge.
template=np.gradient(base[145:595].mean(0),axis=0);cam=[]
for key in g['keyframes']['x']:
 f=round(key['t']*30);a=load(f);target=np.gradient(a[145:595].mean(0),axis=0);worldx=np.arange(max(0,round(key['value'])+20),min(960,round(key['value'])+464));tt=target[worldx]
 def cost(x):
  vals=np.stack([np.interp(worldx-x,np.arange(484),template[:,c],left=0,right=0) for c in range(3)],1);return 1-float(np.sum(vals*tt)/max(1,np.sqrt(np.sum(vals*vals)*np.sum(tt*tt))))
 fit=minimize_scalar(cost,bounds=(key['value']-6,key['value']+6),method='bounded',options={'xatol':.002});key['value']=float(fit.x);cam.append(dict(frame=f,x=float(fit.x),cost=float(fit.fun)))
by={q['frame']:q['x'] for q in cam};rows=[]
for f in range(875,892):
 a=load(f);xcam=by[f];worldY,worldX=np.mgrid[110:440:2,150:480:2];target=np.stack([map_coordinates(a[:,:,c],[worldY,worldX+xcam],order=1,mode='constant',cval=255) for c in range(3)],2);bg=base[110:440:2,150:480:2]
 frac=np.clip((f/30-29.2)/.3,0,1);x0=183+229*frac;y0=134+229*frac
 # A local optimizer cannot cross an empty-cell plateau. Search the actual
 # diagonal action path first, then refine the native pose/blur.
 qv=np.linspace(-.03,1.03,213);vv,uu=np.mgrid[0:60:2,0:58:2];good=alpha[::2,::2]>.2;uu=uu[good];vv=vv[good];al=alpha[::2,::2][good];qc=qa[::2,::2][good];cx=183+229*qv;cy=134+229*qv;sy=cy[:,None]+vv;scx=cx[:,None]+uu;tb=np.stack([map_coordinates(base[:,:,c],[sy,scx],order=1,mode='nearest') for c in range(3)],2);ta=np.stack([map_coordinates(a[:,:,c],[sy,scx+xcam],order=1,mode='nearest') for c in range(3)],2);model=(qc[None,:,:]-tb)*al[None,:,None];err=np.sum(model*model-2*model*(ta-tb),axis=(1,2));at=int(np.argmin(err));x0=float(cx[at]);y0=float(cy[at])
 def residual(v):
  x,y,blur=v;aa=gaussian_filter(alpha,blur,mode='constant',cval=0);rgb=gaussian_filter(premult,(blur,blur,0),mode='constant',cval=0);coords=[worldY-y,worldX-x];ac=map_coordinates(aa,coords,order=1,mode='constant',cval=0);pc=np.stack([map_coordinates(rgb[:,:,c],coords,order=1,mode='constant',cval=0) for c in range(3)],2);model=bg*(1-ac[:,:,None])+pc;return (model-target).ravel()/255
 fit=least_squares(residual,[x0,y0,.5],bounds=([150,100,0],[440,395,12]),max_nfev=75,diff_step=.003,ftol=.0002,xtol=.0002);x,y,b=map(float,fit.x);rows.append(dict(frame=f,x=x,y=y,blur=b,cost=float(np.mean(fit.fun**2))));print(f,fit.x,flush=True)
queen['keyframes']={k:[dict(t=860/30,value=rows[0][k])]+[dict(t=q['frame']/30,value=q[k],ease='linear') for q in rows] for k in ['x','y','blur']};queen['x']=queen['y']=0
(D/'chess-art-v12-measurements.json').write_text(json.dumps(dict(camera=cam,queen=rows,provenance=[dict(path=str(basePath),source_frame=891,box=[237,0,721,720],kind='single bounded settled chess app UI artwork; original queen removed with genuine empty matching dark-cell material; independent native queen/camera/scrim/badge/glow/confetti'),dict(path=str(qp),source_frame=891,box=[649,363,707,423],kind='single isolated genuine queen artwork with transparent exterior, native independently measured position/blur')]),indent=2));(D/'scene-chess-art-tap-v12.json').write_text(json.dumps(s,indent=2)+'\n');print('camera',[(q['frame'],round(q['x'],3)) for q in cam if q['frame'] in [891,909,933,936,939]])
