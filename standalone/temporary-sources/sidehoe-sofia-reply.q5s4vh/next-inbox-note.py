from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'inbox-next/scene.json').read_text())
mapped=json.loads((p/'next-inbox-rows.json').read_text())
scene['inboxHeldRegistration'].update(mapped)
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def evaluate(f):
    key=str(f)
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    entry=scene['inboxHeldRegistration'][key]
    so=np.asarray(Film(scene).frame(f),dtype=np.int16)
    y=400+round((f-31)*-.6)
    lines=np.s_[max(295,y-90):495,335:675]
    best=float(np.abs(ref-so)[lines].mean())
    baseline=best
    start=(0,0,0,10)
    accepted=None
    for choices in ((None,(0,0,.06,12),(0,0,.15,14),(0,0,.26,16)),
                    ((-3,-4),(0,-4),(3,-4),(-3,1),(3,1),(0,3))):
        for value in choices:
            if value is None:
                continue
            if len(value)==2:
                proposed=(*value,*start[2:])
            else:
                proposed=value
            entry['noteAppearance']=proposed
            a=np.asarray(Film(scene).frame(f),dtype=np.int16)
            score=float(np.abs(ref-a)[lines].mean())
            if score<best and np.abs(ref-a).mean()<np.abs(ref-so).mean():
                start,best,accepted=proposed,score,proposed
        if not accepted:
            entry.pop('noteAppearance',None)
    return (key,list(accepted),baseline,best) if accepted else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        observations=[r for r in pool.map(evaluate,range(10,42)) if r]
    (p/'next-inbox-note.json').write_text(json.dumps(observations,indent=2)+'\n')
    print('note frames improved',len(observations),'f34 fit',[r for r in observations if r[0]=='34'],flush=True)
