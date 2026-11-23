"""Recover closed handset contours and cross-section material from outlined crops."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from casing import closed_casing_distance,closed_casing_coordinates,paint_closed_casing
from render import Film

p=Path(sys.argv[1]); cfg=p/'project/scene.json'
scene=json.loads(cfg.read_text())
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def contour_points(image,q,inside):
    cx,y,w,h,xt,yt,xb,yb=q
    offsets=np.arange(-18,18.25,.38)
    landmarks=[]
    for side in (-1,1):
        for axis,vertical,rx,ry in ((y,-1,xt,yt),(y+h,1,xb,yb)):
            for a in np.linspace(0,np.pi/2,15):
                x0=cx+side*(w/2-rx)
                y0=axis-vertical*ry
                landmarks.append((x0+side*rx*np.cos(a),y0+vertical*ry*np.sin(a),
                                  side*np.cos(a)/rx,vertical*np.sin(a)/ry))
            for t in (.05,.17,.28,.35):
                landmarks.append((cx+side*w*t,axis,0,vertical))
        for yy in np.linspace(y+yt+15,y+h-yb-13,32):
            landmarks.append((cx+side*w/2,yy,side,0))
    observations=[]
    for x,y,nx,ny in landmarks:
        scale=np.hypot(nx,ny)
        u,v=x+nx/scale*offsets,y+ny/scale*offsets
        if (v.min()<1 or v.max()>=998 or u.min()<1 or u.max()>=998):
            continue
        l,r=np.floor(u-.5).astype(int),np.floor(v-.5).astype(int)
        a,b=u-.5-l,v-.5-r
        rgb=image[r,l]*(1-a)*(1-b)+image[r+1,l]*(1-a)*b+image[r,l+1]*a*(1-b)+image[r+1,l+1]*a*b
        grad=(rgb[4:]-rgb[:-4])*.25*(1 if not inside else -1)
        grad*=np.exp(-(offsets[2:-2]/15)**2)
        i=int(np.argmax(grad))+2
        g=grad[i-2]
        if g>5 and abs(offsets[i])<14:
            observations.append((u[i],v[i],min(g,40)))
    return np.asarray(observations)


def fit_shape(image,guess,inside):
    current=np.array(guess)
    for _ in range(2):
        coords=contour_points(image,current,inside)
        if len(coords)<24:break
        xs,ys,strength=coords.T
        def cost(q):
            d=closed_casing_distance(xs,ys,q)
            return np.dot(np.sqrt(d*d+1.45)-np.sqrt(1.45),strength)
        best=cost(current)
        for density in (1,.53,.23,.11):
            for k,step in enumerate((1,1.4,2.8,3.5,3.4,3.1,3.4,3.1)):
                pivot=current.copy()
                for drift in (-2,-1,1,2):
                    v=pivot.copy()
                    v[k]+=drift*step*density
                    result=cost(v)
                    if result<best:
                        current,best=v,result
    return current.round(4).tolist()


def fit(f):
    k=str(f)
    track=scene['threadRegistration']['sofia'][k]
    x,y,scale,header,*_=track['casing']
    width=400*scale
    height=827*scale*track.get('casingAspect',1)
    target=np.asarray(Image.open(ref/f'{f:06d}.png').convert('RGB'),np.int16)
    first=Film(scene).frame(f).convert('RGBA')
    outer=fit_shape(target[:,:,1],(x+width/2,y,width,height,*([66*scale]*4)),False)
    whole=fit_shape(target[:,:,1],(x+width/2,y+15*scale,width-27*scale,height-30*scale,*([52*scale]*4)),True)
    cx,top,w,h,*_=outer
    bounds=[max(0,round(cx-w/2)-32),max(0,round(top)-30),min(1000,round(cx+w/2)+32),min(1000,round(top+h)+33)]
    l,t,r,b=bounds
    rows,cols=np.ogrid[t:b,l:r]
    depth,angle=closed_casing_coordinates(cols+.5,rows+.5,outer,whole)
    region=target[t:b,l:r]
    stops=[-.82,-.58,-.38,-.24,-.17,-.10,-.05,0,.052,.11,.19,.27,.34,.41,.49,.57,.64,
           .72,.78,.85,.91,.97,1.03,1.09,1.16,1.23,1.36,1.52]
    rows_lighting=[]
    for rad in np.linspace(-np.pi,np.pi,16,endpoint=False):
        sep=np.abs((angle-rad+np.pi)%(2*np.pi)-np.pi)
        window=sep<.177
        light=[]
        for stop in stops:
            cluster=window&(np.abs(depth-stop)<.0405)
            if cluster.sum()<5:
                cluster=(sep<.38)&(np.abs(depth-stop)<.099)
            if cluster.sum()<5:
                cluster=np.abs(depth-stop)<.066
            values=region[cluster]
            median=np.median(values,axis=0) if len(values) else [250,250,250]
            light.append(np.rint(median).astype(int).tolist())
        rows_lighting.append(light)
    baseline=float(np.abs(np.asarray(first,np.int16)[:,:,:3]-target).mean())
    best=baseline
    fitted=None
    for limits in ((.77,1.52),(.63,1.45),(.64,1.25),(.88,1.30)):
        test=first.copy()
        params=[outer,whole,stops,rows_lighting,bounds,limits]
        paint_closed_casing(test,params)
        cost=float(np.abs(np.asarray(test,np.int16)[:,:,:3]-target).mean())
        if cost<best:
            fitted,best=params,cost
    print(f,round(baseline,5),round(best,5),outer,whole,flush=True)
    return k,fitted


if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        fits={f:q for f,q in pool.map(fit,range(319,336)) if q}
    scene['sofiaClosedCasing']=fits
    cfg.write_text(json.dumps(scene,indent=2)+'\n')
    (p/'closed-casing-fit.json').write_text(json.dumps(fits,indent=2)+'\n')
