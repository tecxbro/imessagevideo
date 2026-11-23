from pathlib import Path
from PIL import Image
from render import Film
from copy import copy
import json,sys
import numpy as np

p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
results={}
for f in range(671,694):
    key=str(f)
    reg=s['threadRegistration']['follow'][key]
    name=f'{f:06}.png'
    tgt=np.asarray(Image.open(source/name).convert('RGB'),dtype=np.float32)
    a=np.asarray(Film(s).frame(f),dtype=np.float32)
    x,y,r,b=reg['blue']
    r0,r1=round(r-108),round(r-48)
    steps=[]
    for row in np.unique(np.rint(np.linspace(max(y+5,2),b-8,8)).astype(int)):
        band=tgt[row-2:row+3,r0:r1]
        pigment=(band[:,:,2]-band[:,:,0]>7)&(band[:,:,1]-band[:,:,0]>3)
        if pigment.sum()<32:
            continue
        current=np.percentile(band[pigment],35,axis=0)
        steps.append([int(row),*np.round(current,3).tolist()])
    if len(steps)<3:
        continue
    trial=copy(s)
    trial['threadRegistration']=copy(s['threadRegistration'])
    trial['threadRegistration']['follow']=copy(s['threadRegistration']['follow'])
    trial['threadRegistration']['follow'][key]={**reg,"blueGradient":steps}
    new=np.asarray(Film(trial).frame(f),dtype=np.float32)
    old,new=(float(np.abs(there-tgt).mean()) for there in (a,new))
    print(f,round(old,5),round(new,5),flush=True)
    if new<old:
        results[key]=steps
(p/'follow-blue.json').write_text(json.dumps(results,indent=2)+'\n')
