from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,sys
p=Path(sys.argv[1]); refs=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
parts={'upper_rim':(140,270,865,380),'rails':(28,500,125,1000),
 'camera':(337,354,664,486),'status':(146,379,846,483),'edit':(100,481,288,598),
 'filter':(720,478,885,605),'message_heading':(382,490,618,605),
 'side_pins':(131,628,851,866),'branding':(382,607,610,828),'row':(104,886,908,1000)}
for f in (134,135,136,137):
 a,b=[np.array(Image.open(d/f'{f:06}.png').convert('RGB'),np.int16) for d in (refs,p/'prior-full')]
 e=abs(a-b)
 print(f,e.mean())
 for name,(l,t,r,bot) in parts.items(): print(name,round(e[t:bot,l:r].mean(),2),int(e[t:bot,l:r].sum()//3))
 blocks=[]
 for t in range(260,1000,80):
  for l in range(20,1000,87):
   blocks.append((e[t:min(1000,t+80),l:min(1000,l+87)].mean(),(l,t)))
 print(sorted(blocks,reverse=True)[:10])
for f,(left,top,right,bottom) in [(134,(112,305,886,860)),(135,(95,305,885,998)),
                                (136,(95,323,885,998)),(137,(95,350,885,998))]:
 w=right-left; h=bottom-top
 out=Image.new('RGB',(2*w,h),'#ddd')
 for j,d in enumerate((refs,p/'prior-full')):
  im=Image.open(d/f'{f:06}.png').convert('RGB')
  out.paste(im.crop((left,top,right,bottom)),(j*w,0))
 out.save(p/f'lens-window-{f}.jpg',quality=96)
