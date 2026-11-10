from pathlib import Path
import sys,json
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image,ImageDraw
R=Path('/workspace/imessage-recreations/references/03-photon-mini');N=769;a=cv2.imread(str(R/'lunch-native'/f'{N-609:03d}.png'));sift=cv2.SIFT_create(contrastThreshold=.012,edgeThreshold=12);sk,sd=sift.detectAndCompute(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),None);records=[]
for kind,file in [('pizza','apple-pizza.png'),('ramen','apple-ramen.png')]:
 ti=cv2.imread(str(R/'assets'/file),cv2.IMREAD_UNCHANGED);tk,td=sift.detectAndCompute(cv2.cvtColor(ti[:,:,:3],cv2.COLOR_BGR2GRAY),ti[:,:,3]);matches=cv2.BFMatcher().knnMatch(sd,td,k=2);good=[m for m,n in matches if m.distance<.85*n.distance and m.distance<280];print(kind,'template kps',len(tk),'matches',len(good));remaining=list(good)
 for it in range(10):
  if len(remaining)<3:break
  src=np.float32([tk[m.trainIdx].pt for m in remaining]);dst=np.float32([sk[m.queryIdx].pt for m in remaining]);M,inliers=cv2.estimateAffine2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=6000,confidence=.995,refineIters=10)
  if M is None:break
  idx=np.flatnonzero(inliers.ravel());w,h=ti.shape[1],ti.shape[0];corners=np.float32([[0,0],[w,0],[w,h],[0,h]]);points=cv2.transform(corners[None],M)[0];sx=np.linalg.norm(M[:,0]);sy=np.linalg.norm(M[:,1]);det=np.linalg.det(M[:,:2]);cos=np.dot(M[:,0],M[:,1])/max(.001,sx*sy)
  if len(idx)>=3 and .08<sx<4 and .08<sy<4 and det>0 and abs(cos)<.35:
   records.append(dict(kind=kind,matrix=M.tolist(),count=len(idx),corners=points.tolist(),scale=[sx,sy],cos=float(cos)));cv2.polylines(a,[np.int32(points)],True,(0,0,255) if kind=='pizza' else (255,0,0),2)
  remaining=[m for j,m in enumerate(remaining) if j not in set(idx)]
print(json.dumps(records,indent=2));cv2.imwrite(str(R/'food-orbit-measure/sift-probe-769.jpg'),a);(R/'food-orbit-measure/sift-probe-769.json').write_text(json.dumps(records,indent=2))
