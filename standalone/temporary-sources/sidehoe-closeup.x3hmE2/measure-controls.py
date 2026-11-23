from pathlib import Path
from PIL import Image
import numpy as np
import json,sys

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def group(ys,min_span):
    return [s for s in np.split(ys,np.flatnonzero(np.diff(ys)>1)+1) if len(s)>=min_span]
out={}
for f in range(673,693):
    reg=scene['threadRegistration']['follow'][str(f)]
    src=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'))
    l,r=reg['rails']; top=reg['keys'][0]; z=(r-l)/754
    low,high=top-98,top-7
    outlineY=src[low:high,445:620,0].mean(axis=1)
    ymin=low+outlineY[:43].argmin()
    ymax=low+43+outlineY[43:].argmin()
    if not 62<=ymax-ymin<=78:
        print(f,'composer bad',ymin,ymax,flush=True)
        continue
    cy=(ymin+ymax)/2
    middle=round(cy)
    lx=int(l+115*z)
    rx=int(r-31*z)
    left=lx-8+src[middle,lx-8:lx+9,0].argmin()
    right=rx-8+src[middle,rx-8:rx+9,0].argmin()
    q=src[ymin+10:ymax-10,l+12:l+105,0]
    ys,xs=np.where(q<222)
    center_x=(xs.min()+xs.max())/2+l+12
    center_y=(ys.min()+ys.max())/2+ymin+10
    fillrow=src[round(center_y),l+5:l+110,0]
    fillx=np.flatnonzero((fillrow<243) & (np.abs(np.arange(l+5,l+110)-center_x)<40*z))
    radius=(fillx[-1]-fillx[0]+1)/2
    a,b=left+15,int(left+190*z)
    c,d=int(cy-21*z),int(cy+25*z)
    yy,xx=np.where(src[c:d,a:b,0]<230)
    text=(a+xx.min(),c+yy.min(),xx.max()-xx.min()+1,yy.max()-yy.min()+1)
    a,b=right-round(69*z),right-round(22*z)
    yy,xx=np.where(src[c:d,a:b,0]<229)
    mic_x=(xx.min()+xx.max())/2+a
    mic_h=yy.max()-yy.min()+1
    mic_y=c+yy.min()+mic_h*.40

    rails=[]
    hardware=[]
    for index,(prior_start,prior_end,_) in enumerate(reg['edgeRamps']):
        region=(prior_start-11,prior_end) if index==0 else (prior_start,prior_end+9)
        x0,x1=region
        side=src[:,x0:x1+1,0].astype(float)
        foot=np.median(side[435:625],axis=0)
        near_edge=side[:440,:12] if index==0 else side[:440,-12:]
        substrate=foot[:12] if index==0 else foot[-12:]
        marker=np.max(substrate-near_edge,axis=1)
        runs=group(np.flatnonzero(marker>27),14)
        rail_parts=[]
        for run in runs:
            curve=np.median(side[run[len(run)//3:2*len(run)//3]],axis=0)-foot
            # Fit only the narrow band where the volume and lock keys meet the casing.
            if index==0:
                curve[15:]=0
            else:
                curve[:-14]=0
            if abs(curve).max()<32:
                continue
            rail_parts.append([int(run[0]),int(run[-1]),1.6,
                               [round(x,2) for x in curve]])
        rails.append([x0,x1,[round(x,2) for x in foot]])
        hardware.append(rail_parts)
    out[str(f)]={'composer': {'outline':[left+.3,ymin+.64,right+.10,ymax+.1],
              'plus':[float(center_x),float(center_y),round(radius-.25,3)],
              'microphone':[float(mic_x),round(mic_y,3),round(mic_h/27,3)],
              'text':list(map(float,text))},'edgeRamps':rails,'railHardware':hardware}
    print(f,'composer', out[str(f)]['composer'],'hardware',[[t[:3] for t in parts] for parts in hardware],flush=True)
(root/'controls.json').write_text(json.dumps(out,indent=2)+'\n')
