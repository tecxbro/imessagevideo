from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import fit_ink,interpolate,layer,measured_wash
from artwork import font,messages_font

root=Path(sys.argv[1])
s=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
film=s['tracks']
words=[w for line in s['copy']['ending'] for w in line]
ids=('the','most','personal','imessage','assistant','yet')
frame=765
raster=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB'),dtype=np.float64)
paper=np.asarray(measured_wash(tuple(interpolate(film['closingWashFields'],frame))).convert('RGB'),np.float64)

def fit(index):
    word=words[index]
    key=ids[index]
    x,y,w,h,_=interpolate(film[f'closingInk-{key}'],frame)
    left,right=int(x)-6,int(x+w)+8
    top,bottom=int(y)-7,int(y+h)+7
    target=raster[top:bottom,left:right]
    flat=paper[top:bottom,left:right]
    # Keep any trailing neighboring word outside the objective.
    selected=np.ones(target.shape[:2],dtype=bool)
    for ni,nid in enumerate(ids):
        if ni==index or ni//3!=index//3: continue
        nx,ny,nw,nh,_=interpolate(film[f'closingInk-{nid}'],frame)
        low,high=max(0,int(nx-left)-1),int(nx+nw-left)+2
        if high>low:
            selected[:,low:high]=False
    base_weight=515 if index<3 else 690
    orig=np.array([0,0,0,0,base_weight,0],dtype=float)
    def loss(values,family,fractional=True,ink=4):
        dx,dy,dw,dh,weight,blur=map(float,values)
        image=layer(right-left,bottom-top)
        fit_ink(image,word,(x+dx-left,y+dy-top,w+dw,h+dh),round(weight),1,blur,
                family=family,ink=(ink,)*3,fractional=fractional)
        alpha=np.asarray(image.getchannel('A'),dtype=float)/255
        rgb=flat*(1-alpha[:,:,None])+ink*alpha[:,:,None]
        return float(np.abs(rgb[selected]-target[selected]).mean())
    before=loss(orig,font,fractional=False,ink=20)
    options=[]
    for name,family in (('inter',font),('messages',messages_font)):
        v=orig.copy()
        cost=loss(v,family)
        for scale in (1,.55,.25):
            for i,step in enumerate((.75,1.4,1.45,1.5,45,.30)):
                at=v[i]
                for delta in (-2,-1,1,2):
                    q=v.copy()
                    q[i]=at+delta*step*scale
                    if q[5]<0 or q[4]<285 or q[4]>830: continue
                    error=loss(q,family)
                    if error<cost:
                        v,cost=q,error
        options.append((cost,name,v))
    error,name,values=min(options,key=lambda u:u[0])
    print(key,before,error,name,values.round(3).tolist(),flush=True)
    offset=values[:4].round(4).tolist()
    return key,dict(family=name,offset=offset,weight=round(values[4]),blur=round(float(values[5]),4))

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        output=dict(pool.map(fit,range(len(words))))
    (root/'closing-ink-fit.json').write_text(json.dumps(output,indent=2)+'\n')
