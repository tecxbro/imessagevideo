from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from PIL import Image, ImageFilter
import numpy as np
from scipy.optimize import differential_evolution
from scipy.ndimage import label, find_objects, binary_dilation

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('project').resolve()))
from render import cursor, interpolate

base=Path('/tmp/sidehoe-hyperframes.wG3QA2')
tracks=json.loads(Path('project/scene.json').read_text())['tracks']
window=88
center=window//2
Y,X=np.mgrid[:window,:window]

def data(f):
    key = 'isolatedFollowPointer' if f<=661 else 'followApproachPointer'
    px,py = interpolate(tracks[key],f)
    img=Image.open(base/'source-stage'/f'{f:06}.png').convert('RGB')
    left,top=round(px)-center,round(py)-center
    patch=img.crop((left,top,left+window,top+window))
    rgb=np.array(patch,dtype=float)
    person=(rgb.max(axis=2)<188)&(rgb.max(axis=2)-rgb.min(axis=2)<38)
    px,py,zoom=interpolate(tracks['followMeasuredCamera'],f)
    if f<=662 and px+400*zoom < left+window:
        person[:,:max(0,round(px+400*zoom-left+5))]=False
    person[:,max(0,1000-left):]=False
    person[max(0,1000-top):,:]=False
    lab,n=label(person)
    areas=[]
    for i,box in enumerate(find_objects(lab)):
        if not box: continue
        component=lab==i+1
        count=component.sum()
        if 9<=count<=550 and box[0].stop-box[0].start<57:
            count = count/(1 + np.hypot(X[component].mean()-center,Y[component].mean()-center)*.035)
            areas.append((count,i))
    if not areas: return None
    _,i=max(areas)
    surround=binary_dilation(lab==i+1,iterations=6 if 657<=f<=667 else 4)
    weight = np.clip((248-rgb.max(axis=2))/230,0,1)*surround
    cx,cy=[(axis*weight).sum()/weight.sum() for axis in (X,Y)]
    return weight,cx,cy,left,top,zoom

def template(angle, scale, spread):
    art=Image.new('RGBA',(window,window),'white')
    cursor(art,center,center,angle,1,scale)
    art=art.filter(ImageFilter.GaussianBlur(spread))
    w=np.clip((248-np.asarray(art)[:,:,0].astype(float))/230,0,1)
    x,y=[(a*w).sum()/max(w.sum(),1) for a in (X,Y)]
    return w,x,y

def fit(f):
    measured=data(f)
    if measured is None:
        return f,None
    ref,rx,ry,left,top,zoom=measured
    def score(parameters, raw=False):
        angle,scale,spread=map(float,parameters)
        art,x,y=template(angle,scale,spread)
        dx,dy=int(round(rx-x)), int(round(ry-y))
        moved=np.roll(art, (dy,dx), (0,1))
        error=np.abs(moved-ref).sum()
        if raw: return [f, round(center+dx+left,2),round(center+dy+top,2),round(angle,2),
                        round(scale,4),round(spread,3)], round(float(error),2)
        return error
    # The full turn is supported throughout the entry and the approach.
    result=differential_evolution(score,[(0,360),(.19,1.03),(.25,8.0)],
                                  maxiter=24,popsize=8,seed=f,tol=.003,polish=False)
    return f,score(result.x,raw=True)

if __name__=='__main__':
    with ProcessPoolExecutor(6) as pool:
        results=dict(pool.map(fit,range(626,670)))
    (base/'incoming-pointer-fit.json').write_text(json.dumps(results,indent=2))
    for f in (626,629,643,649,653,655,657,659,661,662,664,666,669):
        print(f,results[f])
