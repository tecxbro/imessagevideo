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
 scale=(yy.stop-yy.start)/733;px=960-187.5*scale;py=540-374.5*scale
 # Optimize a rigid camera; source visible material gets fainter against #fdfdfd.
 xlo=max(0,xx.start-10);xhi=min(1920,xx.stop+10);ylo=max(0,yy.start-10);yhi=min(1080,yy.stop+10);ys,xs=np.mgrid[ylo:yhi:2,xlo:xhi:2];truth=target[ylo:yhi:2,xlo:xhi:2]
 def evaluate(q,ret=False):
  x,y,sx,sy=q;samp=ndimage.map_coordinates(ink,[(ys-y)/sy,(xs-x)/sx],order=1,mode='constant',cval=0);alpha=float(np.clip((truth*samp).sum()/max((samp*samp).sum(),1),0,1));loss=float(np.mean((truth-alpha*samp)**2));return (loss,alpha) if ret else loss
 start=[px,py,scale,scale];bounds=[(px-12,px+12),(py-12,py+12),(.85*scale,1.15*scale),(.85*scale,1.15*scale)];fit=optimize.minimize(evaluate,start,method='Powell',bounds=bounds,options={'maxiter':70,'xtol':.0002,'ftol':.00001});x,y,sx,sy=fit.x;loss,opacity=evaluate(fit.x,True)
 if n==891:x,y,sx,sy,opacity=772.,165.,1.,1.,1.
 poses.append({'frame':n,'x':float(x),'y':float(y),'scaleX':float(sx),'scaleY':float(sy),'opacity':float(opacity),'fitMSE':loss})
keys={p:[{'t':r['frame']/30,'value':r[p]} for r in poses] for p in ['x','y','scaleX','scaleY','opacity']}
layer={'id':'root-google-phone-exit','type':'image','src':str(asset),'width':375,'height':749,'start':891/30,'end':899/30,'keyframes':keys,'sourceFrame':891,'semanticText':'Google sign-in phone shrinking and fading','editability':'One bounded original product phone artwork. Native independent camera and opacity; bitmap hardware/UI internals, not live text.'}
spec={'scope':[[891,898]],'layer':layer,'poses':poses,'assetBounds':[772,165,1147,914],'notice':'One original bounded phone image with measured scale/position/opacity. Phone is tiny and faint, but still present at898.'};(REF/'root-google-exit-patch.json').write_text(json.dumps(spec,indent=2));print(poses)
