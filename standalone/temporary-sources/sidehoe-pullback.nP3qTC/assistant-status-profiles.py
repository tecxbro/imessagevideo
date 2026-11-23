from pathlib import Path
from PIL import Image
import numpy as np
import json,sys

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
scene=json.loads((root/'project/scene.json').read_text())
track=scene['tracks']['assistantMeasuredPosition']
read=json.loads((root/'assistant-landmarks.json').read_text())
roots=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),root/'final-frames']

def dark_bounds(im,bounds,tol,n=2):
    x,y,r,b=map(round,bounds)
    z=im[y:b,x:r]
    active=(z[:,:,0]<tol)&(z[:,:,1]<tol)&(z[:,:,2]<tol)
    yy=np.flatnonzero(active.sum(axis=1)>=n)
    xx=np.flatnonzero(active.sum(axis=0)>=n)
    if not yy.size or not xx.size:
        return None
    return [x+int(xx.min()),y+int(yy.min()),x+int(xx.max())+1,y+int(yy.max())+1]

out={}
for f in range(134,161):
    coord=read[str(f)]
    rows={}
    for i,folder in enumerate(roots):
        a=np.array(Image.open(folder/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
        l,t,w=interpolate(track,f)
        if coord[i]['island']:
            ix,iy,ir,ib=coord[i]['island']
            center=(iy+ib)/2
        else:
            center=t+103
        knobs={}
        for name,right_left in {'time':(145,242),'cellular':(643,717),
                                'wifi':(717,772),'battery':(774,851)}.items():
            bound=dark_bounds(a,(right_left[0],center-25,right_left[1],center+26),150)
            knobs[name]=bound
        rail=np.median(a[round(t-38):round(t+34),437:557],axis=(1,2))
        target=rail<185
        yy=np.flatnonzero(target)
        if yy.size:
            knobs['bevel_top']=[int(yy[0])+round(t-38),int(yy[-1])+round(t-38)]
        rows['source' if i==0 else 'candidate']=knobs
    out[f]=rows
    if f in (134,136,139,141,145,150,155):
        print(f,rows)
(root/'assistant-status-profiles.json').write_text(json.dumps(out,indent=2)+'\n')
