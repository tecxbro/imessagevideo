from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,sys
p=Path(__file__).parent;sys.path.insert(0,str(p.parents[1]/'engines'));from render_pillow import state
s=json.loads((p/'final-v13.scene.json').read_text());physical=next(x for x in s['layers'] if x['id']=='measured-lunch-device-v13');records=[]
for f in range(730,735):
 a=np.array(Image.open(p/'lunch-native'/f'{f-609:03}.png'));q=state(physical,f/30);sx=q['scaleX'];sy=q['scaleY'];x0=max(0,round(q['x']+35*sx));x1=min(1920,round(q['x']+767*sx));y0=max(0,round(q['y']+30*sy));y1=min(1080,round(q['y']+1630*sy));roi=a[y0:y1,x0:x1];m=(roi.min(2)>242)&(roi.max(2)-roi.min(2)<8);l,n=ndimage.label(m);c=[]
 for j,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  yy,xx=b;w=xx.stop-xx.start;h=yy.stop-yy.start;area=int((l[b]==j).sum());cx=x0+(xx.start+xx.stop)/2
  if w>20 and h>50 and h/w>.9 and area>500 and abs(cx-960)<90:c.append((area,[x0+xx.start,y0+yy.start,x0+xx.stop,y0+yy.stop]))
 c.sort(reverse=True);b=c[0][1] if c else None
 if b:
  scale=(b[2]-b[0]+1)/742;scale_y=(b[3]-b[1]+1)/1320;x=b[0]-29*scale;y=b[1]-310*scale_y
 else:scale=scale_y=x=y=None
 # Sample the neutral exposed Messages-page margin, away from the widget.
 points=[]
 for xx in [x0+8,x1-9]:
  for yy in range(max(y0+30,100),min(y1-30,950),20):
   rgb=a[yy,xx];v=float(rgb.mean())
   if rgb.max()-rgb.min()<4 and 130<v<248:points.append(v)
 gray=float(np.median(points)) if points else 241;extra=float(np.clip(1-(gray/253)/(1-.04743083003952569),0,1));records.append({'frame':f,'t':f/30,'white_panel_box':b,'semantic_span':'Bright connected body after header divider, native y310..1630; not the full pane.','x':x,'y':y,'scale':scale,'scaleY':scale_y,'background_gray':gray,'extra_dim':extra,'physical_inner_bounds':[x0,y0,x1,y1]})
(p/'menu-close-v14-measurements.json').write_text(json.dumps(records,indent=2));print(records)
