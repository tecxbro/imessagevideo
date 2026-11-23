from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from scipy.ndimage import label,find_objects,binary_closing

p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-follow-entry.0vQCoz/final-dual-frames')
s=json.loads((p/'project/scene.json').read_text())
tracks=s['tracks']
out={}
for f in range(700,724):
    if f<tracks['closingBadgeShape'][0][0]:
        continue
    x,y,w,h,k=interpolate(tracks['closingBadgeShape'],f)
    bb=(x-w/2,y-h/2,x+w/2,y+h/2)
    a,b=[np.asarray(Image.open(d/f'{f:06d}.png').convert('RGB').transform((512,512),
                                      Image.Transform.EXTENT,bb,Image.Resampling.BICUBIC),dtype=np.int16) for d in (source,prior)]
    d=np.abs(a-b)
    def bbox(m):
        yy,xx=np.where(m)
        return None if not xx.size else (int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),int(xx.size))
    def zone(m,l,t,r,b):
        q=m[t:b,l:r]
        z=bbox(q)
        return None if z is None else [z[0]+l,z[1]+t,z[2]+l,z[3]+t,z[4]]
    def result(q):
        r,g,b=np.moveaxis(q,2,0)
        gold=(r>95)&(r-g>10)&(g-b>5)
        rose=(r>110)&(r-g>24)&(b-g>13)
        pink=(r>110)&(r-g>45)&(b-g>22)
        shaded=(r>25)&(r<91)&(abs(r-g)<14)&(abs(r-b)<16)
        return [zone(gold,187,106,325,260),zone(gold,66,145,176,230),zone(gold,335,145,440,230),
                zone(pink,185,280,326,435),zone(rose,75,220,174,356),zone(rose,338,220,425,356),
                zone(shaded,222,146,287,198),zone(shaded,230,204,273,232)]
    coords=((252,42),(188,112),(130,122),(70,192),(268,119),(205,138),(300,142),(200,195),
            (200,240),(302,240),(230,277),(252,318),(252,352),(253,390),(253,400),
            (145,184),(144,226),(147,271),(155,299),(365,190),(368,228),(357,271),(359,301))
    samples=[[np.rint(np.median(q[yy-3:yy+4,xx-3:xx+4],axis=(0,1))).astype(int).tolist() for xx,yy in coords] for q in (a,b)]
    if f in (704,706,709,712,720):
        print(f,'error',round(float(d.mean()),3))
        print('src',result(a))
        print('old',result(b))
        if f==706:print(list(zip(coords,*samples)))
    out[f]={'masks':[result(a),result(b)],'samples':samples,'error':float(d.mean())}
(p/'badge-measurements.json').write_text(json.dumps(out,indent=2)+'\n')
