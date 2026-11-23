from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
import json,sys,math
import numpy as np
from render import Film,tween,mix

root=Path(sys.argv[1])
scene=json.loads((root/'ring-next/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def fit(f):
    frame=str(f)
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),np.int16)
    prior=np.asarray(Image.open(root/'clean-frames'/f'{f:06}.png').convert('RGB'),np.int16)
    data=copy(scene)
    data['orbitArrivalExposure']=deepcopy(scene.get('orbitArrivalExposure',{}))
    data['orbitArrivalExposure'][frame]=reg={}
    film=Film(data)
    phase,=film.track('orbitPhase',f)
    for name,orbit,start in (('rings',.50,478),('red',0,479),('blue',.75,479),('dark',.25,481)):
        if f<start: continue
        x,y,size=film.track(f'{name}Orbit' if name in ('red','blue') else f'{name}MeasuredOrbit',f)
        alpha=mix(.68,1,tween(f,start,start+2))
        depth=math.cos((orbit-phase)*math.tau)
        softness=1.7+(1-depth)*2.9+4*(1-tween(f,478,486))
        reg[name]=scene.get('orbitArrivalExposure',{}).get(frame,{}).get(name,[x,y,size,alpha,softness])[:]
    def cost():
        return float(np.abs(np.asarray(film.frame(f),dtype=np.int16)-target).mean())
    previous=float(np.abs(prior-target).mean())
    best=cost()
    for scale in (1,.55):
        for name,values in reversed(list(reg.items())):
            for i,step in enumerate((3.4,3,4,.072,1.25)):
                origin=values[i]
                choice=origin
                for j in (-2,-1,1,2):
                    v=origin+j*step*scale
                    if i==3 and not .28<=v<=1 or i==4 and not .4<=v<=11:
                        continue
                    values[i]=v
                    test=cost()
                    if test<best:
                        best,choice=test,v
                values[i]=round(choice,5)
    print(f,round(previous,6),round(best,6),reg,flush=True)
    return (frame,reg) if best<previous-.02 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=dict(x for x in pool.map(fit,range(478,483)) if x)
    (root/'ring-arrival-fit.json').write_text(json.dumps(results,indent=2)+'\n')
