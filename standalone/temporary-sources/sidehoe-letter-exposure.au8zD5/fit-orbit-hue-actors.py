"""Register the orbit's four independent tile silhouettes and optical focus."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from render import Film

p=Path(sys.argv[1]); config=p/'orbit-next/scene.json'
s=json.loads(config.read_text())
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
region=(174,310,828,770)

def fit(f):
    k=str(f)
    info={}
    settings={**s,'orbitActorFit':{k:info}}
    actor=Film(settings)
    source=Image.open(ref/f'{f:06d}.png').convert('RGB')
    sample=np.asarray(source.crop(region),np.int16)
    def loss():
        return float(np.abs(np.asarray(actor.frame(f).crop(region),np.int16)-sample).mean())
    first=best=loss()
    # Sample tile colors close to their evaluated camera positions before
    # refining shape and focus against all four overlapping surfaces.
    rgb=np.asarray(source,dtype=np.int16)
    yy,xx=np.ogrid[:source.height,:source.width]
    channels=rgb.transpose(2,0,1)
    r,g,b=channels
    masks={
        'rings': (((g-r>48)&(b>g-4)&(r<130))|((r-g>51)&(b-g>51)&(r<203)&(g<133))),
        'dark': (np.max(rgb,axis=2)<104),
        'red': ((r-g)>73)&((r-b)>32)&(r>180)&(g<170),
        'blue': ((b-r)>60)&((b-g)>27)&(g>83)&(r<148),
    }
    paths={'rings':'ringsMeasuredOrbit','dark':'darkMeasuredOrbit','red':'redOrbit','blue':'blueOrbit'}
    # The initial pose remains eligible when part of an actor is occluded.
    for name in ('rings','dark','blue','red'):
        x,y,size=actor.track(paths[name],f)
        a=1.06 if name=='rings' else .65
        allowed=(abs(xx-x)<size*a)&(abs(yy-y)<size*.62)
        v,u=np.where(masks[name]&allowed)
        if len(u)<30:
            continue
        x_min,x_max=np.percentile(u,[2,98])
        y_min,y_max=np.percentile(v,[2,98])
        dx=(x_min+x_max)*.5-x
        dy=(y_min+y_max)*.5-y
        if abs(dx)>92 or abs(dy)>58:
            continue
        prior=info.get(name,[0,0,1,1,1,1])
        selected=prior.copy()
        for fraction in (.60,1):
            for dy_part in (0,.55,1):
                q=[dx*fraction,dy*dy_part,1,1,1,1]
                info[name]=q
                score=loss()
                if score<best:
                    best,selected=score,q
        info[name]=selected
    for precision in (1,.48,.22):
        for name in ('rings','dark','blue','red'):
            pose=info.get(name,[0,0,1,1,1,1]).copy()
            for i,step in enumerate((12,9,.085,.082,.53,.10)):
                initial=pose.copy()
                for sign in (-2,-1,1,2):
                    test=initial.copy()
                    test[i]+=sign*step*precision
                    if not(abs(test[0])<94 and abs(test[1])<62 and .65<test[2]<1.37 and
                           .65<test[3]<1.37 and .04<test[4]<3.3 and .54<test[5]<=1):
                        continue
                    info[name]=test
                    score=loss()
                    if score<best:
                        best,pose=score,test
                info[name]=pose
    print(f,round(first,5),round(best,5),info['rings'],flush=True)
    return k,{n:[round(v,5) for v in pose] for n,pose in info.items()}

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=8) as pool:
        fit=dict(pool.map(fit,range(486,614)))
    s['orbitActorFit']=fit
    (p/'orbit-full-scene.json').write_text(json.dumps(s,indent=2)+'\n')
    (p/'orbit-full-fit.json').write_text(json.dumps(fit,indent=2)+'\n')
