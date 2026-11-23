from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import label,find_objects
p=Path(__file__).parent
a=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
data={f:(x,y,w,h) for f,x,y,w,h,*_ in json.loads((p/'project/scene.json').read_text())['tracks']['followPointerStage']}
for f in [670,675,678,680,685,688,691,694,695]:
 x,y,w,h=data[f]
 print(f,data[f])
 for r in (a,b):
  d=np.asarray(Image.open(r/f'{f:06}.png').convert('L'))
  x0,y0=round(x)-11,round(y)-8
  crop=d[y0:round(y+h)+19,x0:round(x+w+24)]
  ll,n=label(crop<128)
  # Choose the component under the arrow belly, away from the click control.
  m=(round(y+h*.49)-y0, round(x+w*.34)-x0)
  idx=ll[m]
  if idx==0:
   print('miss'); continue
  j,i=np.where(ll==idx)
  lo,top,hi,bottom=i.min(),j.min(),i.max(),j.max()
  print((int(lo+x0),int(top+y0),int(hi+x0),int(bottom+y0)),
        int(np.percentile(crop[ll==idx],10)),float(np.mean(crop[ll==idx]<45)),len(i),
        [(round(fy,2), (round((min(ii)-lo)/max(1,hi-lo),2),round((max(ii)-lo)/max(1,hi-lo),2))) for fy in (.15,.30,.45,.55,.59,.65,.72,.78,.84,.92,.97)
         if len(ii:=np.flatnonzero(ll[round(top+fy*(bottom-top))]==idx))])
