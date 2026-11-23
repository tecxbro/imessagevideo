from pathlib import Path
from PIL import Image,ImageDraw
import sys
import numpy as np
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-light.sqaBVz/final-frames')
new=p/sys.argv[1]
for f in range(41,67):
 values=[np.array(Image.open(b/f'{f:06}.png').convert('RGB'),dtype=np.int16) for b in (src,old,new)]
 b,a=[np.abs(values[0]-x) for x in values[1:]]
 print(f,round(b.mean(),5),round(a.mean(),5))
for n,frames in enumerate(((42,45,48,52),(54,58,61,64))):
 tile=Image.new('RGB',(1080,809),'white')
 d=ImageDraw.Draw(tile)
 for i,f in enumerate(frames):
  for j,dir in enumerate((src,old,new)):
   im=Image.open(dir/f'{f:06}.png').convert('RGB').resize((265,247),Image.Resampling.LANCZOS)
   tile.paste(im,(i*270,j*270+20))
   d.text((i*270+4,j*270+2),f'{f} {("source","previous","test")[j]}',fill='black')
 tile.save(p/f'{sys.argv[1]}-{n}.jpg',quality=92)
