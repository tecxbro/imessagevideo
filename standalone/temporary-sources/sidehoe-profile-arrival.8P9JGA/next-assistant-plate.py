from concurrent.futures import ProcessPoolExecutor
from copy import copy, deepcopy
from pathlib import Path
from PIL import Image
from render import Film, fit_ink, layer, messages_font
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'assistant-next/scene.json').read_text())
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
held=scene['inboxHeldRegistration']['34']['pinHeadPoses']
native_heads=[held[0],held[2]]
zero=np.asarray([1,1,0,0,0])

def plates(f):
    key=str(f)
    native=np.asarray(Image.open(ref/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    prev=np.asarray(Image.open(p/'clean-frames'/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    data=copy(scene)
    data['assistantScreenRegistration']=copy(scene['assistantScreenRegistration'])
    data['assistantCaptionOptics']=copy(scene['assistantCaptionOptics'])
    stage=Film(data)
    plate=deepcopy(scene['assistantScreenRegistration'].get(key,{}))
    data['assistantScreenRegistration'][key]=plate
    best=float(np.abs(native-prev).mean())
    original=best
    head_poses=[zero.tolist(),zero.tolist()]
    for actor in range(2):
        old=head_poses[actor]
        current=old
        for mix in (.45,.75,1,1.19):
            shape=(zero+(np.asarray(native_heads[actor])-zero)*mix).tolist()
            head_poses[actor]=shape
            plate['headPoses']=head_poses
            score=float(np.abs(native-np.asarray(stage.frame(f),dtype=np.float32)).mean())
            if score<best:
                current,best=shape,score
        head_poses[actor]=current
    plate['headPoses']=head_poses

    # Find the visible title's outline and exposure using the generated font masks.
    pair=[]
    for index,line in enumerate(scene['copy']['assistant']):
        x,y,w,h=stage.track('assistantLine'+str(index+1),f)
        l,t,r,b=max(0,int(x-8)),max(0,int(y-9)),min(1000,int(x+w+10)),min(1000,int(y+h+11))
        region=native[t:b,l:r].mean(2)
        color=253-np.clip(region,0,253)
        observed=color>46
        if observed.sum()<370:
            return key,plate,None,original,best
        yy,xx=np.where(observed)
        intensity=np.clip(float(np.percentile(color[observed],75))/245,.45,1)
        bounds=[l+xx.min(),t+yy.min(),xx.max()-xx.min()+1,yy.max()-yy.min()+1]
        default=[x,y,w,h,564,intensity,.7,.7]
        guess=[*bounds,564,intensity,.7,.7]
        def cost(v):
            x,y,w,h,weight,opacity,bx,by=map(float,v)
            canvas=layer(r-l,b-t)
            fit_ink(canvas,line,(x-l,y-t,w,h),int(weight),opacity,(bx,by),
                    family=messages_font,ink=(8,8,8),fractional=True)
            a=np.asarray(canvas.getchannel('A'),dtype=np.float32)*245/255
            return float(np.abs(a-color).mean())
        opts=default if cost(default)<cost(guess) else guess
        best_ink=cost(opts)
        for mul in (1,.5,.25):
            for i,step in enumerate((1.3,1.6,2.9,2.4,17,.06,.27,.35)):
                n=opts[i]
                for direction in (-2,-1,1,2):
                    curr=opts[:]
                    curr[i]=n+direction*step*mul
                    curr[5]=max(.1,min(1,curr[5]))
                    curr[6]=max(0,curr[6])
                    curr[7]=max(0,curr[7])
                    res=cost(curr)
                    if res<best_ink:
                        opts,best_ink=curr,res
        pair.append([round(float(v),5) for v in opts])
    data['assistantCaptionOptics'][key]=pair
    a=np.asarray(stage.frame(f),dtype=np.float32)
    value=float(np.abs(a-native).mean())
    if value<best:
        return key,plate,pair,original,value
    return key,plate,None,original,best

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        output={}
        for f,hardware,caption,a,b in pool.map(plates,range(142,155)):
            print(f,round(a,5),round(b,5),bool(caption),flush=True)
            if b<a:
                output[f]=dict(hardware=hardware,captions=caption,previous=a,revised=b)
    (p/'next-assistant-plate.json').write_text(json.dumps(output,indent=2)+'\n')
