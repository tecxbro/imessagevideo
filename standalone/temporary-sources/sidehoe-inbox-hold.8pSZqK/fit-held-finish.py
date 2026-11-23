from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import deepcopy
from PIL import Image, ImageColor
from render import Film,tween
import json
import sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
heads=json.loads((p/'pin-head-fit.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
before=json.loads(Path('sidehoe-skill-trial/suggestion-and-type-review/project/scene.json').read_text())

def lights():
    film=Film(scene)
    samples=[([],[]) for j in range(3)]
    for f in (16,22,29,34,39):
        h=scene['inboxHeldRegistration'][str(f)]
        q=film.track('inboxScale',f)[0]
        y0=film.track('inboxY',f)[0]
        x0=500-410*q
        a,b=(np.asarray(Image.open(d/f'{f:06}.png').convert('RGB'),dtype=np.int16)
             for d in (source,p/'held-probe'))
        for j,x in enumerate((169,411,651)):
            dx,dy,size=h['pins'][j]
            cx=x0+(x+dx)*q
            cy=y0+(473+dy)*q
            r=81*q*size
            for v in np.arange(-.57,.64,.05):
                for u in (-.76,-.68,.72,.81):
                    if u*u+v*v>.87:
                        continue
                    xx,yy=int(cx+r*u),int(cy+r*v)
                    target=np.median(a[yy-1:yy+2,xx-1:xx+2],axis=(0,1))
                    current=np.median(b[yy-1:yy+2,xx-1:xx+2],axis=(0,1))
                    error=target-current
                    if max(abs(error))<21 and min(current)<226:
                        samples[j][0].append(((1-v)/2,(1+v)/2))
                        samples[j][1].append(error)
    results=[]
    for i,(x,y) in enumerate(samples):
        x,y=np.asarray(x),np.asarray(y)
        fit=np.zeros((2,3))
        for k in range(4):
            res=np.abs(y-x@fit).mean(1)
            weight=(1+res)**-.6
            fit=np.linalg.solve(x.T@(x*weight[:,None])+np.eye(2)*3,x.T@(y*weight[:,None]))
        keys=scene['inboxPins'][i]
        row=scene['pinLighting'][keys[1]]
        rgb=np.rint(np.clip(np.asarray([ImageColor.getrgb(c) for c in row[:2]])+fit,0,255)).astype(int)
        results.append([*['#'+''.join(f'{c:02x}' for c in color) for color in rgb],row[2]])
    return results

def eval_frame(f):
    key=str(f)
    engine=Film(scene)
    h=scene['inboxHeldRegistration'][key]
    resize=engine.track('inboxScale',f)[0]
    y=engine.track('inboxY',f)[0]
    x=500-410*resize
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    luma=target.mean(2)
    saturation=target.max(2)-target.min(2)
    hardware=deepcopy(h)
    hardware['pinHeadPoses']=heads
    hardware['pinDiskLighting']=lighting
    if f in (40,41):
        hardware['pinSoftness']=[.75,1.35] if f==40 else [1.05,2.1]
    elif f in (10,11,12):
        hardware['pinSoftness']=[.6,1.25] if f==10 else [.4,.65]
    local_luma=(luma<156)&(saturation<36)
    def native_box(mask,rect,ox,oy):
        left,top,right,bottom=map(round,rect)
        yy,xx=np.where(mask[top:bottom,left:right])
        if len(xx)<15:
            return None
        return [round(v,3) for v in ((left+xx.min()-ox)/resize,(top+yy.min()-oy)/resize,
                (xx.max()-xx.min()+1)/resize,(yy.max()-yy.min()+1)/resize)]
    labels=[]
    for j,cx in enumerate((169,411,651)):
        dx,dy,size=hardware['pins'][j]
        xt=x+(cx+dx)*resize
        yt=y+(571+dy)*resize
        labels.append(native_box(local_luma,(xt-64,yt-8,xt+64,yt+44),x,y))
    if all(labels):
        hardware['pinLabels']=labels
    shift_x,shift_y,*_=hardware.get('noteAppearance',(0,0))
    dx,dy,_=hardware['pins'][1]
    left=x+(285+dx+shift_x)*resize
    top=y+(359+(1-tween(f,4,11))*22+dy*.67+shift_y)*resize
    rect=(left+7*resize,top+17*resize,left+201*resize,top+52*resize)
    note=native_box(local_luma,rect,left,top)
    tint=(target[:,:,0]-target[:,:,1]>69)&(target[:,:,0]-target[:,:,2]>44)&(target[:,:,0]>140)
    rect=(left+183*resize,top+15*resize,left+248*resize,top+56*resize)
    icon=native_box(tint,rect,left,top)
    if note and icon:
        hardware['noteInk']=dict(text=note,heart=icon)
    revised=deepcopy(scene)
    front=np.asarray(Film(before).frame(f),dtype=np.int16)
    staged_base=float(np.abs(np.asarray(engine.frame(f),dtype=np.int16)-target).mean())
    first=float(np.abs(front-target).mean())
    winner=h
    best=staged_base
    opts=[hardware,{k:v for k,v in hardware.items() if k!='noteInk'},
          {k:v for k,v in hardware.items() if k not in ('noteInk','pinLabels')}]
    for option in opts:
        revised['inboxHeldRegistration'][key]=option
        image=np.asarray(Film(revised).frame(f),dtype=np.int16)
        err=float(np.abs(image-target).mean())
        if err<best:
            best,winner=err,option
    print(f,round(first,5),round(staged_base,5),round(best,5),flush=True)
    return (key,winner)

if __name__=='__main__':
    lighting=lights()
    data=dict(eval_frame(f) for f in range(10,42))
    (p/'held-finish.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
