from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
p=Path(sys.argv[1]);root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
rows=[]
for f in range(708,778):
 file=f'{f:06}.png'
 imgs=[Image.open(d/file).convert('RGB') for d in (root,p/'prior-full',p/'closing-probe')]
 target,old,new=map(lambda i:np.asarray(i,dtype=np.int16),imgs)
 prev,next_=np.abs(target-old),np.abs(target-new)
 b,a=float(prev.mean()),float(next_.mean())
 samples={}
 for label,(l,t,r,bot) in {'top text':(292,575,698,635),'low text':(242,635,760,695),'wash':(0,730,1000,1000)}.items():
  samples[label]=[float(z[t:bot,l:r].mean()) for z in (prev,next_)]
 rows.append([f,b,a,samples])
 if f in (734,754,765,767,775):
  board=Image.new('RGB',(1500,500))
  for j,im in enumerate(imgs): board.paste(im.resize((500,500),Image.Resampling.LANCZOS),(j*500,0))
  board.save(p/f'closing-stage-{f}.jpg',quality=94)
 print(f,round(b,5),round(a,5),'improved' if a<b else '')
(p/'closing-stage-results.json').write_text(json.dumps(rows,indent=2)+'\n')
