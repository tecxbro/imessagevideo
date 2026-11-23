from concurrent.futures import ProcessPoolExecutor
from copy import copy
from pathlib import Path
from PIL import Image
from render import Film
from treatments import capsule_coverage, camera_island_layer
import json
import sys
import numpy as np

root = Path(sys.argv[1])
scene = json.loads((root/'project/scene.json').read_text())
ref = Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def optimize(pars, cost, steps, floor, ceil, factors=(1, .5, .22)):
    p=np.array(pars,dtype=float)
    best=cost(p)
    for k in factors:
        for i,gap in enumerate(steps):
            prior=p[i]
            for direction in (-2,-1,1,2):
                v=p.copy()
                v[i]=np.clip(prior+direction*gap*k,floor[i],ceil[i])
                value=cost(v)
                if value<best:
                    p,best=v,value
    return p

def solve(frame):
    label=str(frame)
    film=Film(scene)
    px, py, screen_w = film.track('assistantMeasuredPosition',frame)
    ix, iy, iw, ih = film.track('assistantIslandBox',frame)
    x = px + (ix + iw/2)*screen_w/900
    y = py+iy+ih/2
    w = iw*screen_w/900
    h = ih
    blank=copy(scene)
    blank['assistantIslandRegistration']={label:{}}
    base=np.asarray(Film(blank).frame(frame),dtype=np.float32)
    before=np.asarray(film.frame(frame),dtype=np.float32)
    goal=np.asarray(Image.open(ref/f'{frame:06}.png').convert('RGB'),dtype=np.float32)
    # The measured band contains the cutout and its immediate glass gap.
    bord=(int(x-w/2-15),int(y-h/2-12),int(x+w/2+16),int(y+h/2+14))
    l,t,r,b=bord
    rows, cols=np.mgrid[t:b:2,l:r:2]
    before_fit, clean, target = [a[rows,cols] for a in (before,base,goal)]
    bracket=(clean.mean(2)>104) | (rows>y-ih*.23)
    br=bracket
    black = [8,8,10]
    def outer_cost(params):
        cov=capsule_coverage(cols,rows,params)[...,None]
        image=clean+(black-clean)*cov
        return float(np.abs(image-target)[br].mean())
    soft = (5 if frame in (134,135,136) else 2.8 if frame<142 else
            .9 if frame<154 else max(1.2,(frame-151)*.41))
    layout=optimize((x,y,w,h,soft,0,0),outer_cost,(3,3,4,4,.8,2,2),
                    (x-16,y-14,w-24,h-18,.45,-19,-20),
                    (x+16,y+14,w+24,h+19,11,19,20),
                    (1,.55,.28,.14))
    mask=capsule_coverage(cols,rows,layout)
    cx,cy,sw,sh,blur,slope,bend=layout
    island=mask>.95
    dark=island & (np.abs(cols-(cx+sw*.07))<sw*.055)
    black=np.clip(np.percentile(target[dark],35,axis=0),0,36) if dark.any() else black
    # Within the dark opening, the sensor's edge is visible in luma.
    insert0=[cx-sw*.183,cy+bend*.8,sw*.51,sh*.59,
             max(.7,blur*.57),slope*.48,bend*.23]
    left=island & (np.abs(cols-insert0[0])<sw*.15) & (np.abs(rows-insert0[1])<sh*.17)
    pigment=np.clip(np.median(target[left],axis=0),0,51).tolist() if left.any() else [18,18,19]
    keep=island&(cols<cx+sw*.10)
    def insert_cost(params):
        cov=capsule_coverage(cols,rows,params)[...,None]
        image=np.asarray(black)+(pigment-black)*cov
        return float(np.abs(image-target)[keep].mean())
    p=insert0
    sensor=optimize(p,insert_cost,(3,1.9,5,3,.35,1.5,1.5),
                    [p[0]-18,p[1]-9,p[2]-20,p[3]-20,.4,-16,-12],
                    [p[0]+18,p[1]+9,p[2]+20,p[3]+20,9,16,12],(1,.52,.22))
    right=island&(cols>cx+sw*.24)
    expected_x=cx+sw*.35
    expected_y=cy + slope*.70 + bend*.51
    weight=np.maximum(target[...,2]-target[...,0]-3,0)**1.45 * right
    lens_x=float((cols*weight).sum()/weight.sum()) if weight.sum() else expected_x
    lens_y=float((rows*weight).sum()/weight.sum()) if weight.sum() else expected_y
    lx=np.clip(lens_x,expected_x-11,expected_x+11)
    ly=np.clip(lens_y,expected_y-10,expected_y+10)
    lens_model=[(lx,ly,sh*.26,sh*.31),(lx,ly,sh*.133,sh*.17),
                (lx+.019*sw,ly-sh*.06,sh*.068,sh*.078),
                (lx-.013*sw,ly+sh*.087,sh*.064,sh*.084)]
    fields=[]
    for xx,yy,rx,ry in lens_model:
        fields.append(np.exp(-((cols[right]-xx)/rx)**2-((rows[right]-yy)/ry)**2))
    X=np.vstack(fields).T
    if X.size:
        raw=target[right]-np.asarray(black)
        lift=np.linalg.solve(X.T@X+np.eye(4)*.28,X.T@raw)
        lift=np.clip(lift,-26,85)
    else:
        lift=np.zeros((4,3))
    look=dict(opening=layout.tolist(),sensor=sensor.tolist(),black=np.asarray(black).tolist(),
              sensor_color=np.asarray(pigment).tolist(),
              reflections=[[*shape,*delta] for shape,delta in zip(lens_model,lift,strict=True)])
    current=copy(scene)
    current['assistantIslandRegistration']={label:look}
    redrawn=np.asarray(Film(current).frame(frame),dtype=np.float32)
    was=float(np.abs(before-goal).mean())
    now=float(np.abs(redrawn-goal).mean())
    ims=[np.abs(a[t:b,l:r]-goal[t:b,l:r]).mean() for a in (before,redrawn)]
    print(frame,round(was,5),round(now,5),[round(float(n),3) for n in ims],flush=True)
    return (label,look) if now<was and ims[1]<ims[0] else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        records=dict(z for z in pool.map(solve,range(134,162)) if z is not None)
    (root/'island-fit.json').write_text(json.dumps(records,indent=2)+'\n')
