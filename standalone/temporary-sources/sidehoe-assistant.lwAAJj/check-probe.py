from pathlib import Path
from PIL import Image
import numpy as np,sys
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-pullback.nP3qTC/final-title-frames')
new=p/sys.argv[1]
for f in range(132,164):
 name=f'{f:06d}.png'
 if not (new/name).exists():continue
 a,b,c=[np.asarray(Image.open(r/name).convert('RGB'),dtype=np.int16) for r in (src,prior,new)]
 g,h=abs(a-b),abs(a-c)
 print(f,round(g.mean(),4),round(h.mean(),4),round(h.mean()-g.mean(),4),
       [(round(g[y:Y,x:X].mean(),3),round(h[y:Y,x:X].mean(),3))
        for x,y,X,Y in ((120,340,860,660),(40,265,965,518),(75,560,930,978))])
