from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import interpolate,layer,revealed_caption

p=Path(sys.argv[1])
scene=json.loads((p/'clean/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
specs=scene['tracks']
def solve(frame):
    source_img=Image.open(source/f'{frame:06}.png').convert('RGB')
    rendered=Image.open(p/'clean-frames'/f'{frame:06}.png').convert('RGB')
    lines=[]
    for index,caption in enumerate(scene['copy']['assistant']):
        axis=specs[f'assistantLettering{index+1}']
        if frame<axis[0][0]:
            lines.append(None)
            continue
        base=list(interpolate(axis,frame))
        cx,cy,w,h,alpha,shear,until,softedge,softness=base
        l,t,r,b=int(cx)-16,int(cy+min(0,shear))-10,int(cx+w)+19,int(cy+h+max(shear,0))+9
        if index==0:
            y_stop=interpolate(specs['assistantLettering2'],frame)[1]
            b=min(b,round(y_stop)-6)
        else:
            y_start=int(interpolate(specs['assistantLettering1'],frame)[1]+
                        interpolate(specs['assistantLettering1'],frame)[3])
            t=max(y_start+4,t)
        rect=(l,t,r,b)
        src=np.asarray(source_img.crop(rect),dtype=np.float32)
        ref=np.asarray(rendered.crop(rect),dtype=np.float32)
        paper=np.broadcast_to(np.median(np.stack((src[:,:4],src[:,-4:])),axis=(0,2))[:,None],src.shape)
        color=np.clip(paper-src,0,255)
        before=float(np.abs(src-ref).mean())
        def cost(v):
            patch=layer(r-l,b-t)
            pos=v.copy();pos[0]-=l;pos[1]-=t
            revealed_caption(patch,caption,list(map(float,pos)))
            channel=np.asarray(patch.getchannel('A'),dtype=np.float32)*paper.mean(2)/255
            return float(np.abs(channel[:,:,None]-color).mean())
        best=cost(base)
        for step in (1,.5,.25):
            for i,stride in enumerate((1.8,2.4,3.5,2.3,.054,3.1,.078,.072,.58)):
                at=base[i]
                for n in (-2,-1,1,2):
                    trial=base.copy();trial[i]=at+step*stride*n
                    if not .01<trial[4]<=1 or not .04<=trial[6]<=1.18 or not .035<=trial[7]<=.65 or not .25<=trial[8]<=5.8:
                        continue
                    loss=cost(trial)
                    if loss<best:
                        base,best=trial,loss
        result=[round(float(v),5) for v in base]
        print(frame,index,round(before,5),round(best,5),result,flush=True)
        lines.append(result if best<before-.13 else None)
    return str(frame),lines

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=dict(pool.map(solve,range(135,155)))
    (p/'next-assistant-lettering.json').write_text(json.dumps(results,indent=2)+'\n')
