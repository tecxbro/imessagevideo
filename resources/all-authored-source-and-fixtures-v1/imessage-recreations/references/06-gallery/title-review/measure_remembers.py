from pathlib import Path
import sys,importlib.util,json
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image
from scipy.optimize import minimize
from scipy.ndimage import label
R=Path(__file__).resolve().parent;cv2.setNumThreads(1);spec=importlib.util.spec_from_file_location('trace',R.parent.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def load(p):return np.asarray(Image.open(p).convert('RGB')).astype(float)
a=load(R.parent/'native-transition-v18/000600.png');gray=(255-a.mean(2))/255;cuts=[(340,968),(968,1213),(1213,1580)];labels=['Remembers','your','people'];births=[556,561,566];out=[];art=[]
for j,(word,(left,right),birth) in enumerate(zip(labels,cuts,births)):
 mask=gray[450:650,left:right]>.5;yy,xx=np.nonzero(mask);bb=[int(xx.min()+left),int(yy.min()+450),int(xx.max()+left+1),int(yy.max()+450+1)];l,t,r,b=bb;pad=6;template=gray[t-pad:b+pad,l-pad:r+pad].astype(np.float32);d,stats=trace.trace_alpha(template,-pad,-pad);W,H=r-l,b-t;art.append(dict(label=word,sourceFrame=600,sourceBounds=bb,width=W,height=H,path=d,fill='#000000',traceStats=stats));poses=[]
 for n in range(556,581):
  if n<birth:continue
  src=load(R/'remembers-native'/f'{n:06d}.png');roiTop=500 if n==556 else 430;roiHeight=690-roiTop;target=((255-src[roiTop:690,left:right].mean(2))/255).astype(np.float32);peak=float(np.quantile(target[target>.35*target.max()],.96));mk=target>peak*.5;labs,num=label(mk);sz=np.bincount(labs.ravel());keep=sz>=4;keep[0]=False;mk=keep[labs];yy,xx=np.nonzero(mk)
  if len(xx)<20:continue
  bounds=[int(xx.min()+left),int(yy.min()+roiTop),int(xx.max()+left+1),int(yy.max()+roiTop+1)];sx=np.clip((bounds[2]-bounds[0])/W,.95,1.06);sy=np.clip((bounds[3]-bounds[1])/H,.92,1.12);init=[bounds[0],bounds[1],sx,sy,1 if n<birth+4 else 0]
  def score(v,ret=False):
   x,y,sx,sy,blur=v;M=np.array([[sx,0,x-pad*sx-left],[0,sy,y-pad*sy-roiTop]]);warp=cv2.warpAffine(template,M,(right-left,roiHeight),flags=cv2.INTER_LINEAR)
   if blur>.02:warp=cv2.GaussianBlur(warp,(0,0),float(blur))
   op=float(np.clip(np.sum(warp*target)/max(1e-8,np.sum(warp*warp)),0,1));err=float(np.mean(np.abs(target-op*warp)));return (err,op) if ret else err
  if n<birth+9:
   opts=[(init[0]-4,init[0]+4),(init[1]-5,init[1]+5),(.95,1.06),(.92,1.12),(0,10)];fit=minimize(score,init,method='Powell',bounds=opts,options={'maxiter':18,'maxfev':250,'ftol':.00005,'xtol':.0005});v=fit.x
  else:v=np.array(init)
  err,op=score(v,True);fittedOp=op;op=max(op,peak) if v[4]<.3 else op;poses.append(dict(frame=n,x=float(v[0]),y=float(v[1]),scaleX=float(v[2]),scaleY=float(v[3]),blur=float(v[4]),opacity=op,fittedOpacity=fittedOp,measuredCoreOpacity=peak,fitAlphaMAE=err,sourceInkBounds=bounds))
 out.append(dict(label=word,sourceBirth=birth,poses=poses));print(word,[(p['frame'],round(p['opacity'],3),round(p['blur'],2),round(p['x'],2),round(p['y'],2)) for p in poses[:7]],flush=True)
(R/'remembers-measurements.json').write_text(json.dumps(out,indent=2));(R/'remembers-outlines.json').write_text(json.dumps(art,indent=2));print('Measured independent early words; source555 has no title and is excluded',flush=True)
