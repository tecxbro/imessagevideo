from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).parent
roots=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),Path('/tmp/sidehoe-thread-audit.oxTJaL/frames')]
sheet=Image.new('RGB',(1008,1690),'#f8f8f8'); d=ImageDraw.Draw(sheet)
for i,f in enumerate((667,668,669,670,671)):
 imgs=[Image.open(k/f'{f:06}.png').convert('RGB') for k in roots]
 a,b=[np.array(im,dtype='int16') for im in imgs]
 q=np.abs(a-b).mean(axis=2)
 for j,im in enumerate([*imgs,Image.fromarray(np.uint8(np.minimum(q*4,255)))]):
  x=j*336;y=i*336+17
  sheet.paste(im.resize((336,319)),(x,y))
  d.text((x+4,y-15),f'{f} '+('source','baseline','difference')[j],fill='black')
sheet.save(p/'follow-grid.jpg',quality=93)
