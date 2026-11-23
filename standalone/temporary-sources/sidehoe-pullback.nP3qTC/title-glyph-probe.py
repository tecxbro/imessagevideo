import json
from functools import lru_cache
from pathlib import Path
import sys
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.optimize import minimize

p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from artwork import messages_font
from render import interpolate
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-follow-entry.0vQCoz/final-dual-frames')

@lru_cache(maxsize=100)
def masks(word,weight):
    font=messages_font(190,weight)
    w=int(font.getlength(word)+100)
    fields=[]
    for i,char in enumerate(word):
        x=25+font.getlength(word[:i+1])-font.getlength(char)
        a=Image.new('L',(w,245))
        ImageDraw.Draw(a).text((x,7),char,font=font,fill=255,anchor='la')
        box=a.getbbox()
        fields.append((box,np.asarray(a.crop(box),dtype=np.float32)/255))
    return fields, np.array([min(q[0][0] for q in fields),min(q[0][1] for q in fields),
                              max(q[0][2] for q in fields),max(q[0][3] for q in fields)])

results={}
for frame in (188,190,192,195,198,201,204,206):
    ref,old=[np.asarray(Image.open(d/f'{frame:06d}.png').convert('RGB'),dtype=np.float32) for d in (source,prior)]
    specs=[]
    pose=s['tracks']['personalWordRegistration']
    colors=[interpolate(t,frame)[-3:] for t in s['tracks']['personalLettering']]
    reconstructed=old.copy()
    for line,caption in enumerate(s['copy']['personal']):
        controls=interpolate(pose[line],frame)
        line_patches=[]
        for wi,word in enumerate(caption.split()):
            x,y,w,h,weight,focus,level=controls[wi*7:wi*7+7]
            letter_shapes,all_box=masks(word,weight)
            ext_w,ext_h=all_box[2:]-all_box[:2]
            lefts=[]
            for glyph,(g,template) in enumerate(letter_shapes):
                l,t,r,b=g
                center=[x+(l-all_box[0])*w/ext_w,y+(t-all_box[1])*h/ext_h,
                        (r-l)*w/ext_w,(b-t)*h/ext_h]
                lefts.append(center)
            for glyph,((_,alph),initial) in enumerate(zip(letter_shapes,lefts)):
                gx,gy,gw,gh=initial
                a=max(0,int(gx)-4);v=max(0,int(gy)-4)
                A=min(999,int(gx+gw)+5);V=min(999,int(gy+gh)+5)
                if glyph>0:
                    edge=(lefts[glyph-1][0]+lefts[glyph-1][2]+gx)/2
                    a=max(a,int(edge)-1)
                if glyph+1<len(lefts):
                    edge=(gx+gw+lefts[glyph+1][0])/2
                    A=min(A,int(edge)+2)
                ys,xs=np.mgrid[v:V,a:A]
                true=ref[v:V,a:A]
                old_crop=old[v:V,a:A]
                sr,sg,sb=np.moveaxis(true,2,0)
                # Work where the pink hearts did not tint either rendering.
                clean=(true.max(2)-true.min(2)<(18 if not line else 36))&(old_crop.max(2)-old_crop.min(2)<(22 if not line else 39))
                if line==0:
                    next_line=interpolate(s['tracks']['personalLettering'][1],frame)[1]
                    clean &= (ys<next_line+3)|(xs>345)
                ink=np.array(colors[line])
                paper=np.median(true[true[:,:,1]>231],axis=0) if np.count_nonzero(true[:,:,1]>231)>5 else np.array([253]*3)
                aim=(paper[1]-sg)/max(1,paper[1]-ink[1])
                bounds=[(gx-4,gx+4),(gy-3.5,gy+3.5),
                        (max(1,gw*.81),gw*1.20+1),(max(2,gh*.88),gh*1.1+1),
                        (.15,2.3),(.72,1.04)]
                init=[*initial,np.clip(focus,.15,2.3),np.clip(level,.72,1.04)]
                def draw(q):
                    xx,yy,ww,hh,fog,oc=q
                    sx=(xs+.5-xx)*alph.shape[1]/ww-.5
                    sy=(ys+.5-yy)*alph.shape[0]/hh-.5
                    z=map_coordinates(alph,(sy,sx),order=1,mode='grid-constant',prefilter=False)
                    return gaussian_filter(z*oc,fog,mode='constant')
                def error(q):
                    z=draw(q)
                    e=np.abs(z-aim)
                    return np.mean((e+e**2*.8)[clean])
                if clean.sum()<15:
                    best=init
                else:
                    fit=minimize(error,init, method='Powell',bounds=bounds,
                                 options={'maxiter':22,'xtol':.006,'ftol':.002})
                    best=fit.x if fit.fun<error(init) else init
                result=np.array(best)
                pixel=paper*(1-draw(result)[...,None])+ink*draw(result)[...,None]
                reconstructed[v:V,a:A][clean]=pixel[clean]
                line_patches.append([wi,glyph,*np.round(result,4).tolist(),round(float(error(init)),5),
                                     round(float(error(result)),5)] if clean.any() else [])
        specs.append(line_patches)
    label=np.array([173,386,836,602])
    l,t,r,b=label
    print(frame,round(np.abs(ref[t:b,l:r]-old[t:b,l:r]).mean(),4),
          round(np.abs(ref[t:b,l:r]-reconstructed[t:b,l:r]).mean(),4),flush=True)
    results[frame]=specs
    if frame==190:
        Image.fromarray(np.uint8(np.clip(reconstructed,0,255))).crop(tuple(label)).save(p/'glyph-testing.png')
(p/'glyph-probe.json').write_text(json.dumps(results,indent=2)+'\n')
