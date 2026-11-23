from concurrent.futures import ProcessPoolExecutor
from copy import copy
from pathlib import Path
from PIL import Image
from render import Film
import json,sys
import numpy as np

p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
bands=((-3,4),(5,5.1),(12,5.2),(21,7.2),(30,6.5),(43,5.7))

def solve(f):
    key=str(f)
    film=Film(s)
    target=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    base=np.asarray(film.frame(f),dtype=np.float32)
    orig=target-base
    x0,y,w=film.track('assistantMeasuredPosition',f)
    start,stop=max(0,round(y)-28),min(999,round(y)+92)
    x_list=list(range(174,831,36))
    knots=[]
    for x in x_list:
        sample=np.median(target[:,x-2:x+3].mean(2),axis=1)
        edge=np.flatnonzero((sample[start:stop]<166)&(sample[start+2:stop+2]<136))
        if edge.size:
            knots.append((x,int(edge[0])+start))
    if len(knots)<7:
        return
    xs,ys=np.asarray(knots).T
    l,r=xs[0],xs[-1]+1
    t,b=max(0,ys.min()-19),min(1000,ys.max()+57)
    row,col=np.mgrid[t:b:2,l:r:2]
    cy=np.interp(col[0],xs,ys)[None,:]
    n=len(xs)
    mask=(row<cy+51)&(row>cy-16)
    island=s['assistantIslandRegistration'].get(key,{}).get('opening')
    if island:
        cx,iy,iw,ih,*_=island
        mask &= (np.abs(col-cx)>iw/2+4)|(row<iy-ih/2-6)
    yx=(row[mask],col[mask])
    normal=(row-cy)[mask]
    entries=[]
    for j in range(n):
        coeff=np.interp(col[0],xs,np.eye(n)[j])
        along=np.broadcast_to(coeff,row.shape)[mask]
        for offset,width in bands:
            entries.append(along*np.exp(-((normal-offset)/width)**2))
    A=np.stack(entries,axis=1)
    left=base[yx]
    right=target[yx]
    X=np.zeros((n*len(bands),3))
    penalty=np.eye(A.shape[1])*1.4
    for i in range(4):
        correction=right-np.clip(left+A@X,0,255)
        weight=(3+np.abs(correction))**-.40
        for c in range(3):
            z=A*weight[:,c,None]
            X[:,c]=np.linalg.solve(A.T@z+penalty,z.T@(right-left)[:,c])
        X=np.clip(X,-96,96)
    parameters=[[int(x),int(y),*np.round(values,4).tolist()]
        for x,y,values in zip(xs,ys,X.reshape(n,-1),strict=True)]
    new=copy(s)
    new['assistantCrownLight']={key:parameters}
    updated=np.asarray(Film(new).frame(f),dtype=np.float32)
    err=np.abs(target-updated)
    initial=np.abs(orig).mean()
    score=err.mean()
    sub_old=np.abs(orig[t:b,l:r]).mean()
    sub_new=err[t:b,l:r].mean()
    print(f,round(float(initial),4),round(float(score),4),round(float(sub_old),4),round(float(sub_new),4),flush=True)
    if score<initial-.008 and sub_new<sub_old:
        return key,parameters

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=3) as pool:
        data=dict(z for z in pool.map(solve,range(134,143)) if z)
    (p/'crown-light-fit.json').write_text(json.dumps(data,indent=2)+'\n')
