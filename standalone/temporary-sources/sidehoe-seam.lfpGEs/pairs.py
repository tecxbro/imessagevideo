from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,sys
base=Path(__file__).parent
r=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
v=Path('/tmp/sidehoe-surface.oiqQZp/final-frames')
for title,frames in [('handoff',range(398,405)),('sofia',range(337,343))]:
 w,h=365,376
 sheet=Image.new('RGB',(3*w,h*len(frames)),'white')
 d=ImageDraw.Draw(sheet)
 for i,f in enumerate(frames):
  pair=[Image.open(j/f'{f:06}.png').convert('RGB') for j in (r,v)]
  a,b=[np.asarray(t,dtype=np.int16) for t in pair]
  q=np.abs(a-b).mean(axis=2)
  delta=Image.fromarray(np.uint8(np.clip(q*5,0,255)))
  for j,t in enumerate([*pair,delta]):
   sheet.paste(t.resize((w,356)),(w*j,h*i+20))
   d.text((w*j+4,h*i+4),str(f)+' '+['source','current','difference x5'][j],fill='black')
 sheet.save(base/(title+'.jpg'),quality=90)
