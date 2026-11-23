"""Fit separate perspective and local shutter exposures from decoded key crops."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from render import Film, exposed_key_ink

p=Path(sys.argv[1])
cfg=p/'sofia-keys-next/scene.json'
base=json.loads(cfg.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
alphabet=('QWERTYUIOP','ASDFGHJKL','ZXCVBNM')


def fit(frame):
    k=str(frame)
    film=Film(base)
    target=Image.open(source/f'{frame:06d}.png').convert('RGB')
    prior=film.frame(frame)
    scene=json.loads(cfg.read_text())
    data=scene['threadRegistration']['sofia'][k]
    data['keyInkRegistration']=[[[] for _ in row] for row in alphabet]
    blank=Film(scene).frame(frame).convert('RGBA')
    item=[]
    for letters,(x,y,pitch,w,h,count) in zip(alphabet,data['keys'][2]):
        row=[]
        for i,letter in enumerate(letters):
            cx=x+pitch*i+w*.5
            left,top=max(0,round(cx-w*.49)),max(0,round(y+h*.12))
            right,bottom=min(1000,round(cx+w*.52)),min(1000,round(y+h*.88))
            if right-left<8 or bottom-top<8:
                row.append(None)
                continue
            box=(left,top,right,bottom)
            target_array=np.asarray(target.crop(box),np.int16)
            untreated=np.asarray(prior.crop(box),np.int16)
            if min(target_array.shape[:2])<8:
                row.append(None)
                continue
            matte=blank.crop(box)
            neutral=np.asarray(matte,np.int16)[:,:,:3]
            yy,xx=np.mgrid[:matte.height,:matte.width]
            # Use darker pixels against the rendered white face to locate the ink.
            stroke=np.clip(np.mean(neutral-target_array,axis=2)-33,0,220)
            stroke[(xx<1)|(yy<1)|(xx>=matte.width-1)|(yy>=matte.height-1)]=0
            support=np.where(stroke>34)
            if len(support[0])<8 or not stroke.sum():
                row.append(None)
                continue
            miny,maxy=int(support[0].min()),int(support[0].max())
            minx,maxx=int(support[1].min()),int(support[1].max())
            obsx=(minx+maxx)/2
            obsy=(miny+maxy)/2
            w0=max(5,(maxx-minx)*.95)
            h0=max(12,(maxy-miny)*.94)
            g=[obsx,obsy,w0,h0,0.,0.,0.,3.,2.2,.77]
            def cost(params):
                stage=matte.copy()
                exposed_key_ink(stage,letter,params)
                return float(np.abs(np.asarray(stage,np.int16)[:,:,:3]-target_array).mean())
            initial=float(np.abs(untreated-target_array).mean())
            best=cost(g)
            for scale in (1,.53,.24):
                for j,step in enumerate((1.2,1.3,2.4,2.7,.18,.17,3.,3.1,.67,.14)):
                    start=g.copy()
                    for n in (-2,-1,1,2):
                        sample=start.copy()
                        sample[j]+=n*step*scale
                        if not (3<=sample[2]<w*.82 and 8<=sample[3]<h*.78 and
                                abs(sample[4])<.6 and abs(sample[5])<.6 and abs(sample[6])<=18 and
                                0<=sample[7]<=16 and .2<=sample[8]<=7 and .14<=sample[9]<=1):
                            continue
                        if abs(sample[0]-obsx)>7 or abs(sample[1]-obsy)>7:
                            continue
                        c=cost(sample)
                        if c<best:
                            g,best=sample,c
            row.append([round(a,4) for a in [g[0]+left,g[1]+top,*g[2:]]] if best+.10<initial else None)
        item.append(row)
    data['keyInkRegistration']=item
    original=np.asarray(prior,np.int16)
    rounded=np.asarray(Film(scene).frame(frame),np.int16)
    target=np.asarray(target,np.int16)
    a,b=np.abs(original-target),np.abs(rounded-target)
    print(frame,'global',round(a.mean(),5),round(b.mean(),5),'keys',round(a[690:,150:855].mean(),5),
          round(b[690:,150:855].mean(),5),'selected',sum(v is not None for r in item for v in r),flush=True)
    return k,item if b.mean()<a.mean() else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        output={k:v for k,v in pool.map(fit,range(336,343)) if v}
    scene=json.loads(cfg.read_text())
    for k,v in output.items():
        scene['threadRegistration']['sofia'][k]['keyInkRegistration']=v
    cfg.write_text(json.dumps(scene,indent=2)+'\n')
    (p/'sofia-key-ink-fit.json').write_text(json.dumps(output,indent=2)+'\n')
