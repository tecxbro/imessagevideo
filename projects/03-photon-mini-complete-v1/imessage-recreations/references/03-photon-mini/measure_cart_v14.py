from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
p=Path('/workspace/imessage-recreations/references/03-photon-mini');out=[]
for f in range(664,731):
 a=np.array(Image.open(p/'lunch-native'/f'{f-609:03}.png').convert('RGB').crop((1290,50,1500,900)));r=a.astype('int16');m=(r.max(2)-r.min(2)<10)&(r.mean(2)>220)&(r.mean(2)<249);z=ndimage.binary_closing(m,structure=np.ones((3,3)));lab,n=ndimage.label(z);c=[]
 for i,b in enumerate(ndimage.find_objects(lab),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start;area=int((lab[b]==i).sum())
  if w>15 and h>15 and area>140 and 1<w/h<2:c.append({'bbox':[x.start+1290,y.start+50,x.stop+1290,y.stop+50],'area':area,'w':w,'h':h})
 c.sort(key=lambda q:q['area'],reverse=True);out.append({'frame':f,'candidates':c,'chosen':c[0] if c else None})
(p/'cart-v14-measurements.json').write_text(json.dumps(out,indent=2))
for r in out:
 if r['frame']<680 or r['frame']>724:print(r)
