"""Fit the handset's two editable veils on unobstructed paper and glass."""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json,sys
from pathlib import Path

import numpy as np
from PIL import Image
from render import Film

w=Path(sys.argv[1])
project=w/'project/scene.json'
s=json.loads(project.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fields(columns,rows,q):
    curves=[]
    for cx,cy,sx,sy,shear in q:
        curves.append(np.exp(-((columns-cx+shear*(rows-cy))/sx)**2-((rows-cy)/sy)**2))
    return np.stack(curves,axis=-1)

def calibrate(frame):
    key=str(frame)
    fit=deepcopy(s.get('assistantVeilRegistration',{}).get(key))
    if not fit:
        original=Film(s)
        c=original.track('assistantLighting',frame)
        fit=dict(color=[c[:8],c[8:]],response=original.track('assistantWashResponse',frame))
    local={**s,'assistantVeilRegistration':{key:fit}}
    actor=Film(local)
    ref=np.asarray(Image.open(source/f'{frame:06d}.png').convert('RGB'),np.int16)
    previous=np.asarray(Film(s).frame(frame),np.int16)
    original=deepcopy(fit)
    fit['color']=[q[:5]+[0,0,0] for q in fit['color']]
    fit['response']=[0,0]
    flat=np.asarray(actor.frame(frame),np.int16)
    original_geometry=np.array([q[:5] for q in original['color']],dtype=float)
    amplitudes=np.array([q[5:8] for q in original['color']],dtype=float)
    xx,yy=np.meshgrid(np.arange(3,1000,7),np.arange(503,1000,6))
    current=flat[yy,xx]
    aimed=ref[yy,xx]
    matte=(current.min(axis=-1)>=246)&(aimed[:,:,0]>=178)&(aimed[:,:,2]>=198)
    matte&=(np.max(np.abs(previous[yy,xx]-aimed),axis=-1)<74)
    x,y=xx[matte]/999,yy[matte]/999
    expected=(current-aimed)[matte]
    opacity=np.ones(x.shape)
    # Fix the lighting geometry against the paper where the underlying fill is known.
    q=original_geometry.copy()
    def objective(geometry):
        a=fields(x,y,geometry)
        weights=np.sqrt(opacity)[:,None]
        design=a*weights
        b=expected*weights
        damping=np.diag([.24,.24])
        colors=np.linalg.solve(design.T@design+damping,design.T@b+damping@amplitudes)
        colors=np.clip(colors,[-20,0,-15],[92,244,95])
        proposed=a@colors
        error=np.sqrt((proposed-expected)**2+2.2)-1.483
        return float(np.mean(error*opacity[:,None])),colors
    best,colors=objective(q)
    for model in range(2):
        predicted=fields(x,y,q)@colors
        weight=np.max(np.abs(predicted-expected),axis=-1)
        opacity=np.clip(6/np.maximum(6,weight),.13,1)
        best,colors=objective(q)
        for scale in (.95,.48,.22):
            for j in range(2):
                for i,step in enumerate((.033,.041,.029,.039,.155)):
                    saved=q.copy()
                    for sign in (-2,-1,1,2):
                        test=saved.copy()
                        test[j,i]+=sign*step*scale
                        if test[j,2]<=.07 or test[j,3]<=.13:
                            continue
                        score,tones=objective(test)
                        if score<best:
                            best,q,colors=score,test,tones
    baseline=float(np.abs(ref-previous).mean())
    chosen=deepcopy(original); winner=baseline
    measured=np.column_stack((q,colors))
    old=np.array(original['color'])
    for strength in (.46,.79,1.0):
        fit['color']=(old+strength*(measured-old)).round(6).tolist()
        start=original['response']
        for a,b in ((1,1),(.78,1),(.83,.80),(1.22,1.15),(1.16,.91),(.68,.7)):
            fit['response']=[round(float(gain*m),5) for gain,m in zip(start,(a,b),strict=True)]
            error=float(np.abs(ref-np.asarray(actor.frame(frame),np.int16)).mean())
            if error<winner:
                winner,chosen=error,deepcopy(fit)
    print(frame,round(baseline,6),round(winner,6),chosen['response'],flush=True)
    return key,chosen if winner<baseline-.005 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=6) as pool:
        new={key:value for key,value in pool.map(calibrate,range(138,162)) if value}
    s.setdefault('assistantVeilRegistration',{}).update(new)
    project.write_text(json.dumps(s,indent=2)+'\n')
    (w/'assistant-light-fit.json').write_text(json.dumps(new,indent=2)+'\n')
