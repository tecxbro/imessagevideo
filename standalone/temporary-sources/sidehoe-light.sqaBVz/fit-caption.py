from pathlib import Path
from PIL import Image
from copy import deepcopy
import numpy as np,json,sys
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film,fit_ink,messages_font,tween,interpolate
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
priordir=root/'probe-b'
baseline=Path('/tmp/sidehoe-sofia.fuoOwt/clean-frames')
results={}
for f in range(155,161):
    orig=[[*interpolate(scene['tracks'][f'assistantLine{i}'],f),620,1,2*tween(f,158,161),2*tween(f,158,161)] for i in (1,2)]
    l=290
    t=int(orig[0][1])-45
    r=713
    b=int(orig[1][1]+orig[1][3])+45
    roi=l,t,r,b
    target=np.array(Image.open(source/f'{f:06}.png').convert('RGB').crop(roi),dtype=np.int16)
    source_ink=target.mean(2)
    prior=np.array(Image.open(priordir/f'{f:06}.png').convert('RGB').crop(roi),dtype=np.int16)
    old=np.array(Image.open(baseline/f'{f:06}.png').convert('RGB').crop(roi),dtype=np.int16)
    raw=deepcopy(scene)
    raw['copy']['assistant']=['','']
    bg=Film(raw).frame(f).crop(roi).convert('RGBA')
    state=deepcopy(orig)
    n=2
    def render(values):
        img=bg.copy()
        for cap,row in zip(scene['copy']['assistant'],values,strict=True):
            x,y,w,h,weight,opacity,blur_x,blur_y=row
            fit_ink(img,cap,(x-l,y-t,w,h),weight,opacity,(blur_x,blur_y),
                    family=messages_font,ink=(8,8,8),fractional=True)
        err=np.abs(np.asarray(img.convert('RGB'),dtype=np.int16)-target)
        return float(err.mean())
    minimum=render(state)
    error_old=float(np.abs(prior-target).mean())
    error_base=float(np.abs(old-target).mean())
    moves=[(-3,-1.5,0,1.5,3),(-10,-7,-4,-2,0,2,4,7,10),(-10,-5,-2,0,2,5,10),
           (-8,-4,-2,0,2,4,8),(-55,-30,0,25,50),(-.20,-.1,-.05,0),
           (-1.5,-.7,0,.7,1.45,2.5,3.5),(-.9,0,.8,1.45,2.1,3.5,5)]
    for _ in range(2):
        for line in range(n):
            for j,opts in enumerate(moves):
                for val in opts:
                    row=state[line][:]
                    row[j]=round(orig[line][j]+val,3)
                    if j in (6,7) and row[j]<0:
                        continue
                    config=state[:];config[line]=row
                    error=render(config)
                    if error<minimum:
                        state,minimum=config,error
    print(f,*map(lambda x:round(x,4),(error_base,error_old,minimum)),state,flush=True)
    if minimum<error_old:
        results[f]=state
(root/'caption-fit.json').write_text(json.dumps(results,indent=2)+'\n')
