"""Measure the attachment control, input field, placeholder and mic separately."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from render import Film

work=Path(sys.argv[1]); path=work/'project/scene.json'
s=json.loads(path.read_text()); film=Film(s)
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
accepted={}
for frame in range(319,343):
    key=str(frame)
    shot=s['threadRegistration']['sofia'][key]
    l,r=shot['rails']; y=shot['keys'][0]; zoom=(r-l)/376
    original=shot.get('composer')
    target=np.asarray(Image.open(ref/f'{frame:06d}.png').convert('RGB'),np.int16)
    b0=np.asarray(film.frame(frame),np.int16)
    g=target[:,:,1]
    xa,xb=round(l+142*zoom),round(r-105*zoom)
    if xb<=xa+11:
        continue
    lo,hi=max(1,round(y-66*zoom)),min(998,round(y-2*zoom))
    split=round(y-31*zoom)
    xy=g[lo:hi,xa:xb].mean(axis=1)
    if not lo+3<=split<=hi-3:continue
    top=lo+int(xy[:split-lo].argmin())
    bottom=split+int(xy[split-lo:].argmin())
    h=bottom-top
    if not 28*zoom<=h<=48*zoom:
        continue
    cy=(bottom+top)/2
    row=round(cy)
    lx=round(l+60*zoom)
    rx=round(r-14*zoom)
    x0=lx-10+int(g[row,lx-10:lx+11].argmin())
    x1=rx-10+int(g[row,rx-10:rx+11].argmin())
    if x1-x0<(r-l)*.61:
        continue
    a,b=round(l+6*zoom),round(l+49*zoom)
    a=max(0,a)
    attach=g[round(top+h*.14):round(bottom-h*.14),a:b]
    yy,xx=np.where(attach<222)
    if len(xx)<9:continue
    center_x=(xx.min()+xx.max())/2+a
    center_y=(yy.min()+yy.max())/2+round(top+h*.14)
    disks=np.flatnonzero(g[round(center_y),a:b]<243)
    if len(disks)<10:continue
    radius=max(7,(disks[-1]-disks[0]+1)/2)
    il,ir=round(x0+9*zoom),round(x0+119*zoom)
    it,ib=round(cy-h*.29),round(cy+h*.37)
    uy,ux=np.where(g[it:ib,il:ir]<234)
    ml,mr=round(x1-36*zoom),round(x1-10*zoom)
    my,mx=np.where(g[it:ib,ml:mr]<228)
    if min(len(ux),len(mx))<5:continue
    text=[int(il+ux.min()),int(it+uy.min()),int(ux.max()-ux.min()+1),int(uy.max()-uy.min()+1)]
    mic=[float(ml+(mx.max()+mx.min())/2),float(it+my.min()+(my.max()-my.min()+1)*.41),
         round((my.max()-my.min()+1)/27,4)]
    pose=dict(outline=[x0+.3,top+.65,x1,bottom+.13],plus=[center_x,center_y,round(radius-.15,3)],
              microphone=mic,text=text,stroke=round(max(1.2,1.15*zoom),3))
    shot['composer']=pose
    b1=np.asarray(film.frame(frame),np.int16)
    errs=[np.abs(x-target) for x in (b0,b1)]
    old,new=[float(x.mean()) for x in errs]
    band=[float(x[lo:hi,l:r].mean()) for x in errs]
    print(frame,[round(v,4) for v in (old,new,*band)],pose,flush=True)
    if new<old and band[1]<band[0]:
        accepted[key]=pose
    elif original:
        shot['composer']=original
    else:
        shot.pop('composer')
path.write_text(json.dumps(s,indent=2)+'\n')
(work/'sofia-composer-fit.json').write_text(json.dumps(accepted,indent=2)+'\n')
