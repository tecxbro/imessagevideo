from pathlib import Path
from copy import copy
from PIL import Image
from render import Film
import json
import sys
import numpy as np

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
film=Film(scene)
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def field(x,y,geometry):
    cx,cy,sx,sy,shear=geometry
    return np.exp(-((x-cx+shear*(y-cy))/sx)**2-((y-cy)/sy)**2)

def fit(rgb, clean, settings):
    y,x=np.mgrid[4:1000:8,4:1000:8]
    old=clean[y,x]
    target=rgb[y,x]
    clear=(old.min(2)>246)&(target[...,0]>156)&(y>260)
    clear &= ((np.abs(target[...,2]-target[...,0])<75)&(target[...,1]>65))
    tx,ty=x[clear]/999,y[clear]/999
    delta=np.clip(253-target[clear],-2,188)
    geometry=np.asarray(settings).reshape(2,8)[:,:5].copy()
    pigment=np.asarray(settings).reshape(2,8)[:,5:].copy()
    penalty=np.identity(2)*.003
    shift_cost=np.array([.009,.014,.028,.016,.0015])
    prior=geometry.copy()

    def grade(choices):
        design=np.stack([field(tx,ty,g) for g in choices],axis=1)
        l=design.T@design+penalty
        rgb_fit=np.linalg.solve(l, design.T@delta+penalty@pigment)
        rgb_fit=np.clip(rgb_fit,[-12,-3,-12],[155,275,155])
        residual=design@rgb_fit-delta
        error=np.abs(residual).mean()+np.sum(((choices-prior)**2)*shift_cost[None,:])
        return error, rgb_fit

    best=grade(geometry)
    for scale in (1,.52,.26):
        for j in range(2):
            for k, increment in enumerate((.075,.060,.067,.051,.32)):
                current=geometry[j,k]
                for direction in (1,-1):
                    testing=geometry.copy()
                    testing[j,k]=current+direction*increment*scale
                    if k in (2,3) and testing[j,k]<.095:
                        continue
                    harder=grade(testing)
                    if harder[0]<best[0]:
                        best=harder
                        geometry=testing
    return np.column_stack([geometry,best[1]])

def fit_response(rgb, clean, settings, response):
    y,x=np.mgrid[4:1000:5,4:1000:5]
    old=clean[y,x]
    target=rgb[y,x]
    dark=(old.min(2)<215)&(np.abs(old[...,0]-old[...,2])<45)&(y>330)
    tx,ty=x[dark]/999,y[dark]/999
    old,target=old[dark],target[dark]
    fields=np.stack([field(tx,ty,g) for g in settings[:,:5]],axis=1)
    chroma=fields@settings[:,5:]
    gain=np.array(response)
    signal=fields*settings[:,6]
    def estimate(gain):
        a=np.clip(signal@gain/175,0,.94)[:,None]
        paint=np.clip(253-chroma/np.maximum(a, 1/255),0,255)
        return (np.abs(old*(1-a)+paint*a-target).mean()+np.sum((gain-response)**2)*.009)
    best=estimate(gain)
    for step in (.24,.12,.06):
        for n in range(len(gain)):
            center=gain[n]
            for direction in (-2,-1,1,2):
                other=gain.copy()
                other[n]=max(.55,center+step*direction)
                error=estimate(other)
                if error<best:
                    gain,best=other,error
    return gain

reports={}
for f in range(137,162):
    fkey=str(f)
    baseline=np.asarray(Image.open(root/'registered-rim'/f'{f:06}.png'),dtype=np.float32)
    rgb=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    no_wash=copy(scene)
    no_wash['tracks']=copy(scene['tracks'])
    no_wash['tracks']['assistantLighting']=[[0,*([1,1,1,1,0,0,0,0]*2)]]
    raw=np.asarray(Film(no_wash).frame(f),dtype=np.float32)
    settings=np.asarray(film.track('assistantLighting',f))
    response=np.asarray(film.track('assistantWashResponse',f))
    fitted=fit(rgb,raw,settings)
    gain=fit_response(rgb,raw,fitted,response)
    retuned=copy(scene)
    retuned['tracks']=copy(scene['tracks'])
    retuned['tracks']['assistantLighting']=[[0,*fitted.ravel().tolist()]]
    choice=None
    prior=float(np.abs(baseline-rgb).mean())
    best=prior
    for candidate in (gain,response,(gain+response)/2):
        retuned['tracks']['assistantWashResponse']=[[0,*candidate.tolist()]]
        after=np.asarray(Film(retuned).frame(f),dtype=np.float32)
        error=float(np.abs(after-rgb).mean())
        if error<best:
            best=error
            choice=candidate
    print(f,round(prior,5),round(best,5),
          None if choice is None else list(np.round(choice,3)),flush=True)
    if choice is not None and (prior-best)>.009:
        reports[fkey]=dict(color=fitted.tolist(),response=choice.tolist(),prior=prior,error=best)
(root/'wash-fit.json').write_text(json.dumps(reports,indent=2)+'\n')
