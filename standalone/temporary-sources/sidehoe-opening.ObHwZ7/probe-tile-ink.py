from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from PIL import Image
from render import Film
import json
import numpy as np

p=Path(__file__).parent
scene=json.loads((p/'cursor-next/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
previous=p/'clean-frames'
def try_once(f):
    s=deepcopy(scene)
    name=f'{f:06}.png'
    rect=(403,max(0,682+(f-615)*29),598,min(1000,860+(f-615)*35))
    a=np.asarray(Image.open(source/name).convert('RGB').crop(rect),dtype=np.float32)
    b=np.asarray(Image.open(previous/name).convert('RGB').crop(rect),dtype=np.float32)
    value=lambda i: float(np.abs(a-i).mean())
    start=value(b)
    best=start,(54,87,1,0)
    for x,y,zoom,bold in [(54,y,h,k) for y in (78,82,86,90) for h in (.91,.95,1.0)
                          for k in (.3,.8)]:
        s['calendarNumeralRegistration']={str(f):(x,y,zoom,bold)}
        sample=Film(s).frame(f).crop(rect)
        score=value(np.asarray(sample,dtype=np.float32))
        if score<best[0]:
            best=score,(x,y,zoom,bold)
    print(f,start,best,flush=True)
    return f,start,best

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(try_once,range(615,621)))
    (p/'tile-ink.json').write_text(json.dumps({f:{'initial':a,'revised':b[0],'pose':b[1]}
                                for f,a,b in results if b[0]<a},indent=2)+'\n')
