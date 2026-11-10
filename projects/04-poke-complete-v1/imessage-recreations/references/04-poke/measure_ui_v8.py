"""Independent keyboard/chat/composer measurements; no shared camera assumption."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;existing=json.loads((p/'measurements-v8/component-tracks.json').read_text())['measurements'];prior={r['frame']:r for r in existing};rows=[]
def components(mask):
 labels,_=ndimage.label(mask);out=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
  if w>200 and h>2:out.append({'bbox':[xx.start,yy.start,xx.stop,yy.stop],'area':int((labels[sl]==i).sum()),'width':w,'height':h})
 return out
def ink(a,roi,predicate):
 x,y,x2,y2=roi;c=a[y:y2,x:x2];yy,xx=np.where(predicate(c))
 return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)]if len(xx)>20 else None
for n in list(range(345,552))+list(range(719,830)):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));c=a.astype(int);r={'frame':n,'time':n*1001/30000}
 if n<552:
  chats=components(np.abs(c-[236,236,236]).max(2)<5);r['chat_bubbles']=[v['bbox']for v in chats if v['width']>300 and v['height']>65]
  km=(c.min(2)>200)&(c.max(2)<239)&(c[:,:,2]-c[:,:,0]>=2)&(c[:,:,2]-c[:,:,0]<11)&(np.abs(c[:,:,0]-c[:,:,1])<4);choices=[v for v in components(km)if v['bbox'][3]>=1078 and v['width']>400];kb=max(choices,key=lambda v:v['area'])['bbox']if choices else None
 else:kb=prior[n].get('keyboard_bbox')
 r['keyboard_bbox']=kb
 if kb:
  x,y,x2,y2=kb;scale=(x2-x)/1109;roi=(max(0,round(x+180*scale)),max(0,round(y-140*scale)),min(1440,round(x+800*scale)),min(1080,round(y-25*scale)))
  if roi[2]>roi[0]and roi[3]>roi[1]:r['composer_ink_bbox']=ink(a,roi,lambda z:(z.min(2)>150)&(z.max(2)<211)&(z.max(2)-z.min(2)<8))
  if n<552:
   roi=(round(x+.3*(x2-x)),y+5,round(x+.7*(x2-x)),min(1080,y+125));r['location_header_ink_bbox']=ink(a,roi,lambda z:z.max(2)<150)
 rows.append(r)
(p/'measurements-v8/ui-camera-tracks.json').write_text(json.dumps({'method':'Exclusive native component bounds. Keyboard body, gray chat bubbles and composer phrase measured separately; composer ROI follows the measured keyboard solely to isolate its text, not to derive its camera.','measurements':rows},indent=2))
for n in [435,450,456,480,492,719,779,799,810,819]:print(next(r for r in rows if r['frame']==n))
