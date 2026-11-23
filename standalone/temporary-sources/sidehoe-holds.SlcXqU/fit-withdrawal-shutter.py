"""Evaluate spatial exposure against the last three source handset frames."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from render import Film,tween

p=Path(sys.argv[1])
root=p/'withdrawal-next'
cfg=root/'scene.json'
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def fit(f):
    s=json.loads(cfg.read_text())
    key=str(f); base=s['threadRegistration']['follow'][key]
    target=np.asarray(Image.open(ref/f'{f:06d}.png').convert('RGB'),np.int16)
    def score():
        art=np.asarray(Film(s).frame(f),np.int16)
        delta=np.abs(art-target)
        return float(delta.mean()+.34*delta[710:,155:850].mean()),float(delta.mean())
    first,prev=score()
    best,before=first,prev
    focus=base.get('focus',[0,0,.78+1.7*tween(f,688,694)])
    candidate=[500,455,.03,0,4,.82,focus[2]]
    control=None
    for zoom in (.028,.059,.090):
        base['cameraShutter']=[500,455,zoom,0,4,1]
        base['focus']=[0,0,max(1.05,focus[2]-.85)]
        metric,full=score()
        if metric<best and full<=prev:
            best,before=metric,full
            candidate=[*base['cameraShutter'],base['focus'][2]]
            control=candidate.copy()
    for precision in (1,.48,.22):
        for i,step in enumerate((13,25,.012,2,3,.17,.46)):
            old=candidate.copy()
            for direction in (-2,-1,1,2):
                new=old.copy()
                new[i]+=direction*precision*step
                if not (.002<=new[2]<=.14 and 0<=new[5]<=1 and .3<=new[6]<=8):
                    continue
                base['cameraShutter']=new[:6]
                base['focus']=[0,0,new[6]]
                metric,full=score()
                if metric<best and full<=prev:
                    best,before,candidate=metric,full,new
                    control=new.copy()
    print(f,round(first,5),round(best,5),round(prev,5),round(before,5),control,flush=True)
    return key,control


if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=3) as pool:
        result=dict(pool.map(fit,range(693,696)))
    s=json.loads(cfg.read_text())
    for f,control in result.items():
        if control:
            t=s['threadRegistration']['follow'][f]
            t['cameraShutter']=control[:6]
            t['focus']=[0,0,control[6]]
    (p/'withdrawal-shutter-fit.json').write_text(json.dumps(result,indent=2)+'\n')
    cfg.write_text(json.dumps(s,indent=2)+'\n')
