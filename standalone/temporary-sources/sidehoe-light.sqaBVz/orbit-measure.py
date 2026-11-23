from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
scene=json.loads((root/'project/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
candidate=Path('/tmp/sidehoe-sofia.fuoOwt/clean-frames')
def measure(source,k):
    a=np.array(source,dtype=np.int16)
    r,g,b=np.moveaxis(a,2,0)
    if k=='red':
        use=(r-g>80)&(r>208)&(g<147)&(b<230)
    else:
        use=(b-r>67)&(b-g>50)&(b>226)&(g>100)&(g<191)
    y,x=np.where(use)
    if x.size<50:
        return None
    return [int(y.size),int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

res={}
for f in range(518,545):
    dims=[Image.open(p/f'{f:06}.png').convert('RGB') for p in (reference,candidate)]
    rows=[[measure(im,k) for im in dims] for k in ('red','blue')]
    res[f]=rows
    print(f,*rows,interpolate(scene['tracks']['redOrbit'],f),interpolate(scene['tracks']['blueOrbit'],f))
(root/'orbit-landmarks.json').write_text(json.dumps(res,indent=2)+'\n')
