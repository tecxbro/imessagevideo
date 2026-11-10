"""Measure independent original food artwork against every source-native frame.
The reference PNGs are measurement-only; output contains affine poses/opacity.
"""
from pathlib import Path
import sys,json,math,time
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
R=Path('/workspace/imessage-recreations/references/03-photon-mini');D=R/'food-orbit-measure';cv2.setNumThreads(1);cv2.setRNGSeed(1847);sift=cv2.SIFT_create(contrastThreshold=.012,edgeThreshold=12);templates={}
for kind,file in [('pizza','apple-pizza.png'),('ramen','apple-ramen.png')]:
 img=cv2.imread(str(R/'assets'/file),cv2.IMREAD_UNCHANGED);kp,desc=sift.detectAndCompute(cv2.cvtColor(img[:,:,:3],cv2.COLOR_BGR2GRAY),img[:,:,3]);templates[kind]=dict(image=img,kp=kp,desc=desc,file=file)
def overlap(a,b):
 ac=np.mean(a['corners'],axis=0);bc=np.mean(b['corners'],axis=0);aw=np.ptp(a['corners'][:,0]);ah=np.ptp(a['corners'][:,1]);bw=np.ptp(b['corners'][:,0]);bh=np.ptp(b['corners'][:,1]);return np.linalg.norm(ac-bc)<max(15,min(aw,ah,bw,bh)*.3)
def score(source,rgba,M):
 H,W=source.shape[:2];h,w=rgba.shape[:2];pts=cv2.transform(np.float32([[[0,0],[w,0],[w,h],[0,h]]]),M)[0];l=max(0,int(math.floor(pts[:,0].min()))-2);t=max(0,int(math.floor(pts[:,1].min()))-2);r=min(W,int(math.ceil(pts[:,0].max()))+2);b=min(H,int(math.ceil(pts[:,1].max()))+2)
 if r<=l or b<=t:return None
 local=M.copy();local[:,2]-=[l,t];warp=cv2.warpAffine(rgba,local,(r-l,b-t),flags=cv2.INTER_LINEAR);mask=warp[:,:,3]>220
 if mask.sum()<10:return None
 observed=source[t:b,l:r][mask].astype(float);paint=warp[:,:,:3][mask].astype(float);v=253-paint;q=253-observed;alpha=float(np.clip(np.sum(v*q)/max(1,np.sum(v*v)),0,1.1));pred=253-v*min(1,alpha);error=float(np.mean(np.abs(observed-pred)));return error,min(1,alpha),int(mask.sum())
records={};started=time.time()
for n in range(730,800):
 source=cv2.imread(str(R/'lunch-native'/f'{n-609:03d}.png'));sk,sd=sift.detectAndCompute(cv2.cvtColor(source,cv2.COLOR_BGR2GRAY),None);found=[]
 for kind,temp in templates.items():
  kp,desc=temp['kp'],temp['desc'];pairs=cv2.BFMatcher().knnMatch(sd,desc,k=2);good=[m for m,z in pairs if m.distance<.85*z.distance and m.distance<280];remaining=list(good);models=[]
  for it in range(18):
   if len(remaining)<4:break
   a=np.float32([kp[m.trainIdx].pt for m in remaining]);b=np.float32([sk[m.queryIdx].pt for m in remaining]);M,inside=cv2.estimateAffine2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=6000,confidence=.995,refineIters=10)
   if M is None:break
   indices=np.flatnonzero(inside.ravel());iset=set(indices);remaining=[m for i,m in enumerate(remaining) if i not in iset]
   if len(indices)<4:continue
   sx,sy=np.linalg.norm(M[:,0]),np.linalg.norm(M[:,1]);det=np.linalg.det(M[:,:2]);cos=np.dot(M[:,0],M[:,1])/max(.001,sx*sy)
   if not(.06<sx<4.5 and .06<sy<4.5 and det>0 and abs(cos)<.48):continue
   pts=a[indices]
   if np.ptp(pts[:,0])<temp['image'].shape[1]*.12 or np.ptp(pts[:,1])<temp['image'].shape[0]*.12:continue
   h,w=temp['image'].shape[:2];corners=cv2.transform(np.float32([[[0,0],[w,0],[w,h],[0,h]]]),M)[0];q=score(source,temp['image'],M)
   if q is None or q[0]>70:continue
   error,opacity,pixels=q;model=dict(kind=kind,matrix=M,corners=corners,inliers=len(indices),fitMAE=error,opacity=opacity,visibleTemplatePixels=pixels,center=corners.mean(0),scale=[sx,sy],shearCos=float(cos))
   if any(overlap(model,old) for old in models):continue
   models.append(model)
  found+=models
 def native(x):
  if isinstance(x,np.ndarray):return x.tolist()
  if isinstance(x,np.generic):return x.item()
  raise TypeError(type(x))
 records[str(n)]=found
 if n%10==0:print(n,{k:sum(m['kind']==k for m in found) for k in templates},'elapsed',round(time.time()-started,1),flush=True)
 (D/'sift-food-measurements-progress.json').write_text(json.dumps(records,default=native))
(D/'sift-food-measurements.json').write_text(json.dumps(dict(frames=records,notice='Measured affine poses of separately declared original food artwork. Source frames are never runtime layers.',sourceRange=[730,799],templates={k:v['file'] for k,v in templates.items()}),default=native,indent=2));print('Complete',round(time.time()-started,1),flush=True)
