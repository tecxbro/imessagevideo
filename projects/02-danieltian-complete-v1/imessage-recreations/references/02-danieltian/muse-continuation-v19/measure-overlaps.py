from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/muse-continuation-v19';SRC=R.parent/'assets/middle-every-frame';poses={r['frame']:r for r in json.load(open(R/'existing-poses.json'))};audit={r['frame']:r['avatars'] for r in json.load(open(R/'audit-660-710.json'))['frames']};asset=ROOT/'outputs/02-danieltian/final-v18/assets/c5968c7a63d20083211360f8af2a8a2ea732595908c62ab0a129f917f4ecbcaf.png';a=np.array(Image.open(asset).convert('RGBA')).astype(float);K=(253-a[:,:,:3])*a[:,:,3:]/255;H,W=K.shape[:2];PAD=8;K=np.pad(K,((PAD,PAD),(PAD,PAD),(0,0)),mode='constant')
def fitphoto(n,x0,y0,s0=1,alpha0=.5,scaleBounds=(.9,1.06)):
 source=np.array(Image.open(SRC/f'source-{n:04}.png').convert('RGB')).astype(float);x1=max(0,int(x0)-15);x2=min(1920,int(x0+W*s0)+16);y1=max(0,int(y0)-18);y2=min(1080,int(y0+H*s0)+19);S=253-source[y1:y2,x1:x2];yy,xx=np.indices(S.shape[:2]);X=xx+x1+.5;Y=yy+y1+.5
 def sprite(q):
  x,y,s,alpha=q;coords=np.array([(Y-y)/s-.5+PAD,(X-x)/s-.5+PAD]);return np.stack([map_coordinates(K[:,:,c],coords,order=1,mode='constant',cval=0) for c in range(3)],axis=-1)
 def residual(q):return (q[3]*sprite(q)-S).ravel()
 res=least_squares(residual,[x0,y0,s0,alpha0],bounds=([x0-6,y0-15,scaleBounds[0],0],[x0+6,y0+15,scaleBounds[1],1.05]),loss='soft_l1',f_scale=.8,diff_step=1e-5,max_nfev=250,xtol=1e-9,ftol=1e-9);q=res.x;T=sprite(q);M=q[3]*T;ncc=float((T*S).sum()/np.sqrt((T*T).sum()*(S*S).sum()));cov=np.linalg.pinv(res.jac.T@res.jac)*np.mean(res.fun**2);return dict(x=float(q[0]),y=float(q[1]),scale=float(q[2]),width=float(W*q[2]),height=float(H*q[2]),alpha=float(q[3]),parameterStd=np.sqrt(np.diag(cov)).tolist(),ncc=ncc,rmse=float(np.sqrt(np.mean((M-S)**2))),roi=[x1,y1,x2,y2],bottomCensored=y0+H*s0>1080,observedPixelHeight=y2-max(y1,int(q[1])),fullSpriteSizeIsModel=True,optimizer=dict(success=bool(res.success),evaluations=int(res.nfev)))
# The uncensored same-actor frame705 calibrates the known original artwork's full scale.
cal=fitphoto(705,280,924,1,.99);print('uncensored705',cal);rows=[]
for n in [666,667,668,669,676,677,678,679,701,702,703,704]:
 p=poses[n];source=np.array(Image.open(SRC/f'source-{n:04}.png').convert('RGB')).astype(float);base=np.array(Image.open(O/f'baseline-native18/{n:06}.png').convert('RGB')).astype(float);x1=max(0,int(np.floor(p['x']))-2);y1=max(0,int(np.floor(p['y']))-2);x2=min(1920,int(np.ceil(p['x']+126*p['scaleX']))+2);y2=min(1080,int(np.ceil(p['y']+126*p['scaleY']))+2);T=253-base[y1:y2,x1:x2];S=253-source[y1:y2,x1:x2];alpha=float(np.sum(T*S)/np.sum(T*T));selected=dict(alpha=alpha,x=p['x'],y=p['y'],scaleX=p['scaleX'],scaleY=p['scaleY'],roi=[x1,y1,x2,y2],ncc=float(np.sum(T*S)/np.sqrt(np.sum(T*T)*np.sum(S*S))),beforeMAE=float(abs(T-S).mean()),afterMAE=float(abs(alpha*T-S).mean()),method='Linear contrast alpha fit against actualV18 native selected-avatar pixels at the exact unchanged camera. No geometry or stage rectangle modification.')
 options=audit[n];others=[v for v in options if abs(v['y']-p['y'])>100]
 if n==701:init=dict(x=279,y=984,alpha=.1);bounds=(cal['scale']-.025,cal['scale']+.025);s0=cal['scale']
 else:
  assert len(others)==1,(n,p,options);init=others[0];bounds=(.9,1.06);s0=1
 clone=fitphoto(n,init['x'],init['y'],s0,init['alpha'],bounds);rows.append(dict(frame=n,selected=selected,clone=clone));print(n,'selectedα',round(alpha,5),'NCC',round(selected['ncc'],4),'clone',clone)
(R/'overlap-measurements.json').write_text(json.dumps(dict(baseSceneSHA256='14657bfc3d9f77a86a92e84367a4b557e925530380a3d6893cbfaeb4420217e2',originalArt=str(asset),uncensored705Calibration=cal,frames=rows,notice='All selected-avatar x/y/scale/asset/lifecycle preserved. Independent complementary clone poses/alphas fit original isolated artwork. Incoming701 bottom-censored: full size follows same-source uncensored705 scale and original artwork aspect; stage truncates visibility, not sprite height. No source frame, message UI or new artwork texture is used.'),indent=2))
