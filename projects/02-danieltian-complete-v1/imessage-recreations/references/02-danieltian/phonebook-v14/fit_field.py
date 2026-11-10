"""Measure original number artwork poses, not font substitutions."""
from pathlib import Path
import sys,json,math,copy,time
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;P=R.parent.parent.parent/'outputs/02-danieltian/final-v13';cv2.setNumThreads(1);cv2.setRNGSeed(1400);BG=253.;SCENE=json.loads((P/'scene.json').read_text());NODES=[q for q in SCENE['layers'] if q['id'].startswith('pb-number-')]
def sample(ks,t,default):
 if not ks:return default
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);ease=b.get('ease','linear')
   if ease=='easeOut':f=1-(1-f)**3
   if ease=='easeIn':f=f**3
   return a['value']+(b['value']-a['value'])*f
 return ks[-1]['value']
def pose(n,f):
 t=f/30;return {k:sample(n.get('keyframes',{}).get(k),t,n.get(k,1 if k in ['scaleX','scaleY','opacity'] else 0)) for k in ['x','y','scaleX','scaleY','opacity']}
def selected(src):
 z=src;rr,gg,bb=z[:,:,0],z[:,:,1],z[:,:,2];out=set()
 if np.count_nonzero((rr[100:400,:850]>150)&(gg[100:400,:850]<100)&(bb[100:400,:850]>145))>8:out.add((1,1))
 if np.count_nonzero((rr[400:700,400:1100]>170)&(gg[400:700,400:1100]<115)&(bb[400:700,400:1100]>70)&(bb[400:700,400:1100]<170))>8:out.add((3,2))
 if np.count_nonzero((rr[750:,:1100]>170)&(gg[750:,:1100]<110)&(bb[750:,:1100]<65))>8:out.add((6,2))
 if np.count_nonzero((gg[100:400,1050:]>rr[100:400,1050:]+15)&(gg[100:400,1050:]>bb[100:400,1050:]+10)&(gg[100:400,1050:]>45))>8:out.add((1,3))
 return out
TEMPLATES={}
for n in NODES:
 p=(P/n['src']).resolve();im=Image.open(p).convert('RGBA');alpha=np.asarray(im)[:,:,3].astype(np.float32)/255;W,H=im.size;yy,xx=np.nonzero(alpha>.5);TEMPLATES[n['id']]=dict(alpha=alpha,width=W,height=H,ink=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],asset=str(p))
def fit_cell(n,f,src,gray,hidden):
 r,c=map(int,n['id'].rsplit('-',2)[1:]);p=pose(n,f);temp=TEMPLATES[n['id']];W,H=temp['width'],temp['height'];old=np.array([[p['scaleX'],0,p['x']],[0,p['scaleY'],p['y']]],float)
 if (r,c) in hidden:return dict(id=n['id'],frame=f,matrix=old.tolist(),opacity=0,status='phone replaced by visible agent',asset=temp['asset'],width=W,height=H)
 PAD=32;CW=max(W+PAD*2,int(math.ceil(W*p['scaleX']))+PAD*2);CH=max(H+PAD*2,int(math.ceil(H*p['scaleY']))+PAD*2);origin=np.floor([p['x']-PAD,p['y']-PAD]).astype(int);target=np.zeros((CH,CW),np.float32);valid=np.zeros((CH,CW),np.uint8);l,t=origin;rgt,bot=l+CW,t+CH;L,T,RR,B=max(0,l),max(0,t),min(1920,rgt),min(1080,bot)
 if RR<=L or B<=T:return dict(id=n['id'],frame=f,matrix=old.tolist(),opacity=0,status='outside frame',asset=temp['asset'],width=W,height=H)
 target[T-t:B-t,L-l:RR-l]=np.clip((BG-gray[T:B,L:RR])/BG,0,1);valid[T-t:B-t,L-l:RR-l]=255;region=target[valid>0];peak=float(np.percentile(region,99))
 if peak<2/BG:return dict(id=n['id'],frame=f,matrix=old.tolist(),opacity=0,status='no measurable field ink',peak=peak,asset=temp['asset'],width=W,height=H)
 canvas=np.zeros_like(target);canvas[PAD:PAD+H,PAD:PAD+W]=temp['alpha'];bb=temp['ink'];mask=(target>peak*.5)&(valid>0);ys,xs=np.nonzero(mask);sx,sy=p['scaleX'],p['scaleY'];tx=p['x']-l-PAD*sx;ty=p['y']-t-PAD*sy
 if len(xs)>20:
  xb,yb,xe,ye=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1);clipL=l<0;clipR=rgt>1920
  if not clipL and not clipR:sx=(xe-xb)/(bb[2]-bb[0])
  sy=(ye-yb)/(bb[3]-bb[1]);sx=float(np.clip(sx,.7,1.3));sy=float(np.clip(sy,.7,1.3));tx=(xe-sx*(PAD+bb[2])) if clipL else (xb-sx*(PAD+bb[0]));ty=yb-sy*(PAD+bb[1])
 init=np.float32([[sx,0,tx],[0,sy,ty]]);warp=init.copy();status='ECC affine'
 try:rho,warp=cv2.findTransformECC(canvas,target,warp,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,1e-5),valid,3)
 except cv2.error:rho=0;warp=init;status='bbox fallback: ECC rejected'
 singular=np.linalg.svd(warp[:,:2])[1]
 if not(.65<singular.min() and singular.max()<1.4 and np.linalg.det(warp[:,:2])>0 and rho>.55):warp=init;status='bbox fallback: unreliable affine'
 pred=cv2.warpAffine(canvas,warp,(CW,CH),flags=cv2.INTER_LINEAR);m=(pred>.03)&(valid>0);op=float(np.clip(np.sum(pred[m]*target[m])/max(1e-8,np.sum(pred[m]**2)),0,1));error=float(np.mean(np.abs(op*pred[m]-target[m]))*BG) if m.any() else 0;M=warp.astype(float);M[:,2]+=M[:,:2]@np.array([PAD,PAD])+origin;return dict(id=n['id'],frame=f,matrix=M.tolist(),opacity=op,status=status,rho=float(rho),foregroundMAE=error,asset=temp['asset'],width=W,height=H,oldPose=p)
def run(frames,outname):
 out={};started=time.monotonic()
 for f in frames:
  src=np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float);gray=src.mean(2);hidden=selected(src);out[str(f)]=[fit_cell(n,f,src,gray,hidden) for n in NODES];print(f,'poses',len(out[str(f)]),'ECC',sum(q['status']=='ECC affine' for q in out[str(f)]),'seconds',round(time.monotonic()-started,2),flush=True);(R/(outname+'-progress.json')).write_text(json.dumps(out))
 (R/(outname+'.json')).write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':run([443,486,501],'field-affine-probe')
