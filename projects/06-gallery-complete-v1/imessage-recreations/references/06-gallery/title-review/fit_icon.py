from pathlib import Path
import sys,json
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from scipy.optimize import minimize
R=Path(__file__).resolve().parent;cv2.setNumThreads(1);rows=json.loads((R/'measurements.json').read_text());asset=cv2.imread(str(R.parent/'assets/root-lock/messages-icon-canonical.png')).astype(float);h,w=asset.shape[:2];st=asset[:,:,1]-asset[:,:,2] # RGB file read BGR: green minus red.
pk=st.max();m=(st>pk*.45)&(asset[:,:,1]-asset[:,:,0]>pk*.2);yy,xx=np.nonzero(m);ab=[xx.min(),yy.min(),xx.max()+1,yy.max()+1];delta=255-asset;fitrows=[]
for row in rows:
 if not row.get('icon'):continue
 n=row['frame'];l,t,r,b=row['icon']['colorBounds'];sx=(r-l)/(ab[2]-ab[0]);sy=(b-t)/(ab[3]-ab[1]);x=l-ab[0]*sx;y=t-ab[1]*sy;src=cv2.imread(str(R/'source-native'/f'{n:06d}.png')).astype(float);L,T,RR,B=max(0,l-7),max(0,t-7),min(1920,r+7),min(1080,b+7);target=src[T:B,L:RR]
 def score(v,ret=False):
  x,y,sx,sy=v;M=np.array([[sx,0,x-L],[0,sy,y-T]]);warp=cv2.warpAffine(delta,M,(RR-L,B-T),flags=cv2.INTER_LINEAR);q=255-target;opacity=float(np.clip(np.sum(q*warp)/np.sum(warp*warp),0,1));err=float(np.mean(np.abs(q-warp*opacity)));return (err,opacity) if ret else err
 init=np.array([x,y,sx,sy]);bounds=[(x-2,x+2),(y-2,y+2),(sx*.975,sx*1.025),(sy*.975,sy*1.025)];fit=minimize(score,init,method='Powell',bounds=bounds,options={'maxiter':35,'xtol':.0003,'ftol':.0001});v=fit.x;err,op=score(v,True);fitrows.append(dict(frame=n,x=float(v[0]),y=float(v[1]),scaleX=float(v[2]),scaleY=float(v[3]),opacity=op,fitMAE=err,sourceColorBounds=[l,t,r,b],templateColorBounds=[int(q) for q in ab],asset='assets/root-lock/messages-icon-canonical.png'))
(R/'icon-poses.json').write_text(json.dumps(fitrows,indent=2));print(fitrows)
