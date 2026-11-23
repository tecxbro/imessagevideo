from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
from copy import copy
from render import Film, fit_ink, layer, messages_font
from treatments import message_outline
import json
import sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def patch_box(x,y,w,h,pad=15):
    return max(0,int(x-pad)),max(0,int(y-pad)),min(1000,int(x+w+pad)),min(1000,int(y+h+pad))

def fill_message_holes(mask):
    a=mask.copy()
    for y,row in enumerate(a):
        indices=np.flatnonzero(row>.63)
        if len(indices)>5:
            a[y,indices[0]:indices[-1]+1]=1
    return a

def fit_shape(target,origin,seed,tail):
    h,w=target.shape
    vals=list(map(float,seed))
    def cost(pose):
        coverage=np.asarray(message_outline((w,h),pose,origin,supersample=2),dtype=np.float32)/255
        return float(np.abs(coverage-target).mean())
    best=cost(vals)
    for mul in (1,.5):
        for i, step in enumerate((3,2.2,3.7,2.8,4,3,3) if tail else (2,2,3,2,3)):
            prior=vals[i]
            for n in (-2,-1,1,2):
                proposal=vals.copy()
                proposal[i]=prior+n*mul*step
                if min(proposal[4:])<0 or not (3<proposal[4]<min(proposal[2:4])*.52):
                    continue
                err=cost(proposal)
                if err<best:
                    vals,best=proposal,err
    return vals

def blue_body(rgb,orig,index):
    x,y,w,h=orig
    left,top,right,bottom=patch_box(x,y,w,h,20)
    a=rgb[top:bottom,left:right]
    strength=a[:,:,1]-a[:,:,0]
    solid=a[strength>147]
    color=np.rint(np.median(solid,axis=0)).astype(int).tolist()
    mask=fill_message_holes(np.clip(strength/180,0,1))
    measured=fit_shape(mask,(left,top),
                       (x-4,y,w+4,h-1,h*(.467 if not index else .337),13,18),True)
    return [measured,[color,color]]

def text_fit(rgb,word,box,bright,amplitude,bg_color,min_width=0,weight=400):
    x,y,w,h=map(float,box)
    left,top,right,bottom=patch_box(x,y,w,h,8)
    a=rgb[top:bottom,left:right]
    # The red channel separates white type from the solid cyan background.
    dark=0 if bright else 1
    if bright:
        target=np.clip(a[:,:,0]-bg_color,0,amplitude+6)
        mask=(a[:,:,1]-a[:,:,0]<120)
        target*=mask
        safe=np.s_[max(0,int(y-top)-4):min(len(target),int(y-top+h)+5),
                  max(0,int(x-left)-3):min(target.shape[1],int(x-left+w)+9)]
        gl=target.copy()
        target[:]=0
        target[safe]=gl[safe]
    else:
        field=np.broadcast_to(bg_color,a[:,:,1].shape)
        target=np.clip(field-a[:,:,1],0,amplitude+6)
        safe=np.s_[max(0,int(y-top)-3):min(len(target),int(y-top+h)+4),
                  max(0,int(x-left)-3):min(target.shape[1],int(x-left+w)+4)]
        gl=target.copy()
        target[:]=0
        target[safe]=gl[safe]
    if (target>18).sum()<20:
        return None
    def cost(specs,frac=True):
        px,py,pw,ph,wt,amount,blur=map(float,specs)
        image=layer(right-left,bottom-top)
        fit_ink(image,word,(px-left,py-top,pw,ph),round(wt),1,blur,
                family=messages_font,ink=(0,0,0),fractional=frac)
        diff=np.abs(np.asarray(image.getchannel('A'))*amount/255-target)
        return float(diff.mean())
    vals=np.array([x,y,w,h,weight,amplitude,.45])
    best=cost(vals,False)
    before=best
    low=(x-7,y-8,w-12,max(3,h-8),340,amplitude*.53,0)
    high=(x+7,y+8,w+12,h+10,560,amplitude+11,1.8)
    for mul in (1,.55,.24):
        for i,step in enumerate((1.8,1.4,3.2,1.8,15,8,.29)):
            at=vals[i]
            for k in (-2,-1,1,2):
                s=vals.copy()
                s[i]=np.clip(at+k*mul*step,low[i],high[i])
                err=cost(s)
                if err<best:
                    vals,best=s,err
    if best>=before:
        return None
    tint=int(np.clip(bg_color+vals[5] if bright else np.median(bg_color)-vals[5],0,255))
    color=([tint, int(np.clip(tint+5,0,255)), 254] if bright else [tint]*3)
    return dict(box=np.round(vals[:4],3).tolist(),weight=round(vals[4]),blur=round(float(vals[6]),4),color=color)

