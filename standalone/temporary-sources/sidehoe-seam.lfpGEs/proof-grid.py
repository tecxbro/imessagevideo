from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
before=Path('/tmp/sidehoe-surface.oiqQZp/final-frames')
for name,frames in [('sofia',[337,339,340,341,342]),('calendar',[397,399,400,401,402])]:
 im=Image.new('RGB',(1230,360*len(frames)),'white')
 d=ImageDraw.Draw(im)
 for j,f in enumerate(frames):
  box=(88,0,920,1000) if name=='sofia' else (90,50,990,1000)
  for i,(stage,label) in enumerate(zip((src,before,p/name),('source','previous','revised'))):
   a=Image.open(stage/f'{f:06}.png').convert('RGB').crop(box)
   a.thumbnail((405,333))
   im.paste(a,(i*410+(410-a.width)//2,j*360+22))
   d.text((i*410+12,j*360+5),f'{f} {label}',fill='black')
 im.save(p/f'{name}-proof.jpg',quality=91)
