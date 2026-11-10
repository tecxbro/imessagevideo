from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';s=json.loads((D/'scene-menu-middle-v11.json').read_text());poses=json.loads((D/'menu-v11-poses.json').read_text());old=next(q for q in s['layers'] if q['id']=='g-119');orig={q['id']:q for q in old['children']};chrome=orig['v11-menu-chrome'];rows=orig['v11-menu-document-viewport']['children'][0]['children'];ref=np.array(Image.open(F/'000108.png').convert('RGB')).astype(np.float32);art=ref[518:614,194:509]
# Monotonic camera prior prevents motion-blurred circle bounds from falsely
# shrinking the whole sheet at113–115.
for p in poses:
 a=np.array(Image.open(F/f"{p['frame']:06}.png").convert('RGB')).astype(np.float32)
 if p['frame'] in [113,114,115,116,117]:
  sc={113:1.075,114:1.087,115:1.096,116:1.103,117:1.103}[p['frame']];x=264*(1-sc);cy=p['docY']+p['scale']*565;y=cy-sc*565;wy,wx=np.mgrid[max(0,int(cy-85)):min(720,int(cy+85)):2,170:570:2];target=np.stack([map_coordinates(a[:,:,c],[wy,wx],order=1) for c in range(3)],2)
  def residual(v):
   y,bx,by,alpha=v;ar=gaussian_filter(art,(by/sc,bx/sc,0),mode='constant',cval=255);coords=[(wy-y)/sc-518,(wx-x)/sc-194];pred=np.stack([map_coordinates(ar[:,:,c],coords,order=1,mode='constant',cval=255) for c in range(3)],2);return ((255-alpha*(255-pred))-target).ravel()/255
  fit=least_squares(residual,[y,p['blurX'],p['blurY'],p['opacity']],bounds=([y-30,0,0,.05],[y+30,15,35,1.1]),max_nfev=45,diff_step=.005);y,bx,by,alpha=map(float,fit.x);p.update(scale=sc,x=x,docY=y,blurX=bx,blurY=by,opacity=min(1,alpha))
 # Measure true viewport rails independently; its zoom differs slightly from
 # the optically resampled content scale.
 sc=p['scale'];tx=p['x'];centerY=p['cardY']+344*sc;ys=slice(max(0,int(centerY)-16),min(720,int(centerY)+17));prof=a[ys].mean((0,2));leftPred=tx+126*sc;rightPred=tx+784*sc
 def bound(pred):
  lo=max(0,round(pred)-25);hi=min(960,round(pred)+26);return float(lo+np.argmin(prof[lo:hi]))
 left=bound(leftPred);right=bound(rightPred);sx=(right-left)/658;cx=left-126*sx;xq=round(left+(right-left)*.82);yp=a[:,max(0,xq-10):min(960,xq+11)].mean((1,2))
 topPred=p['cardY']+38*sc;bottomPred=p['cardY']+650*sc
 def edge(pred):
  lo=max(0,round(pred)-28);hi=min(720,round(pred)+29)
  if hi<=lo:return float(np.clip(pred,0,719))
  return float(lo+np.argmin(yp[lo:hi]))
 top=edge(topPred);bottom=edge(bottomPred)
 if bottom-top<60:top=topPred;bottom=bottomPred
 sy=(bottom-top)/612;cy=top-38*sy;p.update(cardScaleX=sx,cardScaleY=sy,cardX=cx,cardY=cy)
# Native transform cancellation implements directional Gaussian blur without
# source-frame assets: inverse-stretch static rows, blur, stretch back.
ps=[p for p in poses if p['frame']<=126]
def track(fn):return [dict(t=p['frame']/30,value=float(fn(p)),ease='linear') for p in ps]
chrome.pop('keyframes',None);chrome['y']=15
chromeG=dict(type='group',id='v11-menu-chrome-camera',children=[chrome],keyframes={'x':track(lambda p:p['cardX']),'y':track(lambda p:p['cardY']),'scaleX':track(lambda p:p['cardScaleX']),'scaleY':track(lambda p:p['cardScaleY']),'opacity':track(lambda p:p['opacity'] if p['frame']>=125 else 1),'blur':track(lambda p:min(p['blurX'],p['blurY'])/max(p['cardScaleX'],.1) if p['frame']<106 else .25)})
ratio=lambda p:max(.05,p['blurY'])/max(.05,p['blurX'])
inverse=dict(type='group',id='v11-menu-blur-inverse',children=rows,keyframes={'scaleY':track(lambda p:1/ratio(p))})
blurred=dict(type='group',id='v11-menu-directional-blur',children=[inverse],keyframes={'scaleY':track(ratio),'blur':track(lambda p:max(.05,p['blurX'])/p['scale'])})
doc=dict(type='group',id='v11-menu-native-scroll',children=[blurred],keyframes={'x':track(lambda p:(p['x']-p['cardX'])/p['cardScaleX']),'y':track(lambda p:(p['docY']-p['cardY'])/p['cardScaleY']),'scaleX':track(lambda p:p['scale']/p['cardScaleX']),'scaleY':track(lambda p:p['scale']/p['cardScaleY']),'opacity':track(lambda p:p['opacity'])})
viewport=dict(type='group',id='v11-menu-viewport-camera',clip={'x':126,'y':38,'width':658,'height':612,'radius':83},children=[doc],keyframes={k:v for k,v in chromeG['keyframes'].items() if k in ['x','y','scaleX','scaleY']})
old['children']=[chromeG,viewport];old['keyframes']={};old['x']=old['y']=0
(D/'menu-v11-final-poses.json').write_text(json.dumps(poses,indent=2));(D/'scene-menu-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n');print('wrote',len(poses))
