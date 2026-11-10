"""Late grid camera from subpixel saturated banana-tile edges; no NCC hold drift."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;rows=[]

def crossing(values, approximate, level):
    choices=[]
    for index in range(max(1,approximate-6),min(len(values),approximate+9)):
        if values[index]>=level and values[index-1]<level:
            fraction=(level-values[index-1])/(values[index]-values[index-1])
            choices.append(index-1+fraction)
    return min(choices,key=lambda value:abs(value-approximate)) if choices else float(approximate)
for n in range(1169,1215):
    a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float);mask=(a[:,:,0]>200)&(a[:,:,1]>215)&(a[:,:,2]<100);mask[350:]=False;mask[:,:350]=False;mask[:,850:]=False;labels,_=ndimage.label(mask);parts=[]
    for i,sl in enumerate(ndimage.find_objects(labels),1):
        if sl is None:continue
        yy,xx=sl
        if xx.stop-xx.start>150 and yy.stop-yy.start>100:parts.append((int((labels[sl]==i).sum()),[xx.start,yy.start,xx.stop,yy.stop]))
    b=max(parts)[1];cy=round((b[1]+b[3])/2);cx=round((b[0]+b[2])/2);line=255-a[cy,:,2];left=crossing(line,b[0],127.5);right=crossing(-line,b[2],-127.5);vertical=255-a[:,cx,2];bottom=crossing(-vertical,b[3],-127.5);rows.append(dict(frame=n,time=n*1001/30000,left=left,right=right,bottom=bottom,width=right-left,bbox=b))
ref=rows[0]
for r in rows:
    scale=r['width']/ref['width'];r.update(scale=scale,x=r['left']-ref['left']*scale,y=r['bottom']-ref['bottom']*scale)
(p/'measurements-v8/grid-held-camera-v10.json').write_text(json.dumps({'method':'Native saturated banana tile left/right and bottom127.5blue-deficit crossings; fractional edge positions fit independent global scale/x/y after entrance. Reference1169. All24heldlogos use complete authentic static sprites.','measurements':rows},indent=2))
for n in[1169,1183,1199,1214]:print(next(r for r in rows if r['frame']==n))
