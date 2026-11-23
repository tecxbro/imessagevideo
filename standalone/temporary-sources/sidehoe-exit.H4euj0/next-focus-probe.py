from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from itertools import product

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-assistant.lwAAJj/final-inbox-frames')
result={}
for f in range(660,672):
    name=f'{f:06d}.png'
    anchor=np.asarray(Image.open(source/name).convert('RGB'),dtype=np.int16)
    before=np.asarray(Image.open(prior/name).convert('RGB'),dtype=np.int16)
    row=scene['threadRegistration']['follow'][str(f)]
    l,r=row['rails']
    c0,c1=l+8,r-8
    def rates(frame):
        d=np.abs(anchor-frame)
        return float(d.mean()),float(d[120:998,c0:c1].mean())
    opts=[(rates(before),None)]
    for focus in (1.15,2.2,3.4,4.55,5.5):
        for ax,ay in ((0,0),(3,-7),(6,9)):
            v=tuple((ax,ay,focus))
            row['focus']=v
            frame=np.asarray(Film(scene).frame(f),dtype=np.int16)
            opts.append((rates(frame),v))
    best=min(opts,key=lambda row:row[0][0]+row[0][1]*.32)
    print(f,tuple(round(k,4) for k in opts[0][0]),tuple(round(k,4) for k in best[0]),best[1],flush=True)
    result[f]=best[1]
(root/'next-focus-fit.json').write_text(json.dumps(result,indent=2)+'\n')
