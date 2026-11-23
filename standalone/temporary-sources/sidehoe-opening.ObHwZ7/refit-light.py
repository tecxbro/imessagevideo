from pathlib import Path
from PIL import Image
from copy import deepcopy
import json,sys
import numpy as np
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import Film
target=p/'project/scene.json'
scene=json.loads(target.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
bands=((-3,4),(5,5.1),(12,5.2),(21,7.2),(30,6.5),(43,5.7))

def model(base,ref,design,start,bound=155):
    raw,answer=np.asarray(base,dtype=float),np.asarray(ref,dtype=float)
    coeff=np.asarray(start,dtype=float)
    D=np.asarray(design,dtype=np.float64)
    result=coeff[:]
    penalty=np.identity(D.shape[-1])*.58
    X=D.reshape(-1,D.shape[-1])
    B=raw.reshape(-1,3)
    Y=answer.reshape(-1,3)
    for i in range(4):
        diff=np.clip(B+X@result,0,255)-Y
        for c in range(3):
            # The measured basis stays smooth between knots. Favor matching the
            # still-visible colors when the source mask clips to paper white.
            weight=(3+abs(diff[:,c]))**-.51
            delta=np.clip(Y[:,c]-B[:,c],-236,236)
            sol=np.linalg.solve(X.T@(X*weight[:,None])+penalty,
                                X.T@(weight*delta)+penalty@coeff[:,c])
            result[:,c]=np.clip(sol,-bound,bound)
    return result

reports={}
for f in (135,136,137):
  clean=deepcopy(scene)
  name=str(f)
  optical=clean['assistantEntranceOptics'][name]
  top_tracks=clean['assistantPrism'].pop(name,None)
  flare_tracks=optical.pop('flare',None)
  ref=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
  base=np.asarray(Film(clean).frame(f),dtype=np.int16)
  before=np.asarray(Film(scene).frame(f),dtype=np.int16)
  if top_tracks:
    old=np.array(top_tracks)
    xs=np.arange(int(old[0,0]),int(old[-1,0])+1,2)
    yrange=np.arange(int(old[:,1].min())-19,int(old[:,1].max())+62)
    basis=[]
    centers=np.interp(xs,old[:,0],old[:,1])
    distances=yrange[:,None]-centers[None,:]
    eye=np.eye(len(old))
    for i in range(len(old)):
      piece=np.interp(xs,old[:,0],eye[i])
      for height,width in bands:
        basis.append(piece[None,:]*np.exp(-((distances-height)/width)**2))
    D=np.stack(basis,axis=2)
    index=np.ix_(yrange,xs)
    early=start=old[:,2:].reshape(-1,3)
    revised=model(base[index],ref[index],D,start)
    clean['assistantPrism'][name]=[[int(x),int(y),*np.round(c,4).tolist()]
                        for (x,y),c in zip(old[:,:2],revised.reshape(-1,18),strict=True)]
  if flare_tracks:
    original=np.asarray(flare_tracks)
    xs=np.r_[np.arange(10,180,2),np.arange(825,1000,2)]
    yrange=np.arange(895,1000)
    X,Y=xs[None,:],yrange[:,None]
    D=np.stack([np.exp(-((X-x-(Y-y)*angle)/w)**2-((Y-y)/h)**2) for x,y,w,h,angle,*_ in original],axis=2)
    index=np.ix_(yrange,xs)
    fitted=model(base[index],ref[index],D,original[:,5:],135)
    optical['flare']=[[*row[:5],*np.round(c,4).tolist()]
                     for row,c in zip(original.tolist(),fitted,strict=True)]
  after=np.asarray(Film(clean).frame(f),dtype=np.int16)
  olddiff,newdiff=[np.abs(t-ref) for t in (before,after)]
  print(f,*(tuple(round(float(u.mean()),4) for u in (d,d[890:,:],d[284:410,230:765])) for d in (olddiff,newdiff)),flush=True)
  if newdiff.mean()<olddiff.mean():
    reports[name]={'top':clean.get('assistantPrism',{}).get(name),'flare':optical.get('flare')}
(p/'light-refit.json').write_text(json.dumps(reports,indent=2)+'\n')
