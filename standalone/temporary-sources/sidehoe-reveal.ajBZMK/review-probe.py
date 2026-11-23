from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,sys
d=Path(__file__).parent
name=sys.argv[1]
frames=[135,136,137,139,140,142,144,150,157]
sheet=Image.new('RGB',(1296,1110),'#fbfbfb'); draw=ImageDraw.Draw(sheet)
for f in range(133,163):
 data=[Image.open(d/t/f'{f-133:03}.png').convert('RGB') for t in ('source','prior')]
 data.append(Image.open(d/name/f'{f:06}.png').convert('RGB'))
 a,b,c=[np.asarray(img,dtype=np.int16) for img in data]
 print(f,*[round(np.abs(a-z).mean(),3) for z in (b,c)],*[round(np.abs(a[:380]-z[:380]).mean(),3) for z in (b,c)])
 if f not in frames:continue
 i=frames.index(f);x=432*(i%3);y=370*(i//3)
 for j,(t,img) in enumerate(zip(('source','prior','probe'),data)):
  u=img.crop((45,round(max(110,170+(f-140)*4)),955,1000)); u.thumbnail((143,344))
  sheet.paste(u,(x+j*144,y+23));draw.text((x+j*144+7,y+5),f'{f} {t}',fill='#141414')
sheet.save(d/(name+'.jpg'),quality=92)
