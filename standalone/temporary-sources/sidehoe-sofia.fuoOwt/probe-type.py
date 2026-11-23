from pathlib import Path
from PIL import Image
import numpy as np
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import json,sys,math
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film,fit_ink,messages_font,measured_wash,interpolate,title_heart
scene=json.loads((root/'project/scene.json').read_text())
scene['titleHeartOptics'].update(json.loads((root/'hearts-fit.json').read_text()))
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def fit(f):
    candidate=deepcopy(scene)
    film=Film(candidate)
    ref=np.array(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    before=np.array(film.frame(f),dtype=np.int16)
    base=Image.new('RGBA',(1000,1000),film.palette['paper'])
    base.alpha_composite(measured_wash(tuple(film.track('titleWashFields',f))))
    all_glyphs=[]
    for line, (definition,words,colorpath) in enumerate(zip(candidate['personalGlyphRegistration'],candidate['tracks']['personalWordRegistration'],candidate['tracks']['personalLettering'])):
        weights=interpolate(words,f)
        color=tuple(round(x) for x in interpolate(colorpath,f)[-3:])
        shapes=definition['frames'][str(f)]
        k=0
        for j,part in enumerate(definition['caption'].split()):
            weight=weights[j*7+4]
            for letter in part:
                v=shapes[k]
                all_glyphs.append((line,k,letter,color,[*v,weight]))
                k+=1
    frames=candidate['titleHeartOptics'][str(f)]
    positions=[p for l,i,ch,c,p in all_glyphs]
    for n,(line,i,letter,ink,pose) in enumerate(all_glyphs):
        x,y,w,h,focus,opacity,weight=pose
        l,t,r,b=math.floor(x)-4,math.floor(y)-4,math.ceil(x+w)+4,math.ceil(y+h)+4
        if l<0 or t<0 or r>1000 or b>1000:
            continue
        roi=(l,t,r,b)
        a=base.crop(roi)
        source_pixels=ref[t:b,l:r]
        hud=Image.new('RGBA',a.size)
        def draw(image,caption,color,values):
            x,y,w,h,focus,opacity,weight=values
            fit_ink(image,caption,(x-l,y-t,w,h),weight,min(1,opacity),focus,
                    family=messages_font,ink=color,fractional=True)
        neighbor=[]
        for k,((_,_,ch,c,v),pos) in enumerate(zip(all_glyphs,positions,strict=True)):
            if k==n:
                continue
            nx,ny,nw,nh=pos[:4]
            if r+2>nx and b+2>ny and l-2<nx+nw and t-2<ny+nh:
                if k<n:
                    draw(a,ch,c,pos)
                else:
                    neighbor.append((ch,c,pos))
        for heart in frames:
            hx,hy,hw,hh=heart[:4]
            limit=max(hw,hh)*.68+6
            if min(hx+limit,r)>max(hx-limit,l) and min(hy+limit,b)>max(hy-limit,t):
                pp=heart[:];pp[0]-=l;pp[1]-=t
                title_heart(hud,pp)
        def score(v):
            drawn=a.copy()
            draw(drawn,letter,ink,v)
            for ch,c,ns in neighbor:
                draw(drawn,ch,c,ns)
            drawn.alpha_composite(hud)
            diff=np.abs(np.array(drawn.convert('RGB'),dtype=np.int16)-source_pixels)
            return diff.mean()
        best=score(pose)
        result=pose[:]
        moves=[(-1.04,-.62,-.27,0,.27,.62,1.04),(-.95,-.5,-.25,0,.25,.5,.95),
               (-.9,-.5,0,.48,.85),(-.8,-.4,0,.4,.8),
               (-.28,-.15,0,.14,.27),(-.035,0,.03),(-38,-21,0,20,38)]
        for coord,steps in enumerate(moves):
            for delta in steps:
                test=result[:];test[coord]=round(pose[coord]+delta,4)
                error=score(test)
                if error<best:
                    best=error;result=test
        positions[n]=result
        target=candidate['personalGlyphRegistration'][line]['frames'][str(f)]
        target[i]=result
    after=np.array(Film(candidate).frame(f),dtype=np.int16)
    record=[d['frames'][str(f)] for d in candidate['personalGlyphRegistration']]
    return f,np.abs(ref-before).mean(),np.abs(ref-after).mean(),record
output={}
with ThreadPoolExecutor(max_workers=5) as pool:
    for f,a,b,q in pool.map(fit,range(186,207)):
        print(f,round(a,6),round(b,6),flush=True)
        if b<a:
            output[f]=q
(root/'type-fit.json').write_text(json.dumps(output,indent=2)+'\n')
