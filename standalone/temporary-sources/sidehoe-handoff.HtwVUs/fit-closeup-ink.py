from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
from artwork import messages_font
from render import fit_ink
import json
import numpy as np
import sys

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit_line(src, frame, text, box, row_limits, swatch, old_parameters, steps, *, color_fit=True, start=None):
    x,y,w,h=box
    left,right=max(0,int(x)-15),min(1000,int(x+w)+40)
    top,bottom=max(0,int(row_limits[0])),min(1000,int(row_limits[1]))
    target=src[top:bottom,left:right]
    surface=Image.fromarray(np.uint8(np.broadcast_to(swatch[top:bottom,None],target.shape).copy())).convert('RGBA')
    expected=target.astype(np.int16)
    stage=.78+max(0,(672-frame)*.48)+1.7*max(0,min(1,(frame-688)/6))**2*(3-2*max(0,min(1,(frame-688)/6)))
    def score(values):
        xx,yy,ww,hh,weight,shade,softness=values
        v=surface.copy()
        focus=(float((softness**2+(stage*.85)**2)**.5),float((softness**2+stage**2)**.5))
        fit_ink(v,text,(xx-left,yy-top,ww,hh),weight,1,focus,family=messages_font,
                ink=(round(shade),)*3,fractional=True)
        offset=np.asarray(v)[...,:3].astype(np.int16)-expected
        return np.abs(offset).mean()
    before=score(old_parameters)
    best=list(start or old_parameters)
    error=score(best)
    for step in (1,.5,.25):
        for j,stride in enumerate(steps):
            if not stride or j==5 and not color_fit: continue
            base=best[j]
            for scale in (-2,-1,1,2):
                trial=best.copy()
                trial[j]=base+step*stride*scale
                if trial[4]<310 or trial[4]>560 or not 12<trial[5]<256 or not 0<=trial[6]<=5: continue
                value=score(trial)
                if value < error:
                    best,error=trial,value
    return ({'box':[round(v,4) for v in best[:4]],'weight':round(best[4]),
             'color':[round(best[5])]*3,'blur':round(best[6],4)},before,error)

def solve(frame):
    reg=scene['threadRegistration']['follow'][str(frame)]
    src=np.array(Image.open(source/f'{frame:06}.png').convert('RGB'))
    updates={}
    results=[]
    for j,(caption,base_box) in enumerate(zip(scene['copy']['follow'][3],reg['items'][1][1],strict=True)):
        x,y,w,h=base_box
        background=np.repeat([reg['bubbleFill'][1]],1000,axis=0)
        patch,m0,m1=fit_line(src,frame,caption,base_box,(y-5,y+h+4),background,
                             [x,y,w,h,440,34,.25],(.8,.65,2,.7,17,7,.44))
        if m1<m0-.06:
            updates[f'1:{j}']=patch
            results.append(round(m0-m1,3))
    x0,y0,x1,y1=reg['blue']
    height=y1-y0
    colors=np.array(reg['blueGradient'])
    ramp=np.stack([np.interp(np.arange(1000),colors[:,0],c) for c in colors[:,1:].T],axis=1)
    blue=[]
    for j,caption in enumerate(scene['copy']['follow'][1]):
        x=x0+18
        y=y0+height*(.20+.37*j)
        w=min(x1-x-15,len(caption)*height*.250)
        h=height*.24
        left=(409+max(0,(x0-380)*.40)) if j==0 else (410+max(0,(x0-380)*.46))
        top=y0+(.11 if j==0 else .50)*height
        width=(381 if j==0 else 311)*(height/98)
        hh=height*.295
        lo=y0+(.01 if j==0 else .44)*height
        hi=y0+(.47 if j==0 else .84)*height
        patch,m0,m1=fit_line(src,frame,caption,[left,top,width,hh],(lo,hi),ramp,
                             [x,y,w,h,420,254,.6],(1.4,1,4,.8,16,0,.5),
                             start=[left,top,width,hh,410,250,1.1],color_fit=False)
        blue.append(patch)
        results.append(round(m0-m1,3))
    print(frame,results,flush=True)
    return str(frame),(updates,blue)

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=6) as pool:
        data=dict(pool.map(solve,range(671,673)))
    (root/'ink-fit.json').write_text(json.dumps(data,indent=2)+'\n')
