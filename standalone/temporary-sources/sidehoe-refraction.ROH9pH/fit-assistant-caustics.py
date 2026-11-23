from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import Film,caustic_lobes

p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
conditions={
 135: [
  ([145,470,287,600],[211,538,43,42,.20]),
  ([742,473,872,609],[808,539,37,43,.20]),
  ([636,378,743,459],[689,419,26,24,.27]),
  ([104,891,258,1000],[195,961,37,35,.39]),
  ([724,884,873,952],[815,914,30,20,.31]),
 ],
 136:[
  ([94,932,244,1000],[164,985,42,40,.34]),
  ([813,909,884,968],[845,938,17,21,.27]),
 ],
 137:[
  ([804,912,891,984],[851,950,21,22,.33]),
 ],
}
def fit(f):
    src=Image.open(source/f'{f:06}.png').convert('RGB')
    base=Film(s).frame(f).convert('RGB')
    result=[]
    for box,initial in conditions[f]:
        l,t,r,b=box
        rows,cols=np.mgrid[t:b,l:r]
        target=np.asarray(src.crop(box),dtype=float)
        current=np.asarray(base.crop(box),dtype=float)
        residual=target-current
        old=float(np.abs(residual).mean())
        eligible=(target.max(2)>198)&(current.max(2)>185)
        signal=np.clip((target.max(2)-target.min(2))/28,0,1)
        confidence=(.45+signal*.55)*eligible
        weight=confidence.ravel()[::2]
        target_fit=residual.reshape(-1,3)[::2]
        def solve(shape):
            g=caustic_lobes(cols,rows,shape)
            A=g.reshape(-1,8)[::2]
            ridge=np.eye(8)*5.6
            coeffs=np.linalg.solve(A.T@(A*weight[:,None])+ridge,A.T@(target_fit*weight[:,None]))
            coeffs=coeffs.clip(-107,94)
            corrected=np.clip(np.rint(current+g@coeffs),0,255)
            cost=float(np.abs(target-corrected).mean())
            return cost,coeffs
        config=initial[:]
        value,colors=solve(config)
        for factor in (1,.48):
            for i,k in enumerate((2.3,2.4,2.2,2.15,.038)):
                old_pose=config[i]
                chosen=old_pose
                for direction in (-2,-1,1,2):
                    config[i]=old_pose+direction*factor*k
                    if i==4 and config[i]<.11:continue
                    test,coeffs=solve(config)
                    if test<value:
                        value,chosen,colors=test,config[i],coeffs
                config[i]=round(chosen,4)
        if value<old-.11:
            result.append([box,config,colors.round(4).tolist()])
        print(f,box,round(old,5),round(value,5),config,flush=True)
    return str(f),result

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        result=dict(pool.map(fit,conditions))
    (p/'assistant-caustic-fit.json').write_text(json.dumps(result,indent=2)+'\n')
