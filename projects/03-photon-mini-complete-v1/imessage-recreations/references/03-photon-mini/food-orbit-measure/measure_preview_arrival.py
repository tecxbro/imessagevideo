from pathlib import Path
import sys,json,math
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'food-preview-native-measure';cv2.setNumThreads(1);cv2.setRNGSeed(551);sift=cv2.SIFT_create(contrastThreshold=.008,edgeThreshold=12);template=cv2.imread(str(R/'assets/food-preview-original-art.png'));kp,desc=sift.detectAndCompute(cv2.cvtColor(template,cv2.COLOR_BGR2GRAY),None);h,w=template.shape[:2];records=[]
for n in range(546,567):
 im=cv2.imread(str(D/f'{n:04d}.png'));sk,sd=sift.detectAndCompute(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),None);pairs=cv2.BFMatcher().knnMatch(desc,sd,k=2);good=[m for m,z in pairs if m.distance<.75*z.distance and m.distance<240];row=dict(frame=n,matches=len(good))
 if len(good)>=5:
  a=np.float32([kp[m.queryIdx].pt for m in good]);b=np.float32([sk[m.trainIdx].pt for m in good]);M,ins=cv2.estimateAffine2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=2.5,maxIters=4000,confidence=.999);inside=np.flatnonzero(ins.ravel()) if ins is not None else []
  if M is not None and len(inside)>=5 and np.linalg.det(M[:,:2])>.1:
   corners=cv2.transform(np.float32([[[0,0],[w,0],[w,h],[0,h]]]),M)[0];W,H=im.shape[1],im.shape[0];l=max(0,int(corners[:,0].min()));t=max(0,int(corners[:,1].min()));r=min(W,int(corners[:,0].max())+1);bot=min(H,int(corners[:,1].max())+1);local=M.copy();local[:,2]-=[l,t];warp=cv2.warpAffine(template,local,(r-l,bot-t));mask=cv2.warpAffine(np.ones((h,w),np.uint8)*255,local,(r-l,bot-t))>250;mask=cv2.erode(mask.astype('uint8'),np.ones((7,7),np.uint8))>0;obs=im[t:bot,l:r][mask].astype(float);paint=warp[mask].astype(float);v=253-paint;q=253-obs;alpha=float(np.clip(np.sum(v*q)/np.sum(v*v),0,1));error=float(np.mean(np.abs(obs-(253-v*alpha))));nativeM=M.copy();nativeM[:,:2]=nativeM[:,:2]@np.diag([w/520,h/274.7721179624665]);row.update(matrix=M.tolist(),nativeChildLocalMatrix=nativeM.tolist(),corners=corners.tolist(),bounds=[l,t,r,bot],inliers=len(inside),inlierRMS=float(np.sqrt(np.mean((cv2.transform(a[inside,None,:],M)[:,0,:]-b[inside])**2))),opacity=alpha,fitMAE=error,notice='Source-world affine for original bounded art only; source native image pixels are measurement, never a runtime full-frame layer.')
 records.append(row)
 print(n,row.get('bounds'),row.get('inliers'),row.get('opacity'),flush=True)
report=dict(template='assets/food-preview-original-art.png',templateIntrinsic=[w,h],nativeChildSize=[520,274.7721179624665],frames=records,notice='Affine fits of genuine preview artwork against native546–566. Missing model means no reliable feature measurement, not certified absence. Parent/native panel/UI unchanged.');(D/'preview-arrival-affine-measurements.json').write_text(json.dumps(report,indent=2))
