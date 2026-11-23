from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'profile-next/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
anchors=scene['profileMotionRegistration']['267']['actors']
name_chars=((0,0,0),(1,0,0),(1,1,0),(2,1,0),(3,1,1),(4,1,1),(4,2,2))
tag_chars=((1,0,0),(4,0,0),(7,2,0),(8,4,0),(9,6,1),(11,9,2),(12,11,7))

def native_rect(mask,box,min_count=12):
    l,t,r,b=[int(v) for v in box]
    l,t,r,b=max(0,l),max(0,t),min(1000,r),min(1000,b)
    yy,xx=np.where(mask[t:b,l:r])
    if xx.size<min_count:
        return None
    return int(l+xx.min()),int(t+yy.min()),int(l+xx.max()+1),int(t+yy.max()+1)

def fit(f):
    frame=str(f)
    film=Film(scene)
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    before=np.asarray(film.frame(f),dtype=np.int16)
    red,green,blue=np.moveaxis(target,2,0)
    luma=target.mean(2)
    actors=[]
    for i,(name,*_) in enumerate(scene['profiles']):
        anchor=anchors[i]
        track='profileArrival'+name
        if f<scene['tracks'][track][0][0]:
            actors.append(None)
            continue
        x,y,r,softness=film.track(track,f)
        chroma=(green-red>22)&(green-blue>16) if i==0 else (
            ((red-green>31)&(blue-green>12)&(luma>103)) if i==1 else
            ((red-blue>44)&(green-blue>24)&(luma>111)))
        box=native_rect(chroma,(x-r-16,y-r-24,x+r+16,min(589,y+r+27)),150)
        if not box:
            actors.append(None)
            continue
        l,t,rr,b=box
        wid,hei=rr-l,b-t
        cx,cy=(l+rr)/2,(t+b)/2
        # Use the measured ellipse through the reveal and reuse the independently authored head.
        a=deepcopy(anchor)
        ox,oy,ow,oh=anchor['oval']
        a['oval']=[cx,cy,wid,hei]
        a['head']=[round(cx+(anchor['head'][0]-ox)*wid/ow,2),
                   round(cy+(anchor['head'][1]-oy)*hei/oh,2),
                   round(cx+(anchor['head'][2]-ox)*wid/ow,2),
                   round(cy+(anchor['head'][3]-oy)*hei/oh,2)]
        a['veil']=1
        a['headFocus']=[round(max(.25,(softness*.46)-1.0),2),
                        round(max(.25,(softness*.47)-1.0),2)]
        ink=(luma<161)&((target.max(2)-target.min(2))<56)
        a['nameCharacters']=name_chars[f-260][i]
        text=native_rect(ink,(cx-70,b+4,cx+70,607))
        if text and a['nameCharacters']:
            xx,yy,zz,vv=text
            a['name']=[xx,yy,zz-xx,vv-yy]
            a['nameFocus']=round(max(.4,softness*.24),3)
            a['nameOpacity']=1 if f>=263 else .85
        else:
            a['nameCharacters']=0
        accent=(green-red>5)&(green-blue>5)&(luma>226) if i==0 else (
            ((red-green>7)&(blue-green>8)&(luma>226)) if i==1 else
            ((red-blue>10)&(red-green>2)&(luma>227)))
        chunk=native_rect(accent,(cx-168,605,cx+168,694),160)
        a['chip']=None
        if chunk:
            left,top,right,bottom=chunk
            if right-left>=20 and bottom-top>=9:
                a['chip']=list(chunk)
                box=target[top:bottom,left:right]
                colors=box[(box.max(2)-box.min(2)>7)&(box.mean(2)>228)]
                a['chipColor']=np.rint(np.median(colors,axis=0)).astype(int).tolist() if colors.size else a['chipColor']
                dw,dh=(right-left),(bottom-top)
                # Keep the tag glyph independent of the incoming letter masks.
                mask=(luma<184)&((target.max(2)-target.min(2))>19)
                z=native_rect(mask,(left+5,top+2,left+dw*.34,bottom-2))
                a['glyph']=None
                if z:
                    ll,tt,rr,bb=z
                    a['glyph']=[ll,tt,rr-ll,bb-tt]
                a['tagCharacters']=tag_chars[f-260][i]
                body=(green-red>30)&(green-blue>24) if i==0 else (
                    ((red-green>33)&(blue-green>46)) if i==1 else
                    ((red-blue>59)&(green-blue>25)))
                z=native_rect(body,(left+dw*.27,top+3,right-9,bottom-3))
                if z:
                    ll,tt,rr,bb=z
                    a['text']=[ll,tt,rr-ll,bb-tt]
                else:
                    a['tagCharacters']=0
                a['chipFocus']=round(max(.6,softness*.19),3)
        actors.append(a)
    candidate=copy(scene)
    candidate['profileMotionRegistration']=copy(scene['profileMotionRegistration'])
    old=float(np.abs(before-target).mean())
    best=old
    chosen=None
    for focus in ((1.4,1.1),(2.6,2.0),(3.6,3.0)):
        data={'actors':actors,'focus':focus}
        candidate['profileMotionRegistration'][frame]=data
        image=np.asarray(Film(candidate).frame(f),dtype=np.int16)
        error=float(np.abs(image-target).mean())
        if error<best:
            best,chosen=error,data
    print(f,round(old,5),round(best,5),flush=True)
    return (frame,chosen) if chosen else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=dict(z for z in pool.map(fit,range(260,267)) if z)
    (p/'profile-arrival-next.json').write_text(json.dumps(rows,indent=2)+'\n')
