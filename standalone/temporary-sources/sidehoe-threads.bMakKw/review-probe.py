from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,sys
p=Path(__file__).parent
d=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage');old=Path('/tmp/sidehoe-reveal-clean.DeKHma/frames')
new=p/sys.argv[1]
frames=[342,348,351,672,675,679,688,693,694]
sheet=Image.new('RGB',(1323,1125),'#f9f9f9')
draw=ImageDraw.Draw(sheet)
for f in [*range(339,357),*range(669,696)]:
 ims=[Image.open(t/f'{f:06}.png').convert('RGB') for t in (d,old,new)]
 a,b,c=[np.array(x,dtype='int16') for x in ims]
 print(f,*[round(np.abs(a-v).mean(),3) for v in (b,c)])
 if f not in frames:continue
 i=frames.index(f)
 for j,im in enumerate(ims):
  x=(i%3)*441+j*147;y=(i//3)*375
  view=im.resize((147,147))
  sheet.paste(view,(x,y+22))
  draw.text((x+4,y+5),f'{f} '+('source','previous','revised')[j],fill='black')
sheet.save(p/(sys.argv[1]+'.jpg'),quality=92)
