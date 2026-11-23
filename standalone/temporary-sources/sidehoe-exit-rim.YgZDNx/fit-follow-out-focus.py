"""Fit the follow-up handset's withdrawal exposure from decoded stage frames."""
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from render import Film,tween

work=Path(sys.argv[1])
cfg=work/'follow-next/scene.json'
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit(frame):
    scene=json.loads(cfg.read_text())
    entry=scene['threadRegistration']['follow'][str(frame)]
    ref=np.asarray(Image.open(reference/f'{frame:06}.png').convert('RGB'),np.int16)
    def cost():
        rendered=np.asarray(Film(scene).frame(frame),np.int16)
        return float(np.abs(ref-rendered).mean())
    original=entry.get('focus')
    first=best=cost()
    candidate=original.copy() if original else [0,0,.78+1.7*tween(frame,688,694)]
    for precision in (1,.52,.22):
        for variable,step in enumerate((3,3,.52)):
            initial=candidate.copy()
            for n in (-2,-1,1,2):
                trial=initial.copy()
                trial[variable]+=n*step*precision
                if not 0<=trial[variable]<=22:
                    continue
                entry['focus']=trial
                score=cost()
                if score<best:
                    best,candidate=score,trial
    print(frame,round(first,5),round(best,5),candidate,flush=True)
    return str(frame), [round(v,4) for v in candidate] if best<first-.01 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        result=dict(pool.map(fit,range(690,696)))
    eligible={f:v for f,v in result.items() if v}
    (work/'follow-withdraw-focus.json').write_text(json.dumps(eligible,indent=2)+'\n')
    s=json.loads(cfg.read_text())
    for f,v in eligible.items():
        s['threadRegistration']['follow'][f]['focus']=v
    cfg.write_text(json.dumps(s,indent=2)+'\n')
