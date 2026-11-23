from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image,ImageColor
import json,sys
import numpy as np
from render import Film

p=Path(sys.argv[1])
baseline=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def tint(rgb): return '#%02x%02x%02x'%tuple(np.uint8(np.clip(np.rint(rgb),0,255)))
def measure(frame):
    f=str(frame)
    target=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB'),np.int16)
    data=copy(baseline)
    data['assistantScreenRegistration']=copy(baseline['assistantScreenRegistration'])
    data['assistantScreenRegistration'][f]=reg=deepcopy(baseline['assistantScreenRegistration'][f])
    film=Film(data)
    prior=np.asarray(film.frame(frame),dtype=np.int16)
    initial=float(np.abs(target-prior).mean())
    prior_scale=film.track("assistantPinControls",frame)
    left,right,side_diameter,side_lift,pin_alpha,label_alpha=prior_scale
    _,vertical,rad=film.track('assistantPinPose',frame)
    x,y,body_w=film.track('assistantMeasuredPosition',frame)
    pins=reg.get('pins',[(left,vertical+side_lift,side_diameter),(right,vertical+side_lift,side_diameter)])
    head=reg.get('headPoses',[[1,1,0,0,0],[1,1,0,0,0]])
    reg['headPoses']=head
    colors=[baseline['pinLighting'][key][:] for key in ('marie','darla')]
    reg['pinDiskLighting']=colors
    for index,(cx,cy,diam) in enumerate(pins):
        dx=x+cx*body_w/900
        dy=y+cy
        r=diam/2
        xx=r*body_w/900
        l,t,rr,b=round(dx-xx-8),round(dy-r-8),round(dx+xx+8),min(1000,round(dy+r+8))
        if b<=t+18: continue
        crop=(slice(t,b),slice(l,rr))
        actual=np.asarray(target[crop],dtype=float)
        original=np.asarray(prior[crop],dtype=float)
        yy,xxgrid=np.mgrid[t:b,l:rr]
        xi=(xxgrid-dx)/xx
        eta=(yy-dy)/r
        visible=((xi*xi+eta*eta)<.80)&(abs(xi)>.62)
        if not visible.any(): continue
        u=(eta[visible]+1)/2
        design=np.stack((1-u,u),axis=1)
        residual=(actual-original)[visible]/max(.35,pin_alpha)
        gain=np.linalg.lstsq(design,residual,rcond=None)[0].clip(-27,27)
        original_lights=colors[index][:]
        rgb=np.array([ImageColor.getrgb(k) for k in original_lights[:2]])
        def loss():
            painted=np.asarray(film.frame(frame),dtype=np.int16)[crop]
            return float(np.abs(painted-actual).mean())
        base=loss()
        best=base
        chosen=original_lights
        for strength in (.45,.88,1.30):
            colors[index]=[*(tint(v) for v in rgb+gain*strength),original_lights[2]]
            score=loss()
            if score<best:
                best,chosen=score,colors[index]
        colors[index]=chosen
        current=head[index]
        for i,step in enumerate((.032,.039,2.3,2.3,2.8)):
            seed=current[i]
            keep=seed
            for sign in (-2,-1,1,2):
                current[i]=seed+sign*step
                score=loss()
                if score<best:
                    best,keep=score,current[i]
            current[i]=round(keep,6)
        print(frame,index,round(base,4),round(best,4),colors[index],current,flush=True)
    score=float(np.abs(target-np.asarray(film.frame(frame),dtype=np.int16)).mean())
    print(frame,'all',round(initial,6),round(score,6),flush=True)
    if score<initial-.01:
        return f,{k:reg[k] for k in ('headPoses','pinDiskLighting')}
    return f,{}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=7) as pool:
        result={k:v for k,v in pool.map(measure,range(135,138)) if v}
    (p/'entry-pin-fit.json').write_text(json.dumps(result,indent=2)+'\n')
