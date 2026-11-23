"""Fit the live lettering in the two earlier gray bubbles."""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json,sys,math
from pathlib import Path
import numpy as np
from PIL import Image
from render import Film,blur,registered_message_ink,vertical_blur

w=Path(sys.argv[1])
path=w/'sofia-history-next/scene.json'
baseline=json.loads(path.read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit(frame):
    key=str(frame)
    active=deepcopy(baseline)
    stage=active['threadRegistration']['sofia'][key]
    source=np.asarray(Image.open(src/f'{frame:06d}.png').convert('RGB'),np.int16)
    # Sample neutral midtones apart from the darker text and surrounding paper.
    fill=[]
    for bounds,_ in stage['items']:
        x0,y0,x1,y1=bounds
        crop=source[max(0,round(y0+5)):min(1000,round(y1-5)),max(0,round(x0+30)):min(1000,round(x1-26))]
        pixel=crop[(crop[:,:,0]>=216)&(crop[:,:,0]<244)&(np.ptp(crop,axis=2)<13)]
        fill.append(np.median(pixel,axis=0).round().astype(int).tolist() if len(pixel)>20 else [232,232,235])
    stage['bubbleFill']=fill
    blank=deepcopy(active)
    for i in range(len(stage['items'])):
        copy=blank['copy']['sofia'][2+i]
        blank['copy']['sofia'][2+i]=[' ' for _ in copy] if isinstance(copy,list) else ' '
    background=Film(blank).frame(frame)
    stage.setdefault('inkAppearance',{})
    fx,fy,focus=stage.get('focus',[0,0,1.14+.29*min(1,abs(frame-348)/5)])
    result={}
    for i,(bounds,measurements) in enumerate(stage['items']):
        sentences=active['copy']['sofia'][i+2]
        if isinstance(sentences,str):
            sentences=[sentences]
        for j,(sentence,box) in enumerate(zip(sentences,measurements,strict=True)):
            x,y,ww,hh=box
            pad=14
            x0,y0=max(0,math.floor(x-pad)),max(0,math.floor(y-pad))
            x1,y1=min(1000,math.ceil(x+ww+pad)),min(1000,math.ceil(y+hh+pad))
            if x1-x0<10 or y1-y0<8:
                continue
            patch=background.crop((x0,y0,x1,y1)).convert('RGBA')
            compare=source[y0:y1,x0:x1]
            g=[x-x0,y-y0,ww,hh,410,.25,38,0.0]
            def metric(a):
                film=Image.new('RGBA',patch.size)
                color=int(round(a[6]))
                registered_message_ink(film,sentence,dict(box=a[:4],weight=round(a[4]),blur=a[5],
                                                        color=[color]*3,slope=a[7]))
                if fx or fy:
                    film=vertical_blur(film,fy,horizontal=fx)
                film=blur(film,(focus*.85,focus))
                return float(np.abs(np.asarray(Image.alpha_composite(patch,film),np.int16)[:,:,:3]-compare).mean())
            best=metric(g)
            for precision in (1,.53,.22):
                for k,step in enumerate((2.3,2.35,5,2.2,30,.40,14,.013)):
                    first=g.copy()
                    for direction in (-2,-1,1,2):
                        variant=first.copy()
                        variant[k]+=direction*step*precision
                        if variant[5]<.05 or not 305<=variant[4]<=515 or not 15<=variant[6]<=146:
                            continue
                        error=metric(variant)
                        if error<best:
                            best,g=error,variant
            a,b,ww,hh,weight,local,pigment,slope=g
            result[f'{i}:{j}']=dict(box=[round(z,4) for z in (x0+a,y0+b,ww,hh)],weight=round(weight),
                                  blur=round(local,4),color=[round(pigment)]*3,slope=round(slope,5))
    stage['inkAppearance'].update(result)
    before,after=(np.asarray(Film(s).frame(frame),np.int16) for s in (baseline,active))
    a,b=[float(np.abs(out-source).mean()) for out in (before,after)]
    print(frame,round(a,5),round(b,5),flush=True)
    return key,dict(inkAppearance=stage['inkAppearance'],bubbleFill=fill) if b<a else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        accepted={f:value for f,value in pool.map(fit,range(330,343)) if value}
    for f,value in accepted.items():
        baseline['threadRegistration']['sofia'][f].update(value)
    path.write_text(json.dumps(baseline,indent=2)+'\n')
    (w/'sofia-history-fit.json').write_text(json.dumps(accepted,indent=2)+'\n')
