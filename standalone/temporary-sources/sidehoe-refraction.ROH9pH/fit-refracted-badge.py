from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from render import Film

p=Path(sys.argv[1]); src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
baseline=json.loads((p/'project/scene.json').read_text())
def fit(f):
    k=str(f)
    data=copy(baseline)
    data['assistantScreenRegistration']=copy(baseline['assistantScreenRegistration'])
    data['assistantScreenRegistration'][k]=reg=deepcopy(baseline['assistantScreenRegistration'][k])
    film=Film(data)
    x,y,diam=film.track('assistantPinPose',f)
    _,top,_=film.track('assistantMeasuredPosition',f)
    ox=baseline['assistantEntranceOptics'].get(k,{}).get('pin')
    if ox:
        x,y,diam,dist=ox
    else:
        dist=0
    l,t,r,b=(int(x-diam*.70),max(0,int(top+y-diam*.68)),int(x+diam*.74),min(1000,int(top+y+diam*.70)))
    target=np.asarray(Image.open(src/f'{f:06}.png').convert('RGB').crop((l,t,r,b)),np.int16)
    def cost():
        repl=np.asarray(film.frame(f).crop((l,t,r,b)),np.int16)
        return float(abs(repl-target).mean())
    previous=cost()
    config=[[x,y,diam,dist],.82 if f<=135 else .91,[2.2,1.7] if f==134 else [0,0],.35,6 if f==134 else 0]
    reg['badgeCalibration']=config
    best=cost()
    for scale in (1,.60,.26):
        for arr,js in ((config[0],(2.7,2.9,3.2,3.5)),(config,(0,.043,0,.028,3.2)),
                       (config[2],(.9,.9))):
            for i,step in enumerate(js):
                if step==0: continue
                initial=arr[i]
                chosen=initial
                for sign in (-2,-1,1,2):
                    q=initial+sign*step*scale
                    if arr is config and i==1 and not .59<=q<=1.1:continue
                    arr[i]=q
                    value=cost()
                    if value<best:
                        best,chosen=value,q
                arr[i]=round(chosen,5)
    print(f,round(previous,6),round(best,6),config,flush=True)
    return k,config if best<previous-.12 else None
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        data={k:v for k,v in pool.map(fit,range(134,138)) if v}
    (p/'badge-calibration.json').write_text(json.dumps(data,indent=2)+'\n')
