from pathlib import Path
from PIL import Image
import json,sys,numpy as np
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
sc=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
candidate=p/'probe-a'
reference=Path('/tmp/sidehoe-lens.scMdVq/clean-frames')

def bounds(mask,xy,lim=6):
    x0,y0,x1,y1=[int(x) for x in xy]
    x0,y0,x1,y1=max(0,x0),max(0,y0),min(1000,x1),min(1000,y1)
    cuts=mask[y0:y1,x0:x1]
    if not cuts.any():return None
    y,x=np.where(cuts)
    if len(y)<lim:return None
    return [int(x.min()+x0),int(y.min()+y0),int(x.max()+1+x0),int(y.max()+1+y0)]

def fpart(f,base):
    a=np.asarray(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    luma=a.mean(2)
    red,green,blue=np.moveaxis(a,2,0)
    boxes=[(147,190,330,345),(546,188,878,348),(160,294,330,433),(380,294,610,460),(731,285,859,428)]
    acts=[bounds(luma < (197 if f<2 else 169),rect,8) for rect in boxes]
    name_ink=bounds((luma<185)&(red-green<19)&(blue-red<15),(405,397,592,468),12)
    heart=bounds((red-green>45)&(red-blue>31)&(red>157),(545,400,604,451),8)
    dot_mask=(green-red>40)&(blue-red>61)&(green>108)&(red<177)
    unread=[bounds(dot_mask,(182,704+159*i,248,813+159*i),8) for i in (0,1)]
    inks=[]; other=[]
    for i,dot in enumerate(unread):
        line_y=(dot[1]+dot[3])/2 if dot else 755+i*159
        inks.append([bounds(luma<218,(292,line_y-42,467,line_y-16),6),
                     bounds(luma<224,(292,line_y-14,565,line_y+16),6),
                     bounds(luma<231,(645,line_y-44,781,line_y-16),6)])
        other.append(bounds(luma<241,(228,line_y-37,290,line_y+37),12))
    return dict(actors=acts,note=name_ink,heart=heart,dots=unread,inks=inks,avatars=other)
out={}
for f in range(10):
 out[f]=[fpart(f,z) for z in (source,candidate,reference)]
 if f in (0,1,2,4,7,9):
  print(f,*out[f][:2],sep='\n')
(p/'intro-parts.json').write_text(json.dumps(out,indent=2)+'\n')
