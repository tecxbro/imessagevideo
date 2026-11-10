from pathlib import Path
import sys,json,math,time,importlib.util
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent;cv2.setNumThreads(1);cv2.setRNGSeed(14)
spec=importlib.util.spec_from_file_location('field',R/'fit_field.py');field=importlib.util.module_from_spec(spec);spec.loader.exec_module(field)
sift=cv2.SIFT_create(contrastThreshold=.008,edgeThreshold=14)
IDS=json.loads((R/'template-order.json').read_text());templates={}
for id in IDS:
 im=cv2.imread(str(R/(id+'-local-template.png')));kp,desc=sift.detectAndCompute(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),None);templates[id]=(im,kp,desc)

def detect(src):
 gray=src.mean(2);neutral=src.max(2)-src.min(2)<14;m=neutral&(gray>185)&(gray<249);lab,count=ndimage.label(m);out=[]
 for k,bb in enumerate(ndimage.find_objects(lab),1):
  if bb is None:continue
  yy,xx=bb;w,h=xx.stop-xx.start,yy.stop-yy.start
  if 380<w<850 and 22<h<160:
   # Actual ring must have enough enclosed pixels and lie near one of the four agent slots.
   x=(xx.start+xx.stop)/2;y=(yy.start+yy.stop)/2
   z=src[yy,xx][:,:min(w,130)];rr,gg,blue=z[:,:,0],z[:,:,1],z[:,:,2];colored=(rr>gg+45)&(rr>130)
   ratio=float(np.median(blue[colored]/rr[colored])) if colored.sum()>8 else None
   if ratio is not None and ratio>.72:id='pb-capsule-lyft'
   elif ratio is not None and ratio>.28:id='pb-capsule-airbnb'
   elif ratio is not None:id='pb-capsule-resy'
   elif x>1050 and 100<y<420:id='pb-uber-eats'
   elif 100<y<420 and x<900:id='pb-capsule-lyft'
   elif 360<y<750 and 500<x<1300:id='pb-capsule-airbnb'
   elif y>740 and 200<x<1050:id='pb-capsule-resy'
   else:continue
   out.append(dict(id=id,label=k,bbox=[xx.start,yy.start,xx.stop,yy.stop],pixels=int((lab[bb]==k).sum())))
 # A soft search-query halo briefly joins the upper Lyft border. Recover that
 # bounded border from its clean center/lower edges instead of treating the
 # merged query+card component as a giant capsule.
 if not any(q['id']=='pb-capsule-lyft' for q in out):
  pink=(src[:,:,0]>src[:,:,1]+70)&(src[:,:,2]>src[:,:,0]*.72)&(src[:,:,0]>150)
  pl,pc=ndimage.label(pink);sizes=np.bincount(pl.ravel());sizes[0]=0
  if len(sizes)>1 and sizes.max()>40:
   yy,xx=np.nonzero(pl==int(sizes.argmax()));cy=float((yy.min()+yy.max())/2);cx=float((xx.min()+xx.max())/2)
   L=max(0,int(cx-75));RR=min(1920,int(cx+560));T=max(0,int(cy-7));B=min(1080,int(cy+8));band=m[T:B,L:RR];ys,xs=np.nonzero(band)
   if len(xs)>20:
    left=L+int(xs.min());right=L+int(xs.max())+1;T2=int(cy+40);B2=min(1080,int(cy+70));ys,xs=np.nonzero(m[T2:B2,left:right]);bottom=T2+int(ys.max())+1 if len(ys) else int(cy+59);top=bottom-117
    if 590<right-left<620:
     right=left+604
     label=int(lab.max())+1;Y,X=np.indices((117,right-left));rad=58.5;dx=np.maximum(np.maximum(rad-X,0),X-(right-left-rad));dy=Y-58.;edge=np.abs(np.sqrt(dx*dx+dy*dy)-rad)<5;lab[top:bottom,left:right][edge]=label;out.append(dict(id='pb-capsule-lyft',label=label,bbox=[left,top,right,bottom],pixels=int(edge.sum()),disconnectedQueryHalo=True))
 return lab,out


def fit_caps(src,q,f):
 id=q['id'];l,t,r,b=q['bbox'];pad=5;L,T,RR,B=max(0,l-pad),max(0,t-pad),min(1920,r+pad),min(1080,b+pad);crop=np.uint8(src[T:B,L:RR]);sk,sd=sift.detectAndCompute(cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY),None);im,kp,desc=templates[id];W,H=(598,120) if id=='pb-uber-eats' else(604,117);M=None;quality={}
 if sd is not None:
  good=[m for m,z in cv2.BFMatcher().knnMatch(desc,sd,k=2) if m.distance<.8*z.distance and m.distance<280]
  if len(good)>=4:
   a=np.float32([kp[m.queryIdx].pt for m in good]);bb=np.float32([sk[m.trainIdx].pt for m in good]);M,ins=cv2.estimateAffine2D(a,bb,method=cv2.RANSAC,ransacReprojThreshold=2,maxIters=2000,confidence=.995,refineIters=15)
   if M is not None:
    keep=ins.ravel()>0;quality=dict(matches=len(good),inliers=int(keep.sum()),RMS=float(np.sqrt(np.mean((cv2.transform(a[keep,None,:],M)[:,0]-bb[keep])**2))));sv=np.linalg.svd(M[:,:2])[1]
    if sv.min()<.1 or sv.max()>2 or np.linalg.det(M[:,:2])<0 or keep.sum()<4:M=None
 if M is not None:
  M[:,2]+=M[:,:2]@np.array([16,20])+[L,T];q['matrix']=M.tolist();q['fit']='local SIFT affine';q['quality']=quality
 else:q['matrix']=[[float((r-l)/W),0,float(l)],[0,float((b-t)/H),float(t)]];q['fit']='ring-bbox fallback';q['quality']=quality
 return q

if __name__=='__main__':
 out={};start=time.monotonic()
 for f in range(436,526):
  src=np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float);gray=src.mean(2);lab,caps=detect(src);caps=[fit_caps(src,q,f) for q in caps];hidden=field.selected(src)
  for q in caps:hidden.add({'pb-capsule-lyft':(1,1),'pb-capsule-airbnb':(3,2),'pb-capsule-resy':(6,2),'pb-uber-eats':(1,3)}[q['id']])
  cells=[] if f>=510 else[field.fit_cell(n,f,src,gray,hidden) for n in field.NODES]
  out[str(f)]=dict(caps=caps,cells=cells)
  (R/'dense-measure-progress.json').write_text(json.dumps(out,separators=(',',':')))
  if f%5==0:print(f,'caps',[(q['id'],q['bbox'],q['fit']) for q in caps],'seconds',round(time.monotonic()-start,1),flush=True)
 (R/'dense-measurements.json').write_text(json.dumps(out,indent=2));print('complete',len(out),'seconds',time.monotonic()-start,flush=True)
