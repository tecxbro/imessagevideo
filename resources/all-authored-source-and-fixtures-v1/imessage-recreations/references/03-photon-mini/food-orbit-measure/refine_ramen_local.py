"""Recover small/clipped original ramen instances with bounded high-resolution local feature fits."""
from pathlib import Path
import sys,json,math,time
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
R=Path('/workspace/imessage-recreations/references/03-photon-mini');D=R/'food-orbit-measure';cv2.setNumThreads(1);cv2.setRNGSeed(1847);base=json.loads((D/'sift-food-measurements.json').read_text());rgba=cv2.imread(str(R/'assets/apple-ramen.png'),cv2.IMREAD_UNCHANGED);sift=cv2.SIFT_create(contrastThreshold=.009,edgeThreshold=12);tk,td=sift.detectAndCompute(cv2.cvtColor(rgba[:,:,:3],cv2.COLOR_BGR2GRAY),rgba[:,:,3]);out={};started=time.time()
def score(src,M):
 h,w=rgba.shape[:2];pts=cv2.transform(np.float32([[[0,0],[w,0],[w,h],[0,h]]]),M)[0];l=max(0,int(np.floor(pts[:,0].min()))-2);r=min(1920,int(np.ceil(pts[:,0].max()))+2);t=max(0,int(np.floor(pts[:,1].min()))-2);b=min(1080,int(np.ceil(pts[:,1].max()))+2)
 if l>=r or t>=b:return None
 mm=M.copy();mm[:,2]-=[l,t];warped=cv2.warpAffine(rgba,mm,(r-l,b-t));mask=warped[:,:,3]>220
 if mask.sum()<12:return None
 paint=warped[:,:,:3][mask].astype(float);obs=src[t:b,l:r][mask].astype(float);v=253-paint;alpha=float(np.clip(np.sum(v*(253-obs))/max(1,np.sum(v*v)),0,1));err=float(np.mean(np.abs(253-v*alpha-obs)));return pts,alpha,err,int(mask.sum())
def near(a,b):
 ac=np.array(a['center']);bc=np.array(b['center']);aw=np.ptp(a['corners'],axis=0);bw=np.ptp(b['corners'],axis=0);return np.linalg.norm(ac-bc)<max(12,min(*aw,*bw)*.32)
for n in range(730,800):
 src=cv2.imread(str(R/'lunch-native'/f'{n-609:03d}.png'));aa=src.astype(float);r,g,b=aa[:,:,2],aa[:,:,1],aa[:,:,0];orange=(r>90)&(r-g>10)&(r-b>25);lab,num=cv2.connectedComponents(cv2.morphologyEx(orange.astype('uint8'),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8)),8);components=[]
 for li in range(1,lab):
  yy,xx=np.where(num==li)
  if len(xx)<25:continue
  l,t,rr,bb=xx.min(),yy.min(),xx.max()+1,yy.max()+1;w,h=rr-l,bb-t
  if w<10 or h<10 or w>150 or h>160:continue
  components.append([max(0,int(l-.8*w-12)),max(0,int(t-.9*h-12)),min(1920,int(rr+.8*w+12)),min(1080,int(bb+1.2*h+12))])
 models=[]
 for m in base['frames'][str(n)]:
  pts=np.array(m['corners']);size=np.ptp(pts,axis=0)
  if size.max()>400 or m['fitMAE']>45 or (n<795 and m['opacity']<.2):continue
  if m['kind']=='pizza':continue
  models.append(m)
 for box in components:
  l,t,r,b=box;crop=src[t:b,l:r];up=3 if min(crop.shape[:2])<180 else 2;big=cv2.resize(crop,None,fx=up,fy=up,interpolation=cv2.INTER_CUBIC);kp,desc=sift.detectAndCompute(cv2.cvtColor(big,cv2.COLOR_BGR2GRAY),None)
  if desc is None or len(kp)<4:continue
  good=[m for m,z in cv2.BFMatcher().knnMatch(desc,td,k=2) if m.distance<.88*z.distance and m.distance<300]
  if len(good)<4:continue
  for it in range(2):
   if len(good)<4:break
   a=np.float32([tk[m.trainIdx].pt for m in good]);dest=np.float32([kp[m.queryIdx].pt for m in good]);M,inside=cv2.estimateAffine2D(a,dest,method=cv2.RANSAC,ransacReprojThreshold=3*up,maxIters=2500,confidence=.99,refineIters=10)
   if M is None:break
   ids=np.flatnonzero(inside.ravel());iset=set(ids);good=[m for j,m in enumerate(good) if j not in iset]
   if len(ids)<4:continue
   M=M/up;M[:,2]+=[l,t];sx,sy=np.linalg.norm(M[:,0]),np.linalg.norm(M[:,1]);cos=float(np.dot(M[:,0],M[:,1])/max(.001,sx*sy))
   if not(.06<sx<2.5 and .06<sy<2.5 and np.linalg.det(M[:,:2])>0 and abs(cos)<.48):continue
   q=score(src,M)
   if q is None:continue
   pts,alpha,err,pixels=q;size=np.ptp(pts,axis=0);center=pts.mean(0)
   if size.max()>350 or err>43 or (n<795 and alpha<.2) or not(l-20<center[0]<r+20 and t-20<center[1]<b+20):continue
   # A nearly empty white fit must not become a fake food object.
   if np.ptp(a[ids,0])<22 or np.ptp(a[ids,1])<22:continue
   model=dict(kind='ramen',matrix=M.tolist(),corners=pts.tolist(),center=center.tolist(),scale=[float(sx),float(sy)],shearCos=cos,inliers=len(ids),fitMAE=err,opacity=alpha,visibleTemplatePixels=pixels,localRefinement=True)
   old=next((m for m in models if near(m,model)),None)
   if old:
    if err<old['fitMAE']-.5 and len(ids)>=max(4,old['inliers']*.5):models.remove(old);models.append(model)
   else:models.append(model)
 pizzas=[m for m in base['frames'][str(n)] if m['kind']=='pizza' and np.ptp(np.array(m['corners']),axis=0).max()<450 and m['fitMAE']<45 and (n>=795 or m['opacity']>=.2)];pizzas.sort(key=lambda q:(-q['inliers'],q['fitMAE']));models.sort(key=lambda q:(q['fitMAE']>35,-q['inliers'],q['fitMAE']));out[str(n)]=pizzas[:6]+models[:4]
 if n%10==0:print(n,'ramen',len(models[:4]),'pizza',len(pizzas[:6]),'elapsed',round(time.time()-started,1),flush=True)
 (D/'food-refined-progress.json').write_text(json.dumps(out))
(D/'food-refined-measurements.json').write_text(json.dumps(out,indent=2));print('Local ramen refinement complete',round(time.time()-started,1),flush=True)
