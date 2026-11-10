"""Measure independent favorite-avatar and phone poses at exact pullback frames."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;rows=[];avatar_images={name:np.array(Image.open(p/f'assets/{name}.png').convert('RGB'))for name in ['braden','sydney']};logo_boxes={}
for name in ['poke-circle','poke-square']:
 logo=np.array(Image.open(p/f'assets/{name}.png').convert('RGB').resize((476,476),Image.Resampling.LANCZOS)).astype(int);mask=(logo[:,:,2]-logo[:,:,0]>20)&(logo[:,:,2]-logo[:,:,1]>0)&(logo[:,:,0]<150);yy,xx=np.where(mask);logo_boxes[name]=[int(xx.min()-238),int(yy.min()-238),int(xx.max()+1-238),int(yy.max()+1-238)]
def largest(mask,predicate):
 labels,_=ndimage.label(mask);choices=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  y,x=sl;box=[x.start,y.start,x.stop,y.stop];w,h=x.stop-x.start,y.stop-y.start
  if predicate(box,w,h):choices.append((int((labels[sl]==i).sum()),box))
 return max(choices)[1]if choices else None
for n in range(2,142):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int);r={'frame':n,'time':n*1001/30000}
 blue=(a[:,:,2]-a[:,:,0]>20)&(a[:,:,2]-a[:,:,1]>0)&(a[:,:,0]<150);blue[900:]=False
 labels,_=ndimage.label(blue);parts=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl;area=int((labels[sl]==i).sum())
  if area>500 and 550<(xx.start+xx.stop)/2<900:parts.append([xx.start,yy.start,xx.stop,yy.stop])
 r['poke_bbox']=[min(b[0]for b in parts),min(b[1]for b in parts),max(b[2]for b in parts),max(b[3]for b in parts)]if parts else None
 if r['poke_bbox']:
  b=r['poke_bbox'];kind='poke-circle'if n<73 else'poke-square';lb=logo_boxes[kind];scale=(b[2]-b[0])/(lb[2]-lb[0]);x=b[0]-lb[0]*scale;y=b[3]-lb[3]*scale if b[3]-b[1]<.85*(b[2]-b[0])else b[1]-lb[1]*scale;r['poke_pose']={'x':x,'y':y,'scale':scale,'occluded_top':b[3]-b[1]<.85*(b[2]-b[0])}
 warm=(a[:,:,0]-a[:,:,2]>(2 if n<109 else 5))&(a[:,:,0]-a[:,:,1]>(.5 if n<109 else 2));warm[:,450:]=False;warm[850:]=False
 cool=(a[:,:,2]-a[:,:,0]>(.5 if n<109 else 2))&(a[:,:,2]-a[:,:,1]>-2);cool[:,:980]=False;cool[850:]=False
 predicate=lambda b,w,h:70<h<550 and 20<w<550
 r['braden_bbox']=largest(warm,predicate);r['sydney_bbox']=largest(cool,predicate)
 for name in ['braden','sydney']:
  b=r[name+'_bbox']
  if not b:continue
  left,top,right,bottom=b;h=bottom-top;cy=(top+bottom)/2
  if left==0:cx=right-h/2
  elif name=='braden'and right==450:cx=left+h/2
  elif name=='sydney'and left==980:cx=right-h/2
  elif right>=1438:cx=left+h/2
  else:cx=(left+right)/2
  ratios=[];asset=avatar_images[name];ah,aw=asset.shape[:2]
  for theta in np.linspace(0,2*np.pi,80,endpoint=False):
   sx=round(cx+.83*h/2*np.cos(theta));sy=round(cy+.83*h/2*np.sin(theta));tx=round(aw/2+.83*aw/2*np.cos(theta));ty=round(ah/2+.83*ah/2*np.sin(theta))
   if 0<=sx<1440 and 0<=sy<1080:
    source_delta=255-a[sy,sx];target_delta=255-asset[ty,tx].astype(int);valid=target_delta>30;ratios.extend((source_delta[valid]/target_delta[valid]).tolist())
  r[name+'_pose']={'x':cx,'y':cy,'scale':h/274,'opacity':float(np.clip(np.median(ratios),0,1))if ratios else 0}
 rows.append(r)
(p/'measurements-v8/intro-pose-fit.json').write_text(json.dumps({'method':'Individual genuine avatar/logo bounds; independent component cameras, exact source frames2–131. Portrait centers use the fully visible vertical diameter when a horizontal edge is clipped. Portrait opacity uses median linear RGB deficit on the authentic asset background annulus.','measurements':rows},indent=2))
for r in rows[::5]:print(r)
