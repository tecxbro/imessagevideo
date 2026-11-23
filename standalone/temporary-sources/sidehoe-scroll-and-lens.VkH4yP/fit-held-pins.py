"""Align the two contact pins and the center badge on the live handset."""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
import json,sys
from PIL import Image,ImageColor
import numpy as np
from render import Film

work=Path(sys.argv[1])
s=json.loads((work/'project/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def fit(frame):
    key=str(frame)
    reg=deepcopy(s['assistantScreenRegistration'].get(key,{}))
    baseline=Film(s)
    candidate=Film({**s,'assistantScreenRegistration':{**s['assistantScreenRegistration'],key:reg}})
    target=np.asarray(Image.open(src/f'{frame:06d}.png').convert('RGB'),np.int16)
    initial=np.asarray(baseline.frame(frame),np.int16)
    old_error=float(np.abs(initial-target).mean())
    x,y,w=candidate.track('assistantMeasuredPosition',frame)
    px,py,diam=candidate.track('assistantPinPose',frame)
    l,r,side_diameter,dy,alpha,_=candidate.track('assistantPinControls',frame)
    pins=reg.setdefault('pins',[[l,py+dy,side_diameter],[r,py+dy,side_diameter]])
    faces=reg.setdefault('headPoses',[[1,1,0,0,0],[1,1,0,0,0]])
    paints=reg.setdefault('pinDiskLighting',[s['pinLighting'][name][:] for name in ('marie','darla')])
    badge=reg.setdefault('badgePose',[px,py,diam,0])
    for index,actor in enumerate([*pins,badge]):
        cx,cy,d=actor[:3]
        hx=x+cx*w/900
        hy=y+cy
        left,top=max(0,round(hx-d*.62)),max(0,round(hy-d*.62))
        right,bottom=min(1000,round(hx+d*.62)),min(1000,round(hy+d*.62))
        if bottom-top<30:
            continue
        expected=target[top:bottom,left:right]
        def cost():
            a=np.asarray(candidate.frame(frame),np.int16)[top:bottom,left:right]
            return float(np.abs(a-expected).mean())
        best=cost()
        for i,step in enumerate((2.0,1.7,3.1,.31) if index==2 else (2.0,1.7,3.1)):
            q=actor[i]
            win=q
            for n in (-2,-1,1,2):
                value=q+n*step
                if i==3 and not 0<=value<=1:
                    continue
                actor[i]=value
                c=cost()
                if c<best:
                    best,win=c,value
            actor[i]=round(win,4)
        if index==2:
            continue
        center=x+actor[0]*w/900
        center_y=y+actor[1]
        rows,cols=np.mgrid[top:bottom,left:right]
        dx=(cols-center)/(actor[2]/2*w/900)
        dy=(rows-center_y)/(actor[2]/2)
        mask=(abs(dx)>.58)&(dx**2+dy**2<.79)
        if np.count_nonzero(mask)>25:
            screen=np.asarray(candidate.frame(frame),np.int16)[top:bottom,left:right]
            u=(dy[mask]+1)/2
            a=np.stack((1-u,u),axis=1)
            correction=np.linalg.lstsq(a,(expected-screen)[mask],rcond=None)[0]
            correction=np.clip(correction,-26,26)
            original=paints[index].copy()
            active=np.array([ImageColor.getrgb(c) for c in original[:2]])
            optimal=original
            for gain in (.65,1.02,1.54):
                color=np.uint8(np.clip(np.rint(active+gain*correction),0,255))
                paints[index]=['#%02x%02x%02x'%tuple(line) for line in color]+[original[2]]
                c=cost()
                if c<best:
                    best,optimal=c,paints[index]
            paints[index]=optimal
        face=faces[index]
        for j,step in enumerate((.045,.042,2.3,2.15,2.2)):
            q=face[j]; win=q
            for n in (-2,-1,1,2):
                face[j]=q+n*step
                c=cost()
                if c<best:
                    best,win=c,face[j]
            face[j]=round(win,5)
    half=np.asarray(candidate.frame(frame),np.int16)
    final=float(np.abs(half-target).mean())
    print(frame,round(old_error,5),round(final,5),flush=True)
    return key,reg if final<old_error-.003 else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=6) as pool:
        accepted={f:value for f,value in pool.map(fit,range(138,161)) if value}
    (work/'assistant-pins-fit.json').write_text(json.dumps(accepted,indent=2)+'\n')
