from pathlib import Path
from PIL import Image,ImageDraw
import sys,numpy as np
p=Path(__file__).parent
inputs=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),Path('/tmp/sidehoe-thread-audit.oxTJaL/frames'),p/sys.argv[1]]
sheet=Image.new('RGB',(1260,1350),'#f8f8f8'); d=ImageDraw.Draw(sheet)
for i,f in enumerate(range(134,138)):
 imgs=[Image.open(k/f'{f:06}.png').convert('RGB') for k in inputs]
 a,b,c=[np.array(im,dtype='int16') for im in imgs]
 print(f,*[round(np.abs(a-z).mean(),4) for z in [b,c]],'badge',*[round(np.abs(a[540:825,363:650]-z[540:825,363:650]).mean(),3) for z in [b,c]])
 for j,im in enumerate(imgs):
  x=j*420;y=i*337+20
  sheet.paste(im.crop((0,232,1000,1000)).resize((420,314)),(x,y))
  d.text((x+4,y-17),f'{f} '+('source','prior','candidate')[j],fill='black')
sheet.save(p/(sys.argv[1]+'.jpg'),quality=93)
