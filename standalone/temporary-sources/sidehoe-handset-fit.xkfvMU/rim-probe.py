import json
import sys
import numpy as np
from pathlib import Path
from PIL import Image
from render import Film

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
film=Film(scene)
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def smooth_profile(profile):
    padded=np.pad(profile, ((2,2),(0,0)), mode='edge')
    return (padded[:-4]+2*padded[1:-3]+4*padded[2:-2]+2*padded[3:-1]+padded[4:])/10

def outside_edge(profile, start, stop):
    lum=smooth_profile(profile).mean(1)
    candidates=np.flatnonzero((lum[start:stop]<169)&(lum[start+2:stop+2]<132)&
                              (lum[start+4:stop+4]<132))
    if not candidates.size:
        return None
    return int(candidates[0])+start

def analyze(rgb, original, lanes, start, stop, falloff):
    out=[]
    for lane in lanes:
        exp=rgb[:,lane-2:lane+3].mean(1)
        seen=original[:,lane-2:lane+3].mean(1)
        start_edge=outside_edge(exp,start,stop)
        old_edge=outside_edge(seen,start,stop)
        if start_edge is None or old_edge is None:
            continue
        center=start_edge+12
        indices=np.arange(max(0,center-falloff),min(1000,center+falloff+1))
        normal=(indices-center)
        focus=np.clip((falloff-abs(normal))/11,0,1)
        shifts=np.unique(np.r_[np.arange(-16,16.1,.8),old_edge-start_edge,0])
        stretches=np.array([-.24,-.16,-.08,0,.08,.16,.24])
        order=np.vstack((np.repeat(shifts,len(stretches)),np.tile(stretches,len(shifts)))).T
        warp=indices[None,:]+(order[:,0,None]+order[:,1,None]*normal)*focus
        ii=warp.astype(int)
        t=(warp-ii)[...,None]
        estimate=seen[ii]*(1-t)+seen[ii+1]*t
        mismatch=np.abs(estimate-exp[indices]).mean((1,2))
        delta=max(-15,min(15,old_edge-start_edge))
        prior=np.abs(order[:,0]-delta)*.019+np.abs(order[:,1])*.54
        chosen=(mismatch+prior).argmin()
        shift,stretch=order[chosen]
        neutral=np.unique(np.where(np.all(order==0,axis=1))[0])
        if float(mismatch[neutral[0]]-mismatch[chosen])<.075:
            shift=0
            stretch=0
        out.append([lane,center,shift,stretch])
    return out

def warp_lanes(img, knots, falloff):
    k=np.asarray(knots,dtype=np.float32)
    if len(k)<2:
        return img
    left,right=max(0,int(k[0,0])-22),min(1000,int(k[-1,0])+23)
    top,bottom=max(0,int(k[:,1].min())-falloff-1),min(1000,int(k[:,1].max())+falloff+2)
    xs=np.arange(left,right)
    ys=np.arange(top,bottom)[:,None]
    centers,shift,stretch=(np.interp(xs,k[:,0],values) for values in k[:,1:].T)
    normal=ys-centers
    focus=np.clip((falloff-abs(normal))/11,0,1)
    edge=np.clip((xs-left)/22,0,1)*np.clip((right-1-xs)/22,0,1)
    mapped=np.clip(ys+(shift+stretch*normal)*focus*edge,0,999)
    integer=mapped.astype(int)
    t=(mapped-integer)[...,None]
    result=img.copy()
    result[top:bottom,left:right]=np.rint(img[integer,xs]*(1-t)+img[np.minimum(integer+1,999),xs]*t)
    return result

records={}
frames=range(134,162)
for f in frames:
    target,initial=[np.asarray(Image.open(p/f'{f:06}.png').convert('RGB'),dtype=np.float32)
                    for p in (source,root/'baseline')]
    x,y,w=map(round,film.track('assistantMeasuredPosition',f))
    step=7 if f<=137 else 16
    current=initial
    ranges=[
      ('top',target,False,False,range(x+18,x+w-16,step),y-34,y+113,32),
      ('left',target.transpose(1,0,2),True,False,range(y+112,992,22),max(0,x-25),x+65,31),
      ('right',target.transpose(1,0,2)[::-1],True,True,range(y+112,992,22),max(0,1000-x-w-25),1000-x-w+64,31),
    ]
    changed=[]
    for key,comp,transpose,flip,lanes,start,stop,fringe in ranges:
        view=current.transpose(1,0,2) if transpose else current
        if flip:
            view=view[::-1]
        positions=analyze(comp,view,lanes,start,stop,fringe)
        after=warp_lanes(view,positions,fringe)
        old=float(np.abs(view-comp).mean())
        new=float(np.abs(after-comp).mean())
        if new>=old:
            continue
        current=(after[::-1] if flip else after).transpose(1,0,2) if transpose else after
        changed.append([key,fringe,positions])
        print(f,key,round(old,5),round(new,5),len(positions),flush=True)
    if changed:
        records[str(f)]=changed
        (root/'rim-stage').mkdir(exist_ok=True)
        Image.fromarray(current.astype(np.uint8)).save(root/'rim-stage'/f'{f:06}.png')
(root/'rim-fit.json').write_text(json.dumps(records,indent=2)+'\n')
