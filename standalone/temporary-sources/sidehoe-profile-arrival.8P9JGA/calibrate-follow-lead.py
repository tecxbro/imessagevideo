from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
from render import Film, tween
import json,math,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def solve(f):
    key=str(f)
    base=Film(scene)
    records=scene['followSettledRegistration']
    held=records[key]
    reg=deepcopy(held)
    trial=copy(scene)
    trial['followSettledRegistration']=copy(records)
    trial['followSettledRegistration'][key]=reg
    camera=held.get('camera',base.track('followBodyRegistration',f)[:4])
    x,y,w,vertical=camera
    region=np.s_[max(0,round(y)-15):min(1000,round(y+827*w*vertical)+17),
                  max(0,round(x)-21):min(1000,round(x+400*w)+21)]
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    actual=np.asarray(base.frame(f),dtype=np.int16)
    prev=np.abs(target-actual)
    initial=float(prev.mean()),float(prev[region].mean())
    default=.38+2.2*max(0,1-abs(f-665)/7)
    trail,=base.track('followExposure',f)
    start=[*camera,trail,default,default]
    settings=start[:]
    def score(current):
        reg['camera']=current[:4]
        reg['preContactExposure']=current[4:]
        current_frame=np.asarray(Film(trial).frame(f),dtype=np.int16)
        error=np.abs(current_frame-target)
        return float(error.mean()),float(error[region].mean())
    best=score(settings)
    for fine in (1,.50):
        for i,step in enumerate((1.7,1.7,.005,.005,2.7,.52,.63)):
            at=settings[i]
            for k in (-2,-1,1,2):
                option=settings[:]
                option[i]=max(0,at+k*step*fine) if i>=4 else at+k*step*fine
                result=score(option)
                if result[0]<best[0] and result[1]<best[1]:
                    settings,best=option,result
    score(settings)
    xx,yy,scale,aspect=settings[:4]
    _,_,bottom,utility,home=held['layout']
    stage_y=round(yy+(bottom+utility+15)*scale*aspect)
    l=round(xx+150*scale)
    r=round(xx+255*scale)
    mat=target[max(0,stage_y-3):min(1000,stage_y+7),l:r]
    valid=(mat.mean(2)>172)&(mat.mean(2)<243)&((mat.max(2)-mat.min(2))<28)
    if valid.sum()>40:
        brightness=np.rint(np.median(mat[valid],axis=0)).astype(int)
        selected=None
        for ratio in (.48,1):
            tray=np.rint(np.array([215,216,222])*(1-ratio)+brightness*ratio).astype(int).tolist()
            reg['keyboardTrayColor']=tray
            result=score(settings)
            if result[0]<best[0] and result[1]<best[1]:
                best,selected=result,tray
        if selected is not None:
            reg['keyboardTrayColor']=selected
        else:
            reg.pop('keyboardTrayColor',None)
    print(f,initial,best,settings,reg.get('keyboardTrayColor'),flush=True)
    return (key,reg) if best[0]<initial[0] and best[1]<initial[1] else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        selected=dict(z for z in pool.map(solve,range(650,660)) if z)
    (p/'follow-lead-fit.json').write_text(json.dumps(selected,indent=2)+'\n')
