from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from casing import casing_coordinates, paint_exit_casing, shoulder_distance
from render import Film

work=Path(sys.argv[1])
s=json.loads((work/'base/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def contours(image, initial, inside):
    """Locate local normal transitions at independently sampled shoulder angles."""
    cx,top,width,rx,ry=initial
    trend=1 if inside else -1
    offsets=np.arange(-24,25,.5)
    observations=[]
    for sign in (-1,1):
        angles=np.linspace(0,np.pi/2,19)
        x0=cx+sign*(width/2-rx)
        y0=top+ry
        curves=[(x0+sign*rx*np.cos(angle),y0-ry*np.sin(angle),
                 sign*np.cos(angle)/rx,-np.sin(angle)/ry) for angle in angles]
        curves += [(cx+sign*width/2,top+ry+n,sign,0) for n in (14,29,46,61)]
        curves += [(cx+sign*d,top,0,-1) for d in (0,52,110,170,231)]
        for x,y,nx,ny in curves:
            scale=np.hypot(nx,ny)
            ux,uy=x+offsets*nx/scale,y+offsets*ny/scale
            u=np.floor(ux-.5).astype(int)
            v=np.floor(uy-.5).astype(int)
            h,k=ux-.5-u,uy-.5-v
            samples=(image[v,u]*(1-h)*(1-k)+image[v+1,u]*k*(1-h)
                    +image[v,u+1]*h*(1-k)+image[v+1,u+1]*h*k)
            # Moving outward, the glass darkens and the outside paper lightens.
            response=-trend*(samples[4:]-samples[:-4])/2
            response*=np.exp(-(offsets[2:-2]/27)**2)
            j=int(np.argmax(response))
            if response[j]>4 and abs(offsets[j+2])<21:
                observations.append([ux[j+2],uy[j+2],min(30,response[j])])
    return np.array(observations)


def fit_outline(image, guess, inside):
    params=np.array(guess)
    for _ in range(2):
        xy=contours(image,params,inside)
        x,y,w=xy.T
        def cost(candidate):
            d=shoulder_distance(x,y,candidate)
            return np.dot(np.sqrt(d*d+2)-np.sqrt(2),w)
        best=cost(params)
        for precision in (1,.50,.23,.1):
            for k,step in enumerate((1,1.5,3,6,6)):
                old=params.copy()
                for n in (-2,-1,1,2):
                    test=old.copy()
                    test[k]+=n*step*precision
                    score=cost(test)
                    if score<best:
                        params,best=test,score
    return params.round(4).tolist()


def fit(frame):
    film=Film(s)
    x,y,w=film.track('assistantMeasuredPosition',frame)
    im=Image.open(reference/f'{frame:06}.png').convert('RGB')
    target=np.asarray(im,dtype=float)
    old=Image.open(work/'baseline-probe'/f'{frame:06}.png').convert('RGBA')
    left,top,width=x,round(y)-2,w
    outer=fit_outline(target[:,:,1],(left+width/2,top,width,150,150),False)
    inner=fit_outline(target[:,:,1],(left+width/2,top+36,width-68,115,115),True)
    start=max(0,round(min(outer[1],top))-30)
    solid=min(970,round(y)+200)
    end=min(1000,solid+62)
    rows,columns=np.ogrid[start:end,:1000]
    depth,along=casing_coordinates(columns+.5,rows+.5,outer,inner)
    colors=target[start:end]
    # Sparse material samples across the rim and along the width of the handset.
    light=[-1,-.92,-.77,-.50,-.12,.28,.60,.80,.94,1]
    stops=[-.9,-.56,-.34,-.23,-.14,-.08,-.03,.02,.08,.14,.21,.28,.36,
           .44,.52,.60,.68,.75,.82,.89,.95,1,1.04,1.10,1.17,1.26,1.42,1.76]
    layers=[]
    for station in light:
        region=np.abs(np.clip(along,-1,1)-station)
        width=.09 if abs(station)>.73 else .16
        station_keep=region<width
        if abs(station)>.98:
            station_keep = station_keep & (rows>y+130)
        elif abs(station)>.80:
            station_keep = station_keep & (rows<y+153)
        track=[]
        for q in stops:
            search=station_keep & (np.abs(depth-q)<.037)
            if search.sum()<4:
                search=station_keep & (np.abs(depth-q)<.14)
            if search.sum()<4:
                track.append([253,253,253])
                continue
            track.append(np.median(colors[search],axis=0).round(1).tolist())
        layers.append(track)
    settings=[outer,inner,stops,light,layers,[start,solid,end]]
    revised=old.copy()
    paint_exit_casing(revised,settings)
    target=target.astype(np.int16)
    previous,updated=[np.abs(np.asarray(a.convert('RGB'),np.int16)-target) for a in (old,revised)]
    rowscores=[float(e.mean()) for e in (previous,updated)]
    print(frame, [round(z,3) for z in rowscores],outer,inner,flush=True)
    if updated.mean()<previous.mean():
        if frame==160:
            box=(32,start,975,end)
            board=Image.new('RGB',(943,3*(end-start)))
            for i,img in enumerate((im,old,revised)):
                board.paste(img.crop(box),(0,(end-start)*i))
            board.save(work/'exit-fit-160.jpg',quality=94)
        return str(frame),settings,rowscores
    return str(frame),None,rowscores


if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=5) as pool:
        result=list(pool.map(fit,range(153,162)))
    (work/'exit-fit.json').write_text(json.dumps({f:s for f,s,m in result if s},indent=2)+'\n')
    (work/'exit-stat.json').write_text(json.dumps({f:m for f,s,m in result},indent=2)+'\n')
