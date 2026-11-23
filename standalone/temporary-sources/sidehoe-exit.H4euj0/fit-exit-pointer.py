from pathlib import Path
import json,sys,copy
import numpy as np
from PIL import Image
from scipy.optimize import minimize

p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import Film
from treatments import follow_pointer
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-assistant.lwAAJj/final-inbox-frames')
scene=json.loads((p/'project/scene.json').read_text())
result={}
for f in range(690,696):
    start=np.array(scene['followPointerOptics'][str(f)],dtype=float)
    x,y,w,h,sx,sy,alpha,lean=start
    l,t,r,b=map(round,(x-12,y-12,x+w+12,y+h+12))
    scene_off=copy.deepcopy(scene)
    scene_off['followPointerOptics'][str(f)][6]=0
    backdrop=Film(scene_off).frame(f).crop((l,t,r,b)).convert('RGBA')
    target=np.asarray(Image.open(source/f'{f:06d}.png').crop((l,t,r,b)),dtype=np.float32)
    prev=np.asarray(Image.open(old/f'{f:06d}.png').crop((l,t,r,b)),dtype=np.float32)
    old_delta=prev-target
    def costs(v):
        x,y,w,h,sx,sy,opacity,lean=v
        canvas=backdrop.copy()
        follow_pointer(canvas,x-l,y-t,w,h,sx,opacity,lean=lean,vertical_softness=sy,rounded=True)
        delta=np.asarray(canvas.convert('RGB'),dtype=np.float32)-target
        return float(abs(delta).mean()),float((delta**2).mean())
    def loss(v):
        a,b=costs(v)
        reg=np.square(v-start)*[.018,.018,.002,.002,.003,.003,2,.005]
        return a+b/275+sum(reg)
    range_=[3.5,4.,4.,5.,1.65,1.9,.20,3.5]
    lo=start-range_
    hi=start+range_
    lo[2:4]=np.maximum(lo[2:4],4)
    lo[4:6]=np.maximum(lo[4:6],.14)
    hi[6]=1
    bounds=list(zip(lo,hi))
    steps=[.90,-.76,.80,1.05,.37,.31,-.028,1.05]
    m=minimize(loss,start,method='Nelder-Mead',bounds=bounds,
               options={'initial_simplex':np.vstack([start,start+np.diag(steps)]),
                        'maxiter':390,'fatol':.0002,'xatol':.002})
    candidates=[start,m.x]
    choose=min(candidates,key=loss)
    if any(v>p for v,p in zip(costs(choose),costs(start))):
        choose=start
    print(f,'previous',(round(float(abs(old_delta).mean()),4),round(float(np.mean(old_delta**2)),4)),
          'probe',tuple(round(v,4) for v in costs(start)),'fit',tuple(round(v,4) for v in costs(choose)),
          'change',np.round(choose-start,2).tolist(),flush=True)
    result[f]=np.round(choose,5).tolist()
(p/'cursor-fit.json').write_text(json.dumps(result,indent=2)+'\n')
