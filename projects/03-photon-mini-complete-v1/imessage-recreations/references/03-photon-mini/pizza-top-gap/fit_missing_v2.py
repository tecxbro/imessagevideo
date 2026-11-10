"""Measure the missing top-clipped original pizza only; all other actors stay intact."""
from pathlib import Path
import sys,json,math,time
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from scipy import ndimage
from scipy.optimize import differential_evolution,minimize
R=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent;cv2.setNumThreads(1);asset=cv2.imread(str(R/'assets/apple-pizza.png'),-1).astype(float);H,W=asset.shape[:2];assert(W,H)==(106,117);alpha=asset[:,:,3:]/255;premult=np.concatenate([asset[:,:,:3]*alpha,alpha],2);spec=json.loads((R/'food-orbit-final.json').read_text());n=spec['replacements']['authentic-food-pizza-header'];inner=n['children'][0]
def value(layer,k,f):return next(q['value']for q in layer['keyframes'][k]if round(q['t']*30)==f)
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def existing(f):
 A=rot(value(n,'rotation',f))@np.diag([value(n,'scaleX',f),value(n,'scaleY',f)])@rot(value(inner,'rotation',f));center=np.array([value(n,'x',f),value(n,'y',f)]);return np.column_stack([A,center-A@[W/2,H/2]])
known=np.array([existing(f)for f in[735,736,737]]);coef=np.polyfit([-2,-1,0],known.reshape(3,6),2);reports=[];prior={q['frame']:q for q in json.loads((D/'measured-poses.json').read_text())};start=time.monotonic()
for f in[738,739,740]:
 M0=np.array(prior[f]['matrix']) if f<740 else 2*np.array(reports[-1]['matrix'])-np.array(reports[-2]['matrix']);src=cv2.imread(str(R/'lunch-native'/f'{f-609:03d}.png')).astype(float);baseline=cv2.imread(str(R.parents[1]/'outputs/03-photon-mini/frames-gsap'/f'{f:06d}.png')).astype(float);L,T,RR,B=(800,0,935,110)if f==738 else(830,0,930,65)if f==739 else(880,0,915,14);target=src[T:B,L:RR];bg=baseline[T:B,L:RR];red,green,blue=target[:,:,2],target[:,:,1],target[:,:,0];color=(red>green+12)&(green>blue+8)&(target.max(2)-target.min(2)>40);targetmask=ndimage.binary_dilation(ndimage.binary_fill_holes(color),iterations=2)
 if f==740:
  ar,ag,ab=asset[:,:,2],asset[:,:,1],asset[:,:,0];tm=(asset[:,:,3]>127)&(ar>ag+12)&(ag>ab+8)&(asset[:,:,:3].max(2)-asset[:,:,:3].min(2)>40);yy,xx=np.nonzero(tm);pts=M0@np.vstack([xx,yy,np.ones(len(xx))]);sy,sx=np.nonzero(color);M0[1,2]+=T+sy.max()-pts[1].max();pts=M0@np.vstack([xx,yy,np.ones(len(xx))]);visible=(pts[1]>=-.5)&(pts[1]<=4.5);M0[0,2]+=L+(sx.min()+sx.max())/2-(pts[0,visible].min()+pts[0,visible].max())/2

 def material(v):
  M=M0.copy()
  if f<740:M[:,:2]+=np.array(v[:4]).reshape(2,2);M[:,2]+=v[4:6];op=v[6]
  else:M[:,2]+=v[:2];op=v[2]
  local=M.copy();local[:,2]-=[L,T];warp=cv2.warpAffine(premult,local,(RR-L,B-T),flags=cv2.INTER_LINEAR);pred=warp[:,:,:3]*op+bg*(1-warp[:,:,3:]*op);return M,op,pred,warp[:,:,3]
 def loss(v):
  M,op,pred,a=material(v);mask=targetmask|(a>.10)
  return float(np.mean(abs(pred-target)[mask]))if mask.any()else 1e3
 bounds=[(-.11,.11)]*4+[(-9,9),(-9,9),(.94,1)]if f<740 else[(-3,3),(-3,3),(.9,1)]
 fit=differential_evolution(loss,bounds,seed=f,popsize=7,maxiter=120,tol=.0008,polish=False,workers=1);polish=minimize(loss,fit.x,method='Powell',bounds=bounds,options={'maxiter':60,'xtol':.0003,'ftol':.00001});v=polish.x if polish.fun<fit.fun else fit.x;M,op,pred,a=material(v);baselineError=float(np.mean(abs(bg-target)[targetmask]));cv2.imwrite(str(D/f'{f}-predicted-ROI.png'),np.uint8(np.clip(pred,0,255)));row={'frame':f,'matrix':M.tolist(),'opacity':float(op),'fitMAE':loss(v),'baselineTargetMAE':baselineError,'ROI':[L,T,RR,B],'sourceColoredPixels':int(color.sum()),'seedMatrix':M0.tolist(),'method':'Native original Apple RGBA under measured affine camera; full opaque texture fit738/739 and constrained continuation/translation for clipped27pixel tip740. All baseline actors remain unchanged.'};reports.append(row);print(row,'seconds',time.monotonic()-start,flush=True)
(D/'measured-poses-v2.json').write_text(json.dumps(reports,indent=2));print('DONE',time.monotonic()-start,flush=True)
