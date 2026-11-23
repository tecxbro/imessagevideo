from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
from render import Film, fit_ink, messages_font, layer
import json
import sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def tune(args):
    name,f=args
    reg=scene['threadRegistration'][name].get(str(f))
    if not reg:
        return
    raw=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16).mean(2)
    base=np.asarray(Image.open(p/'clean-frames'/f'{f:06}.png').convert('RGB'),dtype=np.int16).mean(2)
    payload={}
    for i,(pill,rects) in enumerate(reg['items'][:2 if name=='sofia' else 1]):
        lines=scene['copy'][name][i+2]
        if isinstance(lines,str):
            lines=[lines]
        for j,(word,rect) in enumerate(zip(lines,rects)):
            x,y,w,h=rect
            left=max(0,int(x-13))
            top=max(0,int(y-10))
            right=min(999,int(x+w+20))
            bottom=min(999,int(y+h+13))
            if j:
                top=max(top,int(rects[j-1][1]+rects[j-1][3])+3)
            if j+1<len(rects):
                bottom=min(bottom,int(rects[j+1][1])-3)
            a=raw[top:bottom,left:right].astype(np.float32)
            if a.shape[0]<13 or a.shape[1]<40:
                continue
            back=np.percentile(a,83,axis=1)
            target=np.clip(back[:,None]-a,0,255)
            visible=target>8
            if visible.sum()<110:
                continue
            yy,xx=np.where(visible)
            inbox=np.flatnonzero(visible.sum(1)>max(3,w*.015))
            if not inbox.size:
                continue
            x0=left+np.percentile(xx,1)
            y0=top+inbox[0]
            full_w=np.percentile(xx,99)-np.percentile(xx,1)+2
            full_h=inbox[-1]-inbox[0]+1
            ink_weight=410 if not i or name=='sofia' else 440
            ink_rgb=114 if name=='follow' and not i else 34
            coverage=np.clip(np.median(back)-np.percentile(a[visible],17),38,225)
            q=np.array([x,y,w,h,ink_weight,max(40,np.median(back)-ink_rgb),.25],dtype=float)
            def predict(params,fractional=True):
                x0,y0,w,h,weight,amount,spread=map(float,params)
                picture=layer(right-left,bottom-top)
                fit_ink(picture,word,(x0-left,y0-top,w,h),round(weight),1,spread,
                        family=messages_font,ink=(0,0,0),fractional=fractional)
                alpha=np.asarray(picture.getchannel('A'),dtype=np.float32)/255
                return alpha*amount
            def cost(params, fractional=True):
                data=predict(params,fractional)
                diff=np.abs(data-target)
                return float(diff.mean()+.24*diff[visible].mean())
            sofar=cost(q,False)
            start=q.copy()
            sc=q.copy()
            measured=(x0,y0,full_w,full_h,ink_weight,coverage,.45)
            if cost(measured)<cost(sc):
                sc=np.array(measured)
            best=cost(sc)
            low=(x-12,y-12,w-22,max(12,h-11),350,33,0)
            high=(x+12,y+12,w+22,h+14,480,240,1.9)
            for scale in (1,.60,.31):
                for k,step in enumerate((1.6,1.3,3.2,1.9,15,7,.28)):
                    value=sc[k]
                    for direction in (-2,-1,1,2):
                        v=sc.copy()
                        v[k]=np.clip(value+direction*step*scale,low[k],high[k])
                        e=cost(v)
                        if e<best:
                            best,sc=e,v
            if best<sofar:
                rendered_ink=int(np.clip(np.median(back)-sc[5],0,255))
                payload[f'{i}:{j}']={'box':np.round(sc[:4],3).tolist(),
                    'weight':int(round(sc[4])), 'color':[rendered_ink]*3,
                    'blur':round(sc[6],3),'error_before':sofar,'error_after':best}
    if payload:
        return (f'{name}:{f}',payload)

if __name__=='__main__':
    tasks=[('sofia',f) for f in range(343,352)]+[('follow',f) for f in range(671,694)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        result=dict(z for z in pool.map(tune,tasks) if z is not None)
    (p/'next-reply-ink-fit.json').write_text(json.dumps(result,indent=2)+'\n')
    print('fitted frames',len(result),'lines',sum(len(v) for v in result.values()),flush=True)
