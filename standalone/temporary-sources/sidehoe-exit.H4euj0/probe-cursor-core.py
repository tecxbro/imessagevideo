from pathlib import Path
from PIL import Image
from copy import deepcopy
import json,math,sys
import numpy as np

root=Path(__file__).parent
sys.path.insert(0,str(root/'tile-push-clean'))
from render import Film,follow_pointer
scene=json.loads((root/'tile-push-clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
frames=(671,674,675,676,677,678,679,680,681,685,686,689,691,693,694,695)
answers={}
for f in frames:
    trial=deepcopy(scene)
    params=trial['followPointerOptics'][str(f)]
    original=list(params)
    params[6]=0
    canvas=Film(trial).frame(f)
    x,y,w,h,_,_,_,lean=original
    box=[math.floor(x)-12,math.floor(y)-12,math.ceil(x+w+abs(lean))+12,math.ceil(y+h)+12]
    ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB').crop(box),dtype=np.int16)
    plain=canvas.crop(box).convert("RGBA")
    stage=np.asarray(plain.convert('RGB'),dtype=np.int16)
    mean=ref.mean(axis=2); back=stage.mean(axis=2)
    keep=(mean+16<back) | (back>228)
    def score(v):
        x,y,w,h,bx,by,alpha,lean=v
        plate=plain.copy()
        follow_pointer(plate,x-box[0],y-box[1],w,h,bx,alpha,lean,
                       vertical_softness=by,rounded=True)
        diff=np.abs(np.asarray(plate.convert('RGB'),dtype=np.int16)-ref)
        return float(diff[keep].mean())
    value=original[:]
    base=score(value)
    best=base
    ranges=[(-2,-1.4,-.75,-.25,0,.25,.75,1.4,2),(-3,-2,-1.25,-.5,0,.7,1.5),(-1.5,-.75,0,.75,1.5,2.5),(-3,-1.5,0,1.5,2.5,3.8),(-.65,-.3,0,.3,.65),(-.5,-.22,0,.25,.5),(0,),(-2,-1,0,.7,1.5,2.5)]
    for round_id in range(2):
        for col,steps in enumerate(ranges):
            offset=original[col]
            for shift in steps:
                t=value[:]
                t[col]=max(0,offset+shift) if col in (4,5) else offset+shift
                err=score(t)
                if err<best:
                    best,value=err,t
    print(f,round(base,4),round(best,4),value,flush=True)
    answers[f]=[base,best,value]
(root/'cursor-core-fit.json').write_text(json.dumps(answers,indent=2)+'\n')
