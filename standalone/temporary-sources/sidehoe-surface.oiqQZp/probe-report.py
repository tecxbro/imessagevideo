from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import label,binary_dilation
p=Path(__file__).parent
s=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
sc=json.loads((p/'project/scene.json').read_text())
keys={r[0]:r[1:] for r in sc['tracks']['followPointerStage']}
def read(fr,folder):
    return np.asarray(Image.open(folder/f'{fr:06}.png').convert('RGB'),dtype=np.int16)
def diff(a,floatabs):
    return np.abs(a-floatabs).mean()
tasks=[('tile',p/'tile-focused',range(599,624),(380,510,621,1000)),
       ('cursor',p/'probes',range(669,697),None),
       ('badge',p/'badge-probe',[*range(699,717),*range(735,739)],(355,355,644,645))]
for name,folder,frames,box in tasks:
 print(name)
 vals=[]
 for f in frames:
    t,x,y=[read(f,d) for d in (s,b,folder)]
    if box:
       i,j,k,l=box
    elif f in keys:
       ax,ay,w,h,*_=keys[f]
       i,j,k,l=map(round,(ax-8,ay-8,ax+w+16,ay+h+9))
    else:
       i,j,k,l=(429,500,650,695)
    if name=='cursor' and f in keys:
       q=t[j:l,i:k]
       lum=q.mean(axis=2)
       ll,n=label((lum<154)&(np.ptp(q,axis=2)<34))
       z=ll[round(ay+h*.44)-j,round(ax+w*.31)-i]
       mask=binary_dilation(ll==z,iterations=3) if z else np.ones(q.shape[:2],dtype=bool)
       crop=lambda a:a[j:l,i:k][mask]
    else:
       crop=lambda a:a[j:l,i:k]
    prev,new=[diff(crop(t),crop(a)) for a in (x,y)]
    vals.append((prev,new))
    print(f,round(prev,4),round(new,4),round(diff(t,x),4),round(diff(t,y),4),'same' if (x==y).all() else '')
 print(name,'average',np.array(vals).mean(axis=0))
