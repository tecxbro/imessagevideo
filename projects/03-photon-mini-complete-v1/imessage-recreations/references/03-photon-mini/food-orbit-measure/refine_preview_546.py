from pathlib import Path
import sys,json
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from scipy.optimize import differential_evolution
R=Path(__file__).resolve().parents[1];D=R/'food-preview-native-measure';cv2.setNumThreads(1);a=cv2.imread(str(R/'assets/food-preview-original-art.png')).astype(float);source=cv2.imread(str(D/'0546.png')).astype(float);x0,y0=694,975;target=source[y0:1000,x0:741];delta=253-a
def matrix(v):
 sx,sy,x,y,opacity,blur=v;return np.array([[sx,0,x],[0,sy,y]])
def loss(v):
 M=matrix(v);M[:,2]-=[x0,y0];warp=cv2.warpAffine(delta,M,(47,25),flags=cv2.INTER_AREA);warp=cv2.GaussianBlur(warp,(0,0),max(.01,v[-1]));pred=253-warp*v[-2];return float(np.mean((pred-target)**2))
r=differential_evolution(loss,[(.035,.065),(.035,.065),(701,707),(978,985),(.05,.28),(.1,1.6)],seed=546,maxiter=60,popsize=10,tol=.001,polish=False);v=r.x;M=matrix(v);h,w=a.shape[:2];corn=cv2.transform(np.float32([[[0,0],[w,0],[w,h],[0,h]]]),M)[0];out=dict(frame=546,manualBoundedFit=True,matrix=M.tolist(),corners=corn.tolist(),bounds=[float(corn[:,0].min()),float(corn[:,1].min()),float(corn[:,0].max()),float(corn[:,1].max())],opacity=float(v[-2]),estimatedSourceBlur=float(v[-1]),fitMSE=float(r.fun),notice='Tiny25px birth has no reliable feature model. Bounded original-art fit to isolated source ROI; approximate bounds/optical blur, not a reliable affine feature measurement.');(D/'preview546-tiny-fit.json').write_text(json.dumps(out,indent=2));print(out)
p=D/'preview-arrival-affine-measurements.json';d=json.loads(p.read_text());old=d['frames'][0];d['rejected546FalseMatch']=old;d['frames'][0]=out;d['notice']+=' Original5467-inlier top-of-frame match rejected after native inspection. Replaced by separately flagged bounded tiny optical fit.';p.write_text(json.dumps(d,indent=2))
