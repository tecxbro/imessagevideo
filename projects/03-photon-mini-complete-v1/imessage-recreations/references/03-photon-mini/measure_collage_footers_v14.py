from pathlib import Path
import json
import numpy as np
from scipy import ndimage
from PIL import Image
p=Path(__file__).parent

def footers(a):
 rgb=a.astype('int16');mask=(rgb.max(2)-rgb.min(2)<12)&(rgb.mean(2)>222)&(rgb.mean(2)<237);mask=ndimage.binary_erosion(mask,iterations=2);l,n=ndimage.label(mask);out=[]
 for i,box in enumerate(ndimage.find_objects(l),1):
  if box is None:continue
  y,x=box;w=x.stop-x.start;h=y.stop-y.start;area=int((l[box]==i).sum())
  if w>75 and h>10 and w/h>2.5 and area>800:
   out.append({'box':[max(0,x.start-2),max(0,y.start-2),min(1920,x.stop+2),min(1080,y.stop+2)],'area':area,'aspect':w/h})
 return sorted(out,key=lambda r:r['box'][1])
rows=[]
for i,f in enumerate(sorted((p/'collage-native').glob('*.png'))):
 a=np.array(Image.open(f).convert('RGB'));rows.append({'frame':891+i,'t':(891+i)/30,'footers':footers(a)})
(p/'collage-v14-footer-measurements.json').write_text(json.dumps(rows,indent=2));print(json.dumps([r for r in rows if r['frame'] in [900,904,915,930,941,956,960]],indent=2))