def control_body(rgb, orig, label, index):
    x,y,w,h=orig
    l,t,r,b=patch_box(x,y,w,h,11)
    a=rgb[t:b,l:r]
    gray=a.mean(2)
    hue=a.max(2)-a.min(2)
    if index:
        selected=(hue>16)&(a[:,:,0]>124)&(gray>154)
    else:
        selected=(hue<11)&(gray>124)&(gray<238)
    mask=fill_message_holes(selected.astype(float))
    # Exclude the message tail and lettering on neighboring controls.
    ux=np.arange(l,r)[None,:]
    vy=np.arange(t,b)[:,None]
    mask*=((ux>=x-9)&(ux<=x+w+9)&(vy>=y-8)&(vy<=y+h+10))
    ys,xs=np.where(mask>.72)
    if len(xs)<130:
        return None
    shape=fit_shape(mask,(l,t),(x,y,w,h,h*.22,0,0),False)
    px,py,pw,ph,_,_,_=shape
    y0=int(py+ph*.21); y1=int(py+ph*.80)
    x0=int(px+pw*.08); x1=int(px+pw*.92)
    samples=rgb[y0:y1,x0:x1]
    lum=samples.mean(2)
    solid=lum>160
    if index:
        color=np.empty((2,3))
        for i, q in enumerate((.08,.93)):
            c=int(samples.shape[1]*q)
            palette=samples[:,max(0,c-3):min(samples.shape[1],c+4)]
            color[i]=np.median(palette.reshape(-1,3),axis=0)
        palette=np.rint(color).astype(int).tolist()
    else:
        g=np.rint(np.median(samples[solid],axis=0)).astype(int).tolist()
        palette=[g,g]
    text_w=pw*(.70 if index else .45)
    bbox=[px+(pw-text_w)/2,py+ph*.26,text_w,ph*.48]
    bg_color=round(float(np.median(np.asarray(palette)[:,1])))
    ink=text_fit(rgb,label,bbox,False,bg_color-31,bg_color,weight=410)
    if not ink:
        ink=dict(box=bbox,weight=410,blur=.4,color=[31,31,31])
    return [shape,palette,ink]

def investigate(f):
    frame=str(f)
    engine=Film(scene)
    rgb=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    a=np.asarray(engine.frame(f),dtype=np.float32)
    copies=scene['copy']['sofia']
    boxes=engine.track('sofiaSuggestionInk',f)
    bodies=[blue_body(rgb,engine.track(name,f),i) for i,name in
            enumerate(('sofiaEarlierReplyBounds','sofiaSuggestedBounds'))]
    ink={}
    for i,word in enumerate([copies[4],*copies[6],copies[5]]):
        box=boxes[i*4:i*4+4]
        low=15 if i<3 else 253
        delta=232 if i<3 else 108
        ref=text_fit(rgb,word,box,i<3,delta,low)
        if ref:
            ink[str(i)]=ref
    controls={}
    shape=engine.track('sofiaSettledControls',f)
    for i,label in enumerate(copies[7:9]):
        control=control_body(rgb,shape[i*4:i*4+4],label,i)
        if control:
            controls[str(i)]=control
    checks=[
        dict(messages=bodies,ink=ink,controls=controls),
        dict(messages=bodies,ink=ink),
        dict(messages=bodies,controls=controls),
        dict(messages=bodies),
    ]
    old=float(np.abs(a-rgb).mean())
    lowest=old
    adopted=None
    for row in checks:
        trial=copy(scene)
        trial['sofiaSuggestionRegistration']={frame:row}
        b=np.asarray(Film(trial).frame(f),dtype=np.float32)
        error=float(np.abs(b-rgb).mean())
        if error<lowest:
            lowest,adopted=error,row
    print(f,round(old,5),round(lowest,5),list(adopted or {}),flush=True)
    return (frame,adopted) if adopted else None

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        values=dict(row for row in pool.map(investigate,range(343,352)) if row)
    (p/'sofia-assembly-fit.json').write_text(json.dumps(values,indent=2,default=lambda x:x.item())+'\n')
