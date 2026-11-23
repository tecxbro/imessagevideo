"""Test local pose continuity where the decoded orbit still regressed."""
from copy import deepcopy
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from render import Film

p=Path(sys.argv[1]); cfg=p/'orbit-smooth-next/scene.json'
s=json.loads(cfg.read_text()); original=deepcopy(s)
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
actor=Film(s)
reference={}
renders={}
affected={504,505,506,514,515,516,521,522,523,524,525,526}
for f in sorted(affected|{f-1 for f in affected}|{f+1 for f in affected}):
    crop=(137,253,879,784)
    reference[f]=np.asarray(Image.open(source/f'{f:06d}.png').convert('RGB').crop(crop),np.int16)
    renders[f]=np.asarray(actor.frame(f).crop(crop),np.int16)
def measurements(f, current):
    target=reference[f]
    absolute=float(np.abs(current-target).mean())
    motion=[]
    for t in (f-1,f+1):
        displacement=(current-renders[t])-(target-reference[t])
        motion.append(float(np.abs(displacement).mean()))
    return absolute,float(np.mean(motion))
chosen=[]
for repeat in range(2):
    for f in sorted(affected):
        mark=s['orbitActorFit'][str(f)]
        starting=renders[f]
        init,shift=measurements(f,starting)
        for tile in ('rings','blue','red','dark'):
            fitted=mark[tile].copy()
            lo=np.asarray(s['orbitActorFit'][str(f-1)][tile]); hi=np.asarray(s['orbitActorFit'][str(f+1)][tile])
            adjacent=(lo+hi)*.5
            winner=fitted.copy()
            live=starting
            for a,b in ((0,2),(0,4),(4,6),(0,6)):
                for mix in (.12,.27,.44,.64,1):
                    test=np.array(fitted)
                    test[a:b]+=(adjacent[a:b]-test[a:b])*mix
                    mark[tile]=test.round(6).tolist()
                    image=np.asarray(actor.frame(f).crop(crop),np.int16)
                    now,move=measurements(f,image)
                    if now<=init and move<shift-.001:
                        init,shift,winner,live=now,move,mark[tile],image
            mark[tile]=winner
            if winner!=fitted:
                chosen.append([f,tile,init,shift])
            starting=live
            renders[f]=starting
for f in affected:
    a=np.asarray(Film(original).frame(f),np.int16)
    b=np.asarray(actor.frame(f),np.int16)
    target=np.asarray(Image.open(source/f'{f:06d}.png').convert('RGB'),np.int16)
    if np.abs(a-target).mean()<np.abs(b-target).mean():
        s['orbitActorFit'][str(f)]=original['orbitActorFit'][str(f)]
cfg.write_text(json.dumps(s,indent=2)+'\n')
(p/'orbit-continuity-fit.json').write_text(json.dumps(chosen,indent=2)+'\n')
print('proposed',len(chosen),'accepted frames',sum(s['orbitActorFit'][str(f)]!=original['orbitActorFit'][str(f)] for f in affected))
