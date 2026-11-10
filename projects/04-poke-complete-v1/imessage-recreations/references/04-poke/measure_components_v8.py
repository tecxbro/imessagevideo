"""Measure independent physical/UI camera evidence in audited transition intervals."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;decoded=p/'measurements-v8/decoded';fps=30000/1001

def boxes(mask,minimum_area=10):
 labels,_=ndimage.label(mask);out=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  y,x=sl;area=int((labels[sl]==i).sum())
  if area>=minimum_area:out.append({'bbox':[x.start,y.start,x.stop,y.stop],'area':area,'width':x.stop-x.start,'height':y.stop-y.start})
 return out
def largest(mask,predicate=lambda q:True):
 rows=[q for q in boxes(mask,100)if predicate(q)]
 return max(rows,key=lambda q:q['area'])['bbox']if rows else None
def ink(a,roi,maskfn):
 x,y,x2,y2=roi;c=a[y:y2,x:x2];m=maskfn(c);yy,xx=np.where(m)
 return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)]if len(xx)>5 else None
measurements=[]
for file in sorted(decoded.glob('*.png')):
 n=int(file.stem)
 if not(435<=n<=492 or 575<=n<=596 or 660<=n<=669 or 695<=n<=829 or 250<=n<=264 or 98<=n<=131):continue
 a=np.array(Image.open(file).convert('RGB'));c=a.astype(int);d={'frame':n,'time':n/fps,'border_rgb':np.median(np.r_[a[:,:20].reshape(-1,3),a[:,-20:].reshape(-1,3)],axis=0).tolist()}
 # The physical device is a separate camera from Messages content.
 dark=boxes(a.max(2)<110,100);tall=[v for v in dark if v['height']>300 and v['width']>2]
 if tall:d['physical_device_bbox']=[min(v['bbox'][0]for v in tall),min(v['bbox'][1]for v in tall),max(v['bbox'][2]for v in tall),max(v['bbox'][3]for v in tall)]
 blue=(c[:,:,2]-c[:,:,0]>20)&(c[:,:,2]-c[:,:,1]>0)&(c[:,:,0]<150);blue[900 if n<132 else 450:]=False
 d['header_blue_bbox']=largest(blue,lambda q:q['width']>40 and q['height']>30 and .6<q['width']/q['height']<1.6)
 if n<132:
  warm=(c[:,:,0]-c[:,:,2]>5)&(c[:,:,0]-c[:,:,1]>2);warm[:,650:]=False;warm[850:]=False
  cool=(c[:,:,2]-c[:,:,0]>2)&(c[:,:,2]-c[:,:,1]>-5);cool[:,:800]=False;cool[850:]=False
  d['braden_bbox']=largest(warm,lambda q:70<q['height']<550 and 20<q['width']<550)
  d['sydney_bbox']=largest(cool,lambda q:70<q['height']<550 and 20<q['width']<550)
 # Keyboard excludes gray chat bubbles (zero chroma) and map footer (negative B−R).
 km=(c.min(2)>200)&(c.max(2)<239)&(c[:,:,2]-c[:,:,0]>=2)&(c[:,:,2]-c[:,:,0]<11)&(np.abs(c[:,:,0]-c[:,:,1])<4)
 d['keyboard_bbox']=largest(km,lambda q:q['bbox'][3]>=1078 and q['width']>400 and q['height']>30)
 # Footer and distance bubble use different native flat colors; keep their cameras independent.
 d['map_footer_bbox']=largest(np.abs(c-[227,227,224]).max(2)<5,lambda q:q['width']>200 and q['width']>q['height']*1.3)
 d['distance_bbox']=largest(np.abs(c-[236,236,236]).max(2)<5,lambda q:q['width']>200 and q['width']>q['height']*2)
 am=(c[:,:,0]>120)&(c[:,:,0]<210)&(c[:,:,1]-c[:,:,0]>1)&(c[:,:,1]-c[:,:,0]<10)&(c[:,:,2]-c[:,:,0]>7)&(c[:,:,2]-c[:,:,0]<25)
 d['audio_bbox']=largest(am,lambda q:q['width']>200 and 1.8<q['width']/q['height']<3.5)
 d['composer_ink_bbox']=ink(a,(330,650,1100,1035),lambda z:(z.min(2)>150)&(z.max(2)<211)&(z.max(2)-z.min(2)<8))
 # Header row is denser than restaurant row names; use its native glyph top as a ruler.
 if 575<=n<=596 or 663<=n<=669:
  black=a[:,280:1150].max(2)<80;density=np.convolve(black.sum(1),np.ones(20),'same');center=int(density.argmax());lo=max(0,center-28);hi=min(1080,center+29)
  if density[center]>1600:d['restaurant_header_ink_bbox']=ink(a,(280,lo,1150,hi),lambda z:z.max(2)<80)
 if 435<=n<=492:
  # Physical side rails at a clean scan line, independent of keyboard/content camera.
  row=a[500].max(1)<80;runs=[]
  for x in np.where(row)[0]:
   if runs and x==runs[-1][-1]+1:runs[-1].append(int(x))
   else:runs.append([int(x)])
  left=[v for v in runs if len(v)>4 and v[-1]<160];right=[v for v in runs if len(v)>4 and v[0]>1280]
  d['physical_left_inner']=max(v[-1]for v in left)+1 if left else None;d['physical_right_inner']=min(v[0]for v in right)if right else None
  kb=d['keyboard_bbox']
  if kb:d['location_header_ink_bbox']=ink(a,(max(0,kb[0]+200),kb[1]+5,min(1440,kb[2]-100),min(1080,kb[1]+125)),lambda z:z.max(2)<100)
 measurements.append(d)
(p/'measurements-v8/component-tracks.json').write_text(json.dumps({'cadence':'30000/1001','bounds':'exclusive x1,y1,x2,y2; separate measured component cameras, not a shared blind transform','measurements':measurements},indent=2))
for n in [109,259,450,456,480,583,664,710,719,779,784,799,810,819]:
 row=next((r for r in measurements if r['frame']==n),None)
 if row:print(n,{k:v for k,v in row.items()if k not in ['frame','time']})
