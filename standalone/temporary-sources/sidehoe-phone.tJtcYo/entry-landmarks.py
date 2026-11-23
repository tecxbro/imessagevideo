from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-portraits.if793d/full-frames')
def spans(binary):
    ix=np.flatnonzero(binary)
    return [(int(r[0]),int(r[-1]+1)) for r in np.split(ix,np.flatnonzero(np.diff(ix)>1)+1) if r.size]
def landmarks(im):
    g=im.mean(2)
    dark=(g[435:470,220:780]<100).mean(axis=0)>.6
    rails=[(220+l,220+r) for l,r in spans(dark)]
    inside=im[:,320:690]
    delta=(inside.max(2)-inside.min(2))
    a,b,c=np.moveaxis(inside,2,0)
    pale=np.mean((a<243)&(a>115)&(b-a>10)&(c-a>14),axis=1)
    bubble=np.var(g[:,365:650],axis=1)
    keys=[]
    qq=(((g>248)&(np.ptp(im,axis=2)<6))[575:990,310:700])
    labs,n=label(qq)
    for yy,xx in find_objects(labs):
        h=yy.stop-yy.start; wid=xx.stop-xx.start
        if 12<h<80 and 15<wid<180 and 200<h*wid<9000:
            keys.append((575+yy.start,575+yy.stop,310+xx.start,310+xx.stop))
    middle=np.median(g[:,440:560],axis=1)
    return rails,spans(pale>.25)[:12],[tuple((j[0],j[1])) for j in keys if j[2]>440 and j[3]<560],spans((middle<56))[-4:]
for f in range(649,660):
    print(f)
    for d in (src,prior):
        im=np.array(Image.open(d/f'{f:06}.png').convert('RGB'),dtype=np.int16)
        print(landmarks(im))
