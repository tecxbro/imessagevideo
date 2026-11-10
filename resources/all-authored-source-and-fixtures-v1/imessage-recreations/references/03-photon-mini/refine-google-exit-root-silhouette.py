"""Fit one bounded original phone artwork with native scale, position and opacity."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from scipy import ndimage,optimize
REF=Path(__file__).resolve().parent;N=REF/'assets/root-zoom-measure';AS=REF/'assets/root-zoom';AS.mkdir(exist_ok=True)
base=Image.open(N/'frame-891.png').convert('RGB').crop((772,165,1147,914));asset=AS/'google-phone-canonical-891.png';base.save(asset);b=np.array(base,dtype=float);gray=b.mean(2);ink=253-gray;canonical=np.array([772.,165.,1.,1.]);poses=[]
for n in range(891,899):
 a=np.array(Image.open(N/f'frame-{n}.png').convert('RGB')).astype(float);target=253-a.mean(2);lab,_=ndimage.label(target>1,np.ones((3,3)));sl=max((s for s in ndimage.find_objects(lab) if s is not None),key=lambda s:(lab[s]>0).sum());yy,xx=sl
 # Normalize the silhouette threshold by the actual material contrast. A
 # whole-UI Powell fit was trapped by repeated text and stretched the phone.
 # The physical rim bounds provide an independent, stable camera constraint.
 def physical_bounds(z):
  peak=float(np.percentile(z[z>1],97));m=z>.18*peak;labels,_=ndimage.label(m,np.ones((3,3)));choices=[]
  for i,sl_ in enumerate(ndimage.find_objects(labels)):
   if sl_ is not None:
    y_,x_=sl_;w=x_.stop-x_.start;h=y_.stop-y_.start
    if h>1.7*w and h<2.3*w:choices.append((int((labels[sl_]==i+1).sum()),sl_))
  _,sl_=max(choices);y_,x_=sl_;return x_.start,y_.start,x_.stop,y_.stop
 bx0,by0,bx1,by1=physical_bounds(ink);tx0,ty0,tx1,ty1=physical_bounds(target);sx=(tx1-tx0)/(bx1-bx0);sy=(ty1-ty0)/(by1-by0);x=tx0-bx0*sx;y=ty0-by0*sy
 # Only opacity is fitted to the UI after fixing its physical camera.
 xlo=max(0,tx0-8);xhi=min(1920,tx1+8);ylo=max(0,ty0-8);yhi=min(1080,ty1+8);ys,xs=np.mgrid[ylo:yhi:1,xlo:xhi:1];truth=target[ylo:yhi:1,xlo:xhi:1];samp=ndimage.map_coordinates(ink,[(ys-y)/sy,(xs-x)/sx],order=1,mode='constant',cval=0);opacity=float(np.clip((truth*samp).sum()/max((samp*samp).sum(),1),0,1));loss=float(np.mean((truth-opacity*samp)**2))
 if n==891:x,y,sx,sy,opacity,loss=772.,165.,1.,1.,1.,0.
 poses.append({'frame':n,'x':float(x),'y':float(y),'scaleX':float(sx),'scaleY':float(sy),'opacity':float(opacity),'fitMSE':loss,'physicalBounds':[tx0,ty0,tx1,ty1]})

keys={p:[{'t':r['frame']/30,'value':r[p]} for r in poses] for p in ['x','y','scaleX','scaleY','opacity']}
layer={'id':'root-google-phone-exit','type':'image','src':str(asset),'width':375,'height':749,'start':891/30,'end':899/30,'keyframes':keys,'sourceFrame':891,'semanticText':'Google sign-in phone shrinking and fading','editability':'One bounded original product phone artwork. Native independent camera and opacity; bitmap hardware/UI internals, not live text.'}
spec={'scope':[[891,898]],'layer':layer,'poses':poses,'assetBounds':[772,165,1147,914],'notice':'One original bounded phone image with measured scale/position/opacity. Phone is tiny and faint, but still present at898.'};(REF/'root-google-exit-patch.json').write_text(json.dumps(spec,indent=2));print(poses)
