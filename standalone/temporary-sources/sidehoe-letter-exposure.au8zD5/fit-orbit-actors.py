"""Register the orbit's four independent tile silhouettes and optical focus."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from render import Film

p=Path(sys.argv[1]); config=p/'orbit-next/scene.json'
s=json.loads(config.read_text())
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
region=(174,310,828,770)

def fit(f):
    k=str(f)
    info={}
    settings={**s,'orbitActorFit':{k:info}}
    actor=Film(settings)
    source=Image.open(ref/f'{f:06d}.png').convert('RGB')
    sample=np.asarray(source.crop(region),np.int16)
    def loss():
        return float(np.abs(np.asarray(actor.frame(f).crop(region),np.int16)-sample).mean())
    first=best=loss()
    for precision in (1,.48,.22):
        for name in ('rings','dark','blue','red'):
            pose=info.get(name,[0,0,1,1,1,1]).copy()
            for i,step in enumerate((12,9,.085,.082,.53,.10)):
                initial=pose.copy()
                for sign in (-2,-1,1,2):
                    test=initial.copy()
                    test[i]+=sign*step*precision
                    if not(abs(test[0])<94 and abs(test[1])<62 and .65<test[2]<1.37 and
                           .65<test[3]<1.37 and .04<test[4]<3.3 and .54<test[5]<=1):
                        continue
                    info[name]=test
                    score=loss()
                    if score<best:
                        best,pose=score,test
                info[name]=pose
    print(f,round(first,5),round(best,5),info['rings'],flush=True)
    return k,{n:[round(v,5) for v in pose] for n,pose in info.items()}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=6) as pool:
        fit=dict(pool.map(fit,range(550,562)))
    s['orbitActorFit']=fit
    config.write_text(json.dumps(s,indent=2)+'\n')
    (p/'orbit-actor-fit.json').write_text(json.dumps(fit,indent=2)+'\n')
