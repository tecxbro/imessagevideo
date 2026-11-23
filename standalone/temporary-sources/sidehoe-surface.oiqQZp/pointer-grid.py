from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
import sys
p=Path(__file__).parent
a=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
c=p/'probes'
keys=json.loads((p/'project/scene.json').read_text())['tracks']['followPointerStage']
data={f:(x,y,w,h) for f,x,y,w,h,*_ in keys}
frames=[670,673,675,677,680,685,688,691,695]
label=['source','previous','revised']
roots=[a,b]+([c] if c.is_dir() else [])
sheet=Image.new('RGB',(270*len(roots),188*len(frames)),'white')
d=ImageDraw.Draw(sheet)
for j,f in enumerate(frames):
 x,y,w,h=data[f]
 box=tuple(map(round,(x-22,y-16,x+82,y+72)))
 for i,r in enumerate(roots):
  img=Image.open(r/f'{f:06}.png').convert('RGB').crop(box)
  img=img.resize((260,167))
  sheet.paste(img,(i*270,j*188+18))
  d.text((i*270+6,j*188+1),f'{f} {label[i]}',fill='black')
sheet.save(p/'pointer-grid.jpg',quality=92)
