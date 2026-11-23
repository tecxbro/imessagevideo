from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,sys
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-thread-audit.oxTJaL/frames')
box=(0,232,1000,1000)
sheet=Image.new('RGB',(1260,1350),'#f8f8f8'); d=ImageDraw.Draw(sheet)
for i,f in enumerate((134,135,136,137)):
 imgs=[Image.open(k/f'{f:06}.png').convert('RGB') for k in (src,old)]
 a,b=[np.array(im,dtype='int16') for im in imgs]
 q=np.abs(a-b).mean(axis=2)
 print('FRAME',f, 'total', round(q.mean(),4))
 for y in (320,380,420,480,550,630,720,810,890,940,975,994):
  print(y,end=' ')
  for z in (a,b):
   l=np.flatnonzero(np.median(z[max(0,y-6):y+7,:150,:],axis=(0,2))<150)
   r=np.flatnonzero(np.median(z[max(0,y-6):y+7,850:,:],axis=(0,2))<150)+850
   print((int(l[0]),int(l[-1]),int(r[0]),int(r[-1])) if len(l) and len(r) else None,end=' ')
  print()
 for j,im in enumerate([*imgs,Image.fromarray(np.uint8(np.minimum(q*4,255)))]):
  x=j*420;y=i*337+20
  sheet.paste(im.crop(box).resize((420,314)),(x,y))
  d.text((x+4,y-17),f'{f} '+('source','prior','difference')[j],fill='black')
sheet.save(p/'first-grid.jpg',quality=93)
