from pathlib import Path
from copy import copy
from PIL import Image
from render import Film,title_heart,layer,blur,tween
import json
import sys
import numpy as np

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
film=Film(scene)
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
reports={}
pigment=np.array([247,143,253])
for f in range(186,207):
    key=str(f)
    hearts=scene['titleHeartOptics'][key]
    rect=(142,365,870,700)
    true=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB').crop(rect),dtype=np.float32)
    plain=copy(scene)
    plain['titleHeartOptics']=copy(scene['titleHeartOptics'])
    plain['titleHeartOptics'][key]=[[*pose[:5],0,*pose[6:]] for pose in hearts]
    bg=np.asarray(Film(plain).frame(f).crop(rect),dtype=np.float32)
    initial=np.asarray(film.frame(f).crop(rect),dtype=np.float32)
    a_values=[]
    for pose in hearts:
        picture=layer(rect[2]-rect[0],rect[3]-rect[1])
        title_heart(picture,[pose[0]-rect[0],pose[1]-rect[1],*pose[2:]])
        spread=tween(f,205,212)
        if spread:
            picture=blur(picture,(1.4*spread,6.5*spread))
        a_values.append(np.asarray(picture.getchannel('A'),dtype=np.float32)/255)
    mix=np.stack(a_values,axis=2)
    weight=np.prod(1-mix,axis=2)[...,None]
    design=mix.copy()
    for i in range(mix.shape[-1]-1):
        design[:,:,i] *= np.prod(1-mix[:,:,i+1:],axis=2)
    inside=(mix.max(2)>.070)
    X=design[inside].astype(float)
    target=true[inside]-bg[inside]*weight[inside]
    initial_color=np.tile(pigment,(len(hearts),1))
    fit=initial_color
    ramp=np.identity(len(hearts))*1.8
    for _ in range(4):
        cost=np.abs(X@fit-target)
        coefficient=(2.2+cost)**-.7
        vectors=[]
        for c in range(3):
            x=X*coefficient[:,c,None]
            params=np.linalg.solve(X.T@x+ramp,x.T@target[:,c]+ramp@initial_color[:,c])
            vectors.append(params)
        fit=np.clip(np.stack(vectors,axis=1),[204,122,207],[255,192,255])
    modified=[[*geometry,*np.rint(rgb).astype(int).tolist()] for geometry,rgb in zip(hearts,fit)]
    after=copy(scene)
    after['titleHeartOptics']=copy(scene['titleHeartOptics'])
    before=float(np.abs(initial-true).mean())
    after['titleHeartOptics'][key]=modified
    changed=np.asarray(Film(after).frame(f).crop(rect),dtype=np.float32)
    error=float(np.abs(changed-true).mean())
    print(f,round(before,5),round(error,5),[p[-3:] for p in modified],flush=True)
    if before>error:
        reports[key]=modified
(root/'heart-color-pose.json').write_text(json.dumps(reports,indent=2)+'\n')
