from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import Film

p=Path(sys.argv[1]); d=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
scene=json.loads((p/'project/scene.json').read_text()); film=Film(scene)

def one_box(a,start,top,w,h):
    x,y=round(start),round(top)
    l=max(12,x-4);r=min(389,x+round(w)+6)
    mid=round(x+w/2)
    xx=np.flatnonzero(a[round(y+h*.18),l:r,0]>238)
    if len(xx)<max(11,w*.60) or xx[-1]-xx[0]>w+5:
        return None
    profile=a[max(0,y-5):min(827,y+round(h)+7),mid-3:mid+4,0].mean(1)
    yy=np.flatnonzero(profile>237)
    if len(yy)<7 or yy[-1]-yy[0]>h+6:
        return None
    l1,t1,r1,b1=int(l+xx[0]),int(y-5+yy[0]),int(l+xx[-1]),int(y-5+yy[-1])
    if abs(t1-y)>4 or abs(b1-y-h)>5 or b1-t1<30 or r1-l1<20:
        return None
    x0,x1=l1+round(w*.10),r1-round(w*.10)
    y0,y1=t1+round(h*.16),b1-round(h*.08)
    yy,xx=np.where(a[y0:y1,x0:x1,0]<152)
    if len(yy)<10 or yy.max()-yy.min()+1<h*.26:
        return None
    box=[float(l1-.12),float(t1+.25),float(r1+.1),float(b1+.16)]
    ink=[int(x0+xx.min()),int(y0+yy.min()),int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)]
    return [box,ink]

all_data={}
for f in range(634,660):
    k=str(f); record=scene['followSettledRegistration'][k]
    x,y,s=film.track('followMeasuredCamera',f)
    asp=1
    if 'camera' in record: x,y,s,asp=record['camera']
    src=Image.open(d/f'{f:06}.png').convert('RGB')
    im=np.asarray(src.transform((400,827),Image.Transform.AFFINE,(s,0,x,0,s*asp,y),Image.Resampling.BICUBIC))
    floor,rows,*_=record['layout']
    faces=[]
    for (x0,top,pitch,w,h),count in zip(rows,(10,9,7),strict=True):
        faces.append([one_box(im,x0+j*pitch,top,w,h) for j in range(count)])
    palette=np.asarray(im[round(floor)+1:round(rows[0][1])-2,156:239,:])
    if palette.size==0:
        palette=im[round(rows[0][1])+14:round(rows[0][1])+39,48:51]
    pixels=palette.reshape(-1,3)
    frame=pixels[(pixels[:,0]>198)&(pixels[:,0]<236)]
    if len(frame)<10:
        tray=[215,216,220]
    else:
        tray=np.rint(np.median(frame,axis=0)).astype(int).tolist()
    count=sum(p is not None for row in faces for p in row)
    if count>=10:
        all_data[k]={'rows':faces,'tray':tray}
    print(f,count,tray)
(p/'settled-key-fit.json').write_text(json.dumps(all_data,indent=2)+'\n')
