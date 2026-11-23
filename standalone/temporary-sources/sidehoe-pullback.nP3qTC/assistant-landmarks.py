from pathlib import Path
import sys,json
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
s=json.loads((root/'project/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=root/'final-frames'

def detect(q,box,mask,area,mode='main'):
    x,y,r,b = tuple(round(x) for x in box)
    x,x1,y,y1=max(0,x),min(1000,r),max(0,y),min(1000,b)
    part=q[y:y1,x:x1]
    mark=mask(part)
    cc,n=label(mark)
    out=[]
    selected=[]
    for i,(yy,xx) in enumerate(find_objects(cc),1):
        mass=(cc[yy,xx]==i).sum()
        if mass>=area:
            selected.append([mass,[xx.start+x,yy.start+y,xx.stop+x,yy.stop+y]])
    if mode=='main':
        return max(selected)[1] if selected else None
    return [r for _,r in sorted(selected,key=lambda r:r[1][0])]

def measure(q,f):
    l,t,w=interpolate(s['tracks']['assistantMeasuredPosition'],f)
    sc=w/900
    dark=lambda a:(a.max(2)<117)
    deep=lambda a:(a.max(2)<38)
    neutral=lambda a:(a.max(2)<164)&(np.ptp(a,axis=2)<30)
    blob=lambda a: (a[:,:,0]<188)&(a[:,:,1]-a[:,:,0]>8)&(a[:,:,2]-a[:,:,0]>35)
    beige=lambda a: (a[:,:,0]<243)&(a[:,:,0]>160)&(a[:,:,0]-a[:,:,2]>29)&(a[:,:,0]-a[:,:,1]>10)
    pos=lambda i,j,k,m:(l+i*sc,t+j,l+k*sc,t+m)
    lo=(
        ('island',pos(279,40,633,185),deep,400,'main'),
        ('time',pos(74,71,201,152),neutral,13,'all'),
        ('network',pos(602,65,800,158),neutral,18,'all'),
        ('pin',pos(280,239,615,554),dark,400,'main'),
        ('left_contact',pos(67,260,319,541),beige,450,'main'),
        ('right_contact',pos(567,266,833,542),blob,450,'main'),
        ('heading',pos(316,183,589,261),neutral,20,'all'),
    )
    return {name:detect(q,rect,predicate,area,mode) for name,rect,predicate,area,mode in lo}

measurements={}
for f in range(134,161):
    r=[measure(np.asarray(Image.open(d/f'{f:06d}.png').convert('RGB'),dtype=np.int16),f) for d in (src,old)]
    measurements[f]=r
    if f in (134,136,139,141,145,150,155):
        print(f)
        for key in r[0]:
            print(key,r[0][key],r[1][key])
(root/'assistant-landmarks.json').write_text(json.dumps(measurements,indent=2)+'\n')
