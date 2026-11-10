"""Exact post-picker and late conversation component bounds, independent UI cameras."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;rows=[]

def components(mask):
    labels,_=ndimage.label(mask);out=[]
    for i,sl in enumerate(ndimage.find_objects(labels),1):
        if sl is None:continue
        yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start;area=int((labels[sl]==i).sum())
        if w>100 and h>20 and area>500:out.append(dict(bbox=[xx.start,yy.start,xx.stop,yy.stop],width=w,height=h,area=area))
    return out
for n in list(range(664,735))+list(range(848,888)):
    a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float);r=dict(frame=n,time=n*1001/30000)
    border=float(np.median(np.r_[a[:,:20].ravel(),a[:,-20:].ravel()]));normalized=a*255/max(1,border) if n<670 else a
    for name,color in [('gray',[236,236,236]),('selected',[228,228,231])]:r[name]=components(np.abs(normalized-color).max(2)<5)
    am=(a[:,:,0]>120)&(a[:,:,0]<210)&(a[:,:,1]-a[:,:,0]>1)&(a[:,:,1]-a[:,:,0]<10)&(a[:,:,2]-a[:,:,0]>7)&(a[:,:,2]-a[:,:,0]<25)
    r['audio']=[c for c in components(am)if c['width']>600 and 1.8<c['width']/c['height']<4]
    rows.append(r)
(p/'measurements-v8/components-v10.json').write_text(json.dumps({'method':'Exact native component geometry, undoing measured scrim only for664–669. Static UI components only; no new production rasters.','measurements':rows},indent=2))
for n in[664,675,687,695,702,709,710,848,853,870,878,887]:print(next(r for r in rows if r['frame']==n))
