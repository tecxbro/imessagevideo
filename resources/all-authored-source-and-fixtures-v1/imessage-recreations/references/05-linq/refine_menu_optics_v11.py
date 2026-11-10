from pathlib import Path
import json,math,copy
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';s=json.loads((D/'scene-menu-middle-v11.json').read_text());p=json.loads((D/'menu-v11-final-poses.json').read_text());g=next(q for q in s['layers'] if q['id']=='g-119');chrome,viewport=g['children'];doc=viewport['children'][0];rows=doc['children'][0]['children'][0]['children'];ps=[q for q in p if q['frame']<=126]
for q in ps:
 a=np.array(Image.open(F/f"{q['frame']:06}.png").convert('RGB')).astype(float);left=126*q['cardScaleX']+q['cardX'];xq=round(left+658*q['cardScaleX']*.82);profile=a[:,xq-10:xq+11].mean((1,2));grad=np.gradient(gaussian_filter1d(profile,1.2))
 topPred=q['cardY']+38*q['cardScaleY'];bottomPred=q['cardY']+650*q['cardScaleY']
 if q['frame']>=110:
  topPred=13+25*math.exp(-(q['frame']-108)/2.7);bottomPred=650+47*(1-math.exp(-(q['frame']-108)/3))
 def edge(pred):
  lo=max(1,round(pred)-20);hi=min(719,round(pred)+21);return float(lo+np.argmin(grad[lo:hi]))
 top=edge(topPred);bottom=edge(bottomPred);q['cardScaleY']=(bottom-top)/612;q['cardY']=top-38*q['cardScaleY']
 # Plain native background before motion settles; the original drawer is
 # visibly gray while its zoom shutter is open.
 xx=round(q['cardX']+600*q['cardScaleX']);yy=round(q['cardY']+300*q['cardScaleY']);v=np.median(a[max(0,yy-4):min(720,yy+5),max(0,xx-4):min(960,xx+5)],axis=(0,1));q['cardFill']='#'+''.join(f'{int(z):02x}' for z in v)
def key(fn):return [dict(t=q['frame']/30,value=fn(q),ease='linear') for q in ps]
for layer in [chrome,viewport]:
 layer['keyframes'].update(y=key(lambda q:q['cardY']),scaleY=key(lambda q:q['cardScaleY']))
doc['keyframes']['y']=key(lambda q:(q['docY']-q['cardY'])/q['cardScaleY']);doc['keyframes']['scaleY']=key(lambda q:q['scale']/q['cardScaleY'])
# Clear the tiny piece of original border inadvertently present below the
# last source UI row; the native viewport supplies its own boundary.
star=next(q for q in rows if q['id']=='v11-menu-row-StarFlights');im=Image.open(star['src']).convert('RGBA');ar=np.array(im);ar[-5:,:,3]=0;Image.fromarray(ar).save(star['src'])
fill=dict(type='rect',id='v11-menu-native-background',x=126,y=38,width=658,height=612,radius=83,keyframes={'fill':key(lambda q:q['cardFill'])})
chrome['children'].insert(0,fill)
# At101–105 the blur is from a zoom, so each menu row has its own velocity;
# treating every row as the Store icon's blur left the upper labels too sharp.
wrappers=[]
for row in rows:
 cx=row['x']+row['width']/2;cy=row['y']+row['height']/2;ks=[]
 for j,q in enumerate(ps):
  bx=q['blurX'];by=q['blurY'];angle=90.;long=max(.05,by);short=max(.05,bx)
  if q['frame']<=105:
   prev=ps[max(0,j-1)]
   if q['frame']==102:prev=ps[0]
   ds=q['scale']-prev['scale'];vx=q['x']-prev['x']+cx*ds;vy=q['docY']-prev['docY']+cy*ds
   if q['frame']==102:vx=0;vy=0
   long=max(4,math.hypot(vx,vy)*.31);short=1.6;angle=math.degrees(math.atan2(vy,vx));
  ks.append((q,angle,long/q['scale'],short/q['scale']))
 invR=dict(type='group',id=row['id']+'-inverse-rotation',children=[row],keyframes={'rotation':[dict(t=q['frame']/30,value=-a) for q,a,l,sh in ks]})
 invS=dict(type='group',id=row['id']+'-inverse-stretch',children=[invR],keyframes={'scaleX':[dict(t=q['frame']/30,value=1/l) for q,a,l,sh in ks],'scaleY':[dict(t=q['frame']/30,value=1/sh) for q,a,l,sh in ks]})
 blur=dict(type='group',id=row['id']+'-zoom-shutter',blur=1,children=[invS],keyframes={'rotation':[dict(t=q['frame']/30,value=a) for q,a,l,sh in ks],'scaleX':[dict(t=q['frame']/30,value=l) for q,a,l,sh in ks],'scaleY':[dict(t=q['frame']/30,value=sh) for q,a,l,sh in ks]});wrappers.append(blur)
doc['children']=wrappers
(D/'menu-v11-optics-poses.json').write_text(json.dumps(ps,indent=2));(D/'scene-menu-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n')
