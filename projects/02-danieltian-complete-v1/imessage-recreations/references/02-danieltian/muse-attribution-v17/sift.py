from pathlib import Path
from PIL import Image
import numpy as np,json,sys
sys.path.insert(0,'/tmp/imessage-food-cv');import cv2
R=Path(__file__).resolve().parent;ROOT=R.parents[2];old=R.parent/'orbit-identity-v17';O=ROOT/'outputs/02-danieltian/muse-attribution-v17';s=json.load(open(old/'base-compact.json'));asset=ROOT/'outputs/02-danieltian/final-v16/assets/bcef7f6e94d52bccb3722accc0c7a211ec9f3491c51293b0f2c055e03ec7c2ab.png';im=Image.open(asset).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);template=np.array(bg.convert('RGB'));gray=cv2.cvtColor(template,cv2.COLOR_RGB2GRAY);sift=cv2.SIFT_create(nfeatures=1500,contrastThreshold=.005,edgeThreshold=20);kp,des=sift.detectAndCompute(gray,None);matcher=cv2.BFMatcher();rows=[]
for n in [565,575,585]:
 row=dict(frame=n)
 for kind,path in [('source',old/f'source/{n:06}.png'),('native',ROOT/f'outputs/02-danieltian/orbit-identity-v17/baseline-native16/{n:06}.png')]:
  a=np.array(Image.open(path).convert('RGB'));p=next(l for l in s['layers'] if l['id']==f'root-orbit-pose-{n}');node=next(c for c in p['children'] if c['id'].endswith('middle-fly-muse'));pad=90;x1=max(0,int(node['x'])-pad);y1=max(0,int(node['y'])-pad);x2=min(1920,int(node['x']+235*node['scaleX'])+pad);y2=min(1080,int(node['y']+236*node['scaleY'])+pad);crop=a[y1:y2,x1:x2];kk,dd=sift.detectAndCompute(cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY),None);matches=matcher.knnMatch(des,dd,k=2) if dd is not None else [];good=[m for m,q in matches if m.distance<.75*q.distance];src=np.float32([kp[m.queryIdx].pt for m in good]);dst=np.float32([kk[m.trainIdx].pt for m in good])+[x1,y1];M,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2,maxIters=10000,confidence=.999) if len(good)>=4 else (None,None)
  if M is None:q=dict(status='no-confident-transform',matches=len(good))
  else:
   mask=inliers.ravel().astype(bool);err=np.linalg.norm(src@M[:,:2].T+M[:,2]-dst,axis=1);q=dict(status='affine',matrix=M.tolist(),matches=len(good),inliers=int(mask.sum()),rms=float(np.sqrt(np.mean(err[mask]**2))),scale=float(np.hypot(M[0,0],M[1,0])),angle=float(np.degrees(np.arctan2(M[1,0],M[0,0]))),crop=[x1,y1,x2,y2],pairs=[dict(template=src[i].tolist(),stage=dst[i].tolist(),inlier=bool(mask[i]),residual=float(err[i])) for i in range(len(good))])
  row[kind]=q;print(n,kind,{k:v for k,v in q.items() if k!='pairs'})
 rows.append(row)
(R/'sift-controls.json').write_text(json.dumps(dict(asset=str(asset),templateFeatures=len(kp),frames=rows,notice='Read-only actual source and actualV16 native controls. Similarity RANSAC uses genuine original M artwork; ROI only bounds computation, all clipping is explicit. Inliers/RMS retained; no accepted trajectory is altered.'),indent=2))
