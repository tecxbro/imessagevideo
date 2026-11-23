from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
from render import Film
import sys,json
import numpy as np

p=Path(sys.argv[1])
new=json.loads((p/'project/scene.json').read_text())
before=json.loads(Path('sidehoe-skill-trial/camera-and-message-review/project/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def evaluate(f):
    name=f'{f:06}.png'
    z=np.asarray(Image.open(src/name).convert('RGB'),dtype=np.int16)
    a,b=[np.asarray(Film(x).frame(f),dtype=np.int16) for x in (before,new)]
    for img,folder in ((a,'baseline'),(b,'ink-probe')):
        Image.fromarray(np.uint8(img)).save(p/folder/name)
    d,e=(float(np.abs(z-x).mean()) for x in (a,b))
    print(f,round(d,5),round(e,5),flush=True)
    return [f,d,e]

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        result=list(pool.map(evaluate,[*range(342,353),*range(670,695)]))
    (p/'ink-stage.json').write_text(json.dumps(result,indent=2)+'\n')
