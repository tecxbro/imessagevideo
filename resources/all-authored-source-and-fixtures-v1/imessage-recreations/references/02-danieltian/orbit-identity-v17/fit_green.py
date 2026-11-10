from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import ndimage,optimize
ROOT=Path(__file__).resolve().parents[3];REF=Path(__file__).resolve().parent;OUT=ROOT/'outputs/02-danieltian/orbit-identity-v17'
def fit(a):
 a=a.astype(float);r,g,b=a.transpose(2,0,1);m=(g-r>40)&(g-b>20)&(g>150);lab,n=ndimage.label(m,np.ones((3,3)));counts=np.bincount(lab.ravel());counts[0]=0
 if n==0 or counts.max()<20:return None
 m=lab==counts.argmax();edge=m&~ndimage.binary_erosion(m);edge[:2]=False;edge[-2:]=False;edge[:,:2]=False;edge[:,-2:]=False;y,x=np.where(edge);x=x.astype(float)+.5;y=y.astype(float)+.5
 if len(x)<8:return dict(status='insufficient-unclipped-edge',points=len(x))
 visible=ndimage.find_objects(m.astype(int))[0];yy,xx=visible;cx=(xx.start+xx.stop)/2;cy=(yy.start+yy.stop)/2;rx=(xx.stop-xx.start)/2;ry=(yy.stop-yy.start)/2
 if yy.stop>=a.shape[0]:cy=yy.start+rx;ry=rx
 if xx.stop>=a.shape[1]:cx=xx.start+ry;rx=ry
 def residual(p):
  cx,cy,rx,ry=p;return (np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)-1)*(rx+ry)/2
 res=optimize.least_squares(residual,[cx,cy,max(rx,2),max(ry,2)],bounds=([-1000,-1000,5,5],[3000,2500,1000,1000]),loss='soft_l1',f_scale=.4,max_nfev=5000)
 p=res.x;J=res.jac;cov=np.linalg.pinv(J.T@J)*np.mean(res.fun**2)
 return dict(status='ellipse-fit',cx=float(p[0]),cy=float(p[1]),rx=float(p[2]),ry=float(p[3]),bounds=[float(p[0]-p[2]),float(p[1]-p[3]),float(p[0]+p[2]),float(p[1]+p[3])],rms=float(np.sqrt(np.mean(res.fun**2))),stddev=np.sqrt(np.diag(cov)).tolist(),pointCount=len(x),stageCensored=[xx.start==0,xx.stop==a.shape[1],yy.start==0,yy.stop==a.shape[0]],edgePoints=np.stack([x,y],axis=-1).tolist())
