"""Fit the independent side buttons from unobstructed source rail profiles."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from casing import paint_casing_buttons
from render import Film

p=Path(sys.argv[1]); cfg=p/'project/scene.json'
s=json.loads(cfg.read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
film=Film(s)
out={}
for k,parameters in s['sofiaClosedCasing'].items():
    frame=int(k)
    reference=np.asarray(Image.open(src/f'{frame:06d}.png').convert('RGB'),np.int16)
    rendered=film.frame(frame).convert('RGBA')
    arr=np.asarray(rendered,np.int16)[:,:,:3]
    center,top,w,h,rx,ry,bx,by=parameters[0]
    lo=max(0,round(top+ry+10))
    hi=min(998,round(top+h-by-12))
    details=[]
    for side in (-1,1):
        edge=round(center+side*w/2)
        a,b=(edge-10,edge+4) if side<0 else (edge-4,edge+11)
        shallow=slice(edge-7,edge+1) if side<0 else slice(edge-1,edge+7)
        outer=reference[lo:hi,shallow,1].astype(float)
        profile=np.percentile(outer,87,axis=0)
        strength=np.max(profile[None,:]-outer,axis=1)
        group=np.flatnonzero(strength>21)
        intervals=np.split(group,np.flatnonzero(np.diff(group)>1)+1)
        for span in intervals:
            if not 10<=len(span)<=round(h*.225):
                continue
            if span[0]<4 or span[-1]>hi-lo-5:
                continue
            if np.mean(strength[span])<25:
                continue
            start,end=lo+int(span[0]),lo+int(span[-1])+1
            guard=max(2,len(span)//5)
            err=reference[start+guard:end-guard,a:b]-arr[start+guard:end-guard,a:b]
            paint=np.median(err,axis=0).tolist()
            if side<0:
                paint[-3:]=[[0,0,0]]*3
            else:
                paint[:3]=[[0,0,0]]*3
            if np.abs(paint).max()<5:
                continue
            best=0
            fitted=None
            inset=(a,start-8,b,end+8)
            l,t,r,d=inset
            original=np.abs(reference[t:d,l:r]-arr[t:d,l:r]).mean()
            for feather in (1.0,2.4,4.4):
                for opacity in (.65,.9,1.12):
                    a1=[a,start+.3,end-.3,feather,(np.asarray(paint)*opacity).round(1).tolist()]
                    v=rendered.copy()
                    paint_casing_buttons(v,[a1])
                    er=np.abs(np.asarray(v.crop(inset).convert('RGB'),np.int16)-reference[t:d,l:r]).mean()
                    if original-er>best:
                        best,fitted=original-er,a1
            if best>.7:
                details.append(fitted)
    if details:
        v=rendered.copy()
        paint_casing_buttons(v,details)
        old=np.abs(arr-reference).mean()
        now=np.abs(np.asarray(v.convert('RGB'),np.int16)-reference).mean()
        print(frame,len(details),round(old,5),round(now,5),flush=True)
        if now<old:
            out[k]=details
s['sofiaCaseButtons']=out
cfg.write_text(json.dumps(s,indent=2)+'\n')
(p/'sofia-case-buttons.json').write_text(json.dumps(out,indent=2)+'\n')
