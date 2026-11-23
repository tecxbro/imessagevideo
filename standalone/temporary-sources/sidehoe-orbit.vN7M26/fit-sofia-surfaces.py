"""Fit cyan outlines and live lettering independently through the suggestion push."""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image
from render import Film,blur,registered_message_ink
from treatments import paint_message_surface

w=Path(sys.argv[1])
cfg=w/'project/scene.json'
base=json.loads(cfg.read_text())
stage=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def area(f):
    k=str(f)
    old=base['sofiaSuggestionRegistration'][k]
    t=deepcopy(old)
    image=Image.open(stage/f'{f:06d}.png').convert('RGB')
    source=np.asarray(image,np.int16)
    existing=Film(base).frame(f)
    new={**base,'sofiaSuggestionRegistration':{**base['sofiaSuggestionRegistration'],k:t}}
    shapes=[]
    for idx,(pose,palette) in enumerate(old["messages"]):
        x,y,ww,h,r,tw,th=pose
        pad=18
        bounds=(max(0,round(x-pad)),max(0,round(y-pad)),min(1000,round(x+ww+tw+pad)),min(1000,round(y+h+pad)))
        left,top,right,bottom=bounds
        target=source[top:bottom,left:right]
        # Score the silhouette outside the central span containing lettering.
        rr=target[:,:,0]
        y_rows,x_cols=np.ogrid[top:bottom,left:right]
        restricted=(y_rows<y-3)|(y_rows>y+h+8)
        prior_scope=~restricted|((target[:,:,2]-rr)>40)
        mask=np.clip((245-rr)/224,0,1)
        lettering=(y_rows>y+h*.19)&(y_rows<y+h*.83)&(x_cols>x+ww*.12)&(x_cols<x+ww*.90)
        weight=np.where(lettering,.12,1)*prior_scope
        colors=[]
        for low,high in ((.10,.30),(.67,.87)):
            tone=(rr<100)&(x_cols>=x+ww*low)&(x_cols<=x+ww*high)&(y_rows>y+.14*h)&(y_rows<y+.84*h)
            colors.append(np.median(target[tone],axis=0).round().astype(int).tolist() if np.any(tone) else palette[len(colors)])
        g=[*pose,0]
        def cost(q):
            patch=Image.new('RGBA',(right-left,bottom-top))
            paint_message_surface(patch,[q[0]-left,q[1]-top,*q[2:]],colors)
            alpha=np.asarray(patch.getchannel('A'),float)/255
            return float(np.mean(np.abs(mask-alpha)*weight))
        score=cost(g)
        for precision in (1,.52,.24):
            for i,step in enumerate((1.7,2.,3.5,2.5,2.2,3.,4.,.011)):
                saved=g.copy()
                for n in (-2,-1,1,2):
                    trial=saved.copy()
                    trial[i]+=n*step*precision
                    if trial[4]<5 or trial[5]<2 or trial[6]<3:
                        continue
                    c=cost(trial)
                    if c<score:
                        score,g=c,trial
        shapes.append([[round(v,5) for v in g],colors])
    t['messages']=shapes
    # Build the painted background once, then refine each live caption against its own crop.
    fills=Image.new('RGBA',(1000,1000),(250,250,250,255))
    for q,c in shapes:
        paint_message_surface(fills,q,c)
    copy=base['copy']['sofia']
    for idx,title in enumerate((copy[4],*copy[6],copy[5])):
        key=str(idx)
        ink=t['ink'][key]
        x,y,ww,h=ink['box']
        pad=7
        left,top=max(0,round(x-pad)),max(0,round(y-pad))
        right,bottom=min(1000,round(x+ww+pad)),min(1000,round(y+h+pad))
        q=(left,top,right,bottom)
        area=source[top:bottom,left:right]
        blank=fills.crop(q)
        arr=np.asarray(blank,np.int16)[:,:,:3]
        m=np.ones(area.shape[:2],dtype=float)
        if idx<3:
            # The target blue window has a stable interior.
            m[(arr[:,:,0]>150)|(area[:,:,2]<130)]=.14
        spec={**ink,'box':[x-left,y-top,ww,h]}
        params=[*spec['box'],spec['weight'],spec['blur'],spec['color'][0],0]
        def calc(data):
            q=blank.copy()
            color=[int(np.clip(data[6]+d,0,255)) for d in (
                0,spec['color'][1]-spec['color'][0],spec['color'][2]-spec['color'][0])]
            registered_message_ink(q,title,{'box':data[:4],'weight':round(data[4]),'blur':data[5],
                                          'color':color,'slope':data[7]})
            test=np.asarray(q,np.int16)[:,:,:3]
            return float(np.mean(np.abs(test-area)*m[:,:,None]))
        best=calc(params)
        for precision in (1,.54,.24):
            for i,step in enumerate((1.9,2.4,3.5,1.9,24,.32,11,.009)):
                old_param=params.copy()
                for n in (-2,-1,1,2):
                    t0=old_param.copy()
                    t0[i]+=n*step*precision
                    if t0[5]<.05 or not 310<=t0[4]<=500 or not 120<=t0[6]<=254:
                        continue
                    cc=calc(t0)
                    if cc<best:
                        params,best=t0,cc
        dx,dy,ww,hh,weight,focus,pigment,slope=params
        color=[int(np.clip(pigment+v-spec['color'][0],0,255)) for v in spec['color']]
        t['ink'][key]={'box':[round(v,5) for v in (left+dx,top+dy,ww,hh)],'weight':round(weight),
                       'blur':round(focus,4),'color':color,'slope':round(slope,5)}
    old_full=float(np.abs(np.asarray(existing,np.int16)-source).mean())
    final=np.asarray(Film(new).frame(f),np.int16)
    new_full=float(np.abs(final-source).mean())
    print(f,round(old_full,6),round(new_full,6),[q[0][-1] for q in shapes],flush=True)
    return k,t if new_full<old_full else None


if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        out={f:v for f,v in pool.map(area,range(340,347)) if v}
    base['sofiaSuggestionRegistration'].update(out)
    (w/'sofia-surface-fit.json').write_text(json.dumps(out,indent=2)+'\n')
    cfg.write_text(json.dumps(base,indent=2)+'\n')
