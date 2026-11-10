"""Original early message body registration; separate static silhouette and camera."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
from v10_shape_trace import vector_outline
p=Path(__file__).parent;rows=[]
for frame in range(547,579):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{frame:06}.png').convert('RGB'));crop=a[620:1080,100:1100].astype(float);m=(crop.max(2)<244)&(crop.min(2)>232)&((crop.max(2)-crop.min(2))<5);lab,_=ndimage.label(m);choices=[]
 for i,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start;area=int((lab[sl]==i).sum())
  if w>500 and h>35 and area>12000:choices.append((area,i,[xx.start+100,yy.start+620,xx.stop+100,yy.stop+620]))
 choices.sort(reverse=True)
 if not choices:rows.append(dict(frame=frame,status='No coherent gray found-body in bounded nativeROI; not proof of absence'));continue
 _,i,b=choices[0];mask=ndimage.binary_fill_holes(lab==i);ys,xs=np.where(mask);rows.append(dict(frame=frame,status='coherent_original_graybody',body_bounds=b,side_censored=b[0]==100 or b[2]==1100,bottom_censored=b[3]==1080,pixels=int(mask.sum())))
 if frame==569:
  # Crop below map; graybody tail belongs to this isolated connected component.
  origin=[b[0],b[1]];shape=vector_outline(mask,(100,620,0,0),origin,1);(p/'measurements-v8/found-early-outline-v17.json').write_text(json.dumps(dict(frame=frame,body_bounds=b,source_origin=origin,d=shape,method='Original569 uniform graybody, black text filled as interior, single editable static vector path; no UI bitmap.'),indent=2))
(p/'measurements-v8/found-early-camera-v17.json').write_text(json.dumps(dict(method='Original native547–578 graycomponent under stated size/palette/ROI gates; components are observations, with censored edges explicitly retained. First missing observation alone is not a lifecycle gate.',records=rows),indent=2));print(rows)
