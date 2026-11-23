"""Reject inner-edge treatments whose complete stage moves away from the source."""
from pathlib import Path
import json,sys
from PIL import Image
import numpy as np
from render import Film

p,prev=map(Path,sys.argv[1:])
s=json.loads((prev/'casing-next/scene.json').read_text())
case=s['assistantCasingGlass']
original=Film({**s,'assistantCasingGlass':{}})
fit=Film(s)
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
keep={}
for k,g in case.items():
    f=int(k)
    target=np.asarray(Image.open(src/f'{f:06d}.png').convert('RGB'),np.int16)
    a,b=[float(np.abs(target-np.asarray(x.frame(f),np.int16)).mean()) for x in (original,fit)]
    if b<a:
        keep[k]=g
    print(f,round(a,5),round(b,5),b<a)
(p/'glass-accepted.json').write_text(json.dumps(keep,indent=2)+'\n')
