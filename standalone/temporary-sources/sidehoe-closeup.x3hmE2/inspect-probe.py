from pathlib import Path
from PIL import Image,ImageDraw
import sys
import numpy as np
p=Path(sys.argv[1]); folder=sys.argv[2]
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
regions={'left':(75,0,133,470),'right':(865,0,927,470),'out':(390,0,842,72),'reply':(205,365,727,470),
         'chips':(172,500,532,625),'composer':(138,626,861,726),'keys':(125,732,873,1000)}
for f in range(668,695):
    ims=[Image.open(d/f'{f:06}.png').convert('RGB') for d in (source,p/'prior-probe',p/folder)]
    src,old,new=[np.array(im,dtype=np.int16) for im in ims]
    prev,now=abs(src-old),abs(src-new)
    print(f,round(prev.mean(),5),round(now.mean(),5),flush=True)
    if f==681:
        for n,(l,t,r,b) in regions.items():
            print(n,[round(a[t:b,l:r].mean(),4) for a in (prev,now)])
        board=Image.new('RGB',(1800,600))
        for i,im in enumerate(ims):
            board.paste(im.resize((600,600),Image.Resampling.LANCZOS),(600*i,0))
        board.save(p/'closeup-stage.jpg',quality=94)
