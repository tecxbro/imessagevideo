"""Measure the publicly published emblem against the independently authored film."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,math,sys
import numpy as np
from PIL import Image
from render import Film

w=Path(sys.argv[1])
scene=json.loads((w/'clean/scene.json').read_text())
site=Image.open(w/'sidehoe-site-icon.png').convert('RGBA')
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def trial(frame):
    k=str(frame)
    full=Film(scene)
    cx,cy,width,height=full.track('closingBadgeShape',frame)[:4]
    bounds=tuple(map(round,(cx-width*.37,cy-height*.35,cx+width*.37,cy+height*.38)))
    l,t,r,b=bounds
    ref=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB').crop(bounds),np.int16)
    current=full.frame(frame).crop(bounds)
    base={**scene,'closingBadgeArtwork':{k:[[1200,0,1,1]]*4}}
    matte=Film(base).frame(frame).crop(bounds).convert('RGBA')
    matte_data=np.asarray(matte,dtype=float)[:,:,:3]
    brightness=(ref[:,:,0]>111)&(ref[:,:,0]>ref[:,:,1]+6)
    yy,xx=np.where(brightness)
    original=float(np.abs(np.asarray(current,np.int16)-ref).mean())
    g=[l+(xx.min()+xx.max())/2,t+(yy.min()+yy.max())/2,xx.max()-xx.min()+1,yy.max()-yy.min()+1,.65,0.]
    cols,rows=np.meshgrid(np.linspace(-1,1,matte.width),np.linspace(-1,1,matte.height))
    gradient=np.stack((np.ones(cols.shape),cols,rows,cols*cols,rows*rows,cols*rows),axis=-1)
    def fit(sample,fit_color):
        x,y,dw,dh,theta,shear=sample
        theta=math.radians(theta)
        uu,vv=math.cos(theta),math.sin(theta)
        sx,sy=site.width/dw,site.height/dh
        u,v=uu*sx,(vv+shear)*sx
        p,q=-vv*sy,uu*sy
        transform=(u,v,site.width*.5+u*(l-x)+v*(t-y),
                   p,q,site.height*.5+p*(l-x)+q*(t-y))
        art=site.transform(matte.size,Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC)
        rgba=np.asarray(art,dtype=float)
        rgb,alpha=rgba[:,:,:3],rgba[:,:,3:]/255
        coeff=None
        if fit_color:
            inner=(alpha[:,:,0]>.96)&brightness
            A=gradient[inner]
            coeff=np.linalg.solve(A.T@A+np.diag([i*12 for i in (1,2,2,3,3,3)]),
                                  A.T@(ref-rgb)[inner])
            rgb=np.clip(rgb+gradient@coeff,0,255)
        mix=np.uint8(np.clip(np.rint(matte_data*(1-alpha)+rgb*alpha),0,255))
        return float(np.abs(mix.astype(np.int16)-ref).mean()),mix,coeff
    best,image,coeff=fit(g,True)
    for precision in (1,.51,.25,.13):
        for j,step in enumerate((.8,.8,1.4,1.4,1.1,.014)):
            first=g.copy()
            for n in (-2,-1,1,2):
                test=first.copy()
                test[j]+=n*step*precision
                proposed,rendered,light=fit(test,True)
                if proposed<best:
                    g,best,image,coeff=test,proposed,rendered,light
    blind,_,_=fit(g,False)
    canvas=Image.new('RGB',(matte.width*3,matte.height))
    for i,pic in enumerate((Image.fromarray(np.uint8(ref)),current,Image.fromarray(image))):
        canvas.paste(pic,(i*matte.width,0))
    canvas.save(w/f'brand-trial-{frame}.png')
    print(frame,'current',round(original,5),'site raw',round(blind,5),'site adjusted',round(best,5),flush=True)
    return str(frame),dict(box=list(bounds),pose=np.asarray(g,dtype=float).round(6).tolist(),
                          colors=coeff.round(5).tolist(),current=original,raw=blind,revised=best)


if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        result=dict(pool.map(trial,(701,706,716,732,755)))
    (w/'brand-icon-fit.json').write_text(json.dumps(result,indent=2)+'\n')
