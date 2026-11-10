from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
p=Path(__file__).parent;rows=[]
for f in range(610,801):
 a=np.array(Image.open(p/'lunch-native'/f'{f-609:03}.png'));r=a.astype('int16');mask=(r[:,:,2]>210)&(r[:,:,1]>100)&(r[:,:,0]<110)&(r[:,:,1]/np.maximum(r[:,:,2],1)>.55);l,n=ndimage.label(mask);c=[]
 for label,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  yy,xx=b;w=xx.stop-xx.start;h=yy.stop-yy.start
  if xx.start<1050 or w<15 or h<15 or not .8<w/h<1.25:continue
  count=np.count_nonzero(l[b]==label)
  if count/(w*h)<.55:continue
  c.append({'box':[xx.start,yy.start,xx.stop,yy.stop],'cx':(xx.start+xx.stop)/2,'cy':(yy.start+yy.stop)/2,'diameter':(w+h)/2,'pixels':int(count)})
 c.sort(key=lambda x:-x['diameter']);rows.append({'frame':f,'t':f/30,'check':c[0] if c else None})
(p/'menu-v13-measurements.json').write_text(json.dumps(rows,indent=2));print([r for r in rows if r['frame'] in [618,619,620,621,624,630,640,651,666,700,729,730,731,732,733,734,735]])
