from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def grade(frame):
    key=str(frame)
    original=scene['threadRegistration']['sofia'][key]
    candidate=copy(scene)
    candidate['threadRegistration']=copy(scene['threadRegistration'])
    candidate['threadRegistration']['sofia']=copy(scene['threadRegistration']['sofia'])
    put=candidate['threadRegistration']['sofia']
    controls=deepcopy(original)
    put[key]=controls
    image=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB'),dtype=np.int16)
    left,right=original['rails']
    keyboard_top,tray,_=original['keys']
    original_header=original['casing'][3]
    zoom=(right-left)/376
    region=np.s_[max(0,round(original['casing'][1])):min(1000,round(keyboard_top+325*zoom)),left-12:right+12]
    def score():
        a=np.asarray(Film(candidate).frame(frame),dtype=np.int16)
        error=np.abs(a-image)
        return float(error.mean()),float(error[region].mean())
    initial=score()
    best=initial
    def accept(current,winner):
        return current[0]<winner[0] and current[1]<winner[1]
    # Measure the keyboard plastic between the utility keys and the home bar.
    footer_y=original.get('keyboardFooter',[keyboard_top+246*zoom])[0]
    y=max(keyboard_top+187*zoom,footer_y-3)
    patch=image[int(y)-4:int(y)+6,int(left+(right-left)*.25):int(left+(right-left)*.78)]
    b=np.mean(patch,axis=2)
    mask=(b>169)&(b<239)&((patch.max(2)-patch.min(2))<28)
    if mask.sum()>40:
        observed=np.rint(np.median(patch[mask],axis=0)).astype(int)
        fitted=tray
        for weight in (.45,.85,1):
            rgb=np.rint(np.array(tray)*(1-weight)+observed*weight).astype(int).tolist()
            controls['keys'][1]=rgb
            trial=score()
            if accept(trial,best):
                best,fitted=trial,rgb
        controls['keys'][1]=fitted
    params=list(original['focus'])
    for variable, options in (
        (1,(0,2.5,4.5,6.5,8.5,11,13)),
        (2,(0,.45,.85,1.25,-.38)),
        (0,(0,1.15,2.4,3.4)),
    ):
        value=params[variable]
        for entry in options:
            q=params[:]
            q[variable]=max(0,value+entry)
            controls['focus']=q
            trial=score()
            if accept(trial,best):
                best,params=trial,q
        controls['focus']=params
    height=original_header
    for delta in (-5,-3,-1,1,3,5):
        controls['casing'][3]=original_header+delta
        trial=score()
        if accept(trial,best):
            best,height=trial,controls['casing'][3]
    controls['casing'][3]=height
    print(frame,initial,best,controls['focus'],controls['keys'][1],height,flush=True)
    return (key,controls) if accept(best,initial) else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=dict(x for x in pool.map(grade,range(319,329)) if x)
    (p/'sofia-entrance-calibration.json').write_text(json.dumps(rows,indent=2)+'\n')
