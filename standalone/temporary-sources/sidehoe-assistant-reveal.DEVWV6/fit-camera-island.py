from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
import render
from treatments import camera_island_layer, camera_edge_light

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit(frame):
    key=str(frame)
    optics=deepcopy(scene['assistantIslandRegistration'][key])
    model=render.Film(scene)
    x,y,w,h,*_=optics['opening']
    l,t,r,b=round(x-w/2-48),round(y-h/2-55),round(x+w/2+48),round(y+h/2+41)
    target=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB').crop((l,t,r,b)),dtype=float)
    prior=np.asarray(model.frame(frame).crop((l,t,r,b)),dtype=float)
    callback=render.paint_camera_island
    try:
        render.paint_camera_island=lambda *a,**k:None
        background=np.asarray(model.frame(frame).crop((l,t,r,b)),dtype=float)
    finally:
        render.paint_camera_island=callback
    rows,columns=np.mgrid[t:b,l:r]
    def paint(local_background, fields=optics):
        alpha,rgb=camera_island_layer(columns,rows,fields)
        return alpha[...,None]*rgb+(1-alpha[...,None])*local_background,alpha
    def cost(local_background=background):
        replica,_=paint(local_background)
        return float(np.abs(replica-target).mean())
    previous=float(np.abs(prior-target).mean())
    best=cost()
    steps=([1.5,1.3,2.1,1.8,.26,1.4,1.4],[1.7,1.5,2.6,1.9,.32,1.55,1.2])
    for scale in (1,.56,.26):
        for (k,n),increments in zip((('opening',7),('sensor',7)),steps,strict=True):
            value=optics[k]
            for i in range(n):
                peak=value[i]
                select=peak
                for sign in (-2,-1,1,2):
                    move=peak+sign*increments[i]*scale
                    if i==4 and move<.24: continue
                    value[i]=move
                    measure=cost()
                    if measure<best:
                        best,select=measure,move
                value[i]=round(select,5)
    # Fit the four lens contributions separately from the pixels at the capsule edge.
    for reflection in optics['reflections']:
        for i,step in enumerate((1.4,1.2,2,2.2,7,7,7)):
            peak=reflection[i]
            select=peak
            for z in (-2,-1,1,2):
                value=peak+z*step
                if i in (2,3) and value<3: continue
                reflection[i]=value
                measure=cost()
                if measure<best:
                    best,select=measure,value
            reflection[i]=round(select,5)
    if frame<=137:
        cx,cy,w,h,*_=optics['opening']
        edge_y=cy-h/2
        refractors=[
            (round(cx+shift,3),round(edge_y-d,3),rx,ry)
            for shift in (-112,-85,-58,-31,-4,23,50,77,103,125)
            for d,rx,ry in ((4,16,5.4),(14,21,8.0),(26,22,9.2))
        ]
        painted,alpha=paint(background)
        basis=np.stack([np.exp(-((columns-a)/rx)**2-((rows-b)/ry)**2)*(1-alpha)
                        for a,b,rx,ry in refractors],axis=-1)
        D=basis.reshape(-1,len(refractors))[::2]
        residual=(target-painted).reshape(-1,3)[::2]
        ridge=np.eye(D.shape[1])*6.5
        coeff=np.linalg.solve(D.T@D+ridge,D.T@residual).clip(-141,141)
        proposed=[[*coordinates,*vector.round(4).tolist()] for coordinates,vector
                  in zip(refractors,coeff,strict=True) if max(abs(vector))>=2.0]
        retouched=np.clip(background+camera_edge_light(columns,rows,proposed),0,255)
        score=cost(retouched)
        if score<best:
            best=score
            optics['edgeReflections']=proposed
    print(frame,round(previous,5),round(best,5),len(optics.get('edgeReflections',())),flush=True)
    return (key,optics) if best<previous-.05 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=6) as pool:
        result=dict(row for row in pool.map(fit,range(134,143)) if row)
    (p/'island-fit.json').write_text(json.dumps(result,indent=2)+'\n')
