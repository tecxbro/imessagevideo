from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import copy
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'inbox-next/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def collect(f):
    key=str(f)
    frame=scene['inboxHeldRegistration'][key]
    alpha_img=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    old=np.asarray(Film(scene).frame(f),dtype=np.int16)
    gray=np.mean(alpha_img,axis=2)
    x0,top,scale=frame['rows']
    def ink(origin,threshold,default):
        a,b,c,d=origin
        a,b,c,d=max(0,int(a)),max(0,int(b)),min(1000,int(c)),min(1000,int(d))
        if b>=d or a>=c:
            return default
        region=gray[b:d,a:c]
        mask=region<threshold
        count=int(mask.sum())
        if count<3:
            return default
        rows=np.where(mask.sum(1)>0)[0]
        y,x=np.where(mask[rows[0]:rows[-1]+1])
        return [a+int(x.min()),b+int(rows.min()),int(x.max()-x.min()+1),int(rows.max()-rows.min()+1)]
    rows=[]
    for i in range(len(scene['inboxRows'])):
        y=top+scale*(696+171*i)
        if y>994:
            break
        lower=y+133*scale
        a=int(y+27*scale); b=min(1000,int(y+79*scale))
        l=int(x0+51*scale); r=int(x0+111*scale)
        if a>=b:
            break
        patch=alpha_img[a:b,l:r]
        hue=patch[:,:,2]-patch[:,:,0]
        visible=(hue>90)&(patch[:,:,1]-patch[:,:,0]>65)
        vy,vx=np.where(visible)
        dot=[l+int(vx.min()),a+int(vy.min()),int(vx.max()-vx.min()+1),int(vy.max()-vy.min()+1)] if len(vx)>7 else [
                x0+72*scale,y+48*scale,16*scale,16*scale]
        default_name=[x0+191*scale,y+11*scale,125*scale,28*scale]
        default_quote=[x0+191*scale,y+52*scale,173*scale,29*scale]
        default_time=[x0+572*scale,y+14*scale,111*scale,24*scale]
        name=ink([x0+178*scale,y-7,x0+495*scale,y+43*scale],156,default_name)
        quote=ink([x0+176*scale,y+42*scale,x0+544*scale,y+99*scale],226,default_quote)
        time=ink([x0+505*scale,y-8,x0+700*scale,y+44*scale],221,default_time)
        avatar=[x0+140*scale,y+55*scale,69*scale]
        name0=scene['inboxRows'][i][0]
        bg=scene.get('inboxRowColors',{}).get(name0,"")
        rows.append([i,dot,avatar,name,quote,time,min(1000,lower),1,bg])
    project=copy(scene)
    project['inboxHeldRegistration']=copy(scene['inboxHeldRegistration'])
    best=None
    loss=float(np.abs(old-alpha_img).mean())
    for soft in ((.27,.42),(.42,.8),(.65,1.15)):
        entry={**frame,'measuredRows':rows,'measuredRowFocus':list(soft)}
        project['inboxHeldRegistration'][key]=entry
        revised=np.asarray(Film(project).frame(f),dtype=np.int16)
        error=float(np.abs(revised-alpha_img).mean())
        if error<loss:
            best,loss=entry,error
    print(f,round(float(np.abs(old-alpha_img).mean()),4),round(loss,4),flush=True)
    if best:
        return (key,best)

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=dict(r for r in pool.map(collect,range(10,42)) if r)
    (p/'next-inbox-rows.json').write_text(json.dumps(results,indent=2)+'\n')
