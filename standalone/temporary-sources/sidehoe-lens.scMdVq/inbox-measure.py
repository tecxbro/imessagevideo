from pathlib import Path
from PIL import Image
import numpy as np,sys,json
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-light.sqaBVz/final-frames')

def region(shape, mask, quorum=1, p=(0,100)):
    l,t,r,b=(int(round(c)) for c in shape)
    l,t,r,b=max(0,l),max(0,t),min(1000,r),min(1000,b)
    if l>=r or t>=b:return None
    view=mask[t:b,l:r]
    on=view.sum(1)>=quorum
    y,x=np.where(view&on[:,None])
    if len(y)<6:return None
    a,d=p
    return [round(float(np.percentile(x,a))+l,2),round(float(np.percentile(y,a))+t,2),
            round(float(np.percentile(x,d))+l+1,2), round(float(np.percentile(y,d))+t+1,2)]

def frame_pos(f,base):
    im=np.asarray(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    red,green,blue=np.moveaxis(im,2,0)
    luma=im.mean(2)
    rows_y,rows_z=interpolate(scene['tracks']['inboxIdentifiedRowPose'],f)
    c_y,c_s=interpolate(scene['tracks']['inboxChromePose'],f)
    x0=500-410*c_s
    col=lambda x:x0+x*c_s
    row=lambda y:c_y+y*c_s
    reading={}
    dark=(luma<140)
    reading['clock']=region((col(76),row(179)-14,col(192),row(251)+10),dark,3)
    reading['headline']=region((col(312),row(281)-12,col(517),row(369)+8),dark,6)
    reading['status']=region((col(552),row(180)-20,col(752),row(260)+8),dark,5)
    caption_mask=(luma<133)
    reading['labels']=[region((col(x-79),row(565)-9,col(x+73),row(613)+10),caption_mask,4) for x in (170,410,647)]
    pin_signals=((red-blue>38)&(green-blue>16)&(red>92)&(red<228),
                 (red<192)&(blue<213)&(green>=75)&(green<169),
                 (blue-red>64)&(blue>154)&(green>77)&(green<197))
    p=[]
    for x,mask in zip((169,411,651),pin_signals,strict=True):
        q=region((col(x-98),row(378)-13,col(x+98),row(558)+11),mask,8,(.1,99.9))
        p.append(q)
    reading['pins']=p
    dots=(red<123)&(green-red>48)&(blue-red>65)&(blue>171)&(green>98)
    rows=[]
    for j in range(9):
        y=rows_y+(752+171*j)*rows_z
        dot=region((500+(135-500)*rows_z,y-63,500+(196-500)*rows_z,y+63),dots,1,(0,100))
        if dot:
            m=(dot[1]+dot[3])*.5
            name=region((239,m-49,519,m-17),dark,3)
            quote=region((239,m-10,577,m+20),(luma<175),3)
            clock=region((640,m-50,810,m-16),(luma<195),3)
            rows.append([j,dot,name,quote,clock])
    reading['rows']=rows
    return reading
data={}
for f in range(39,102):
 pair=[frame_pos(f,d) for d in (source,old)]
 data[str(f)]=pair
 if f in (42,43,45,47,48,50,52,54,57,59,61,63):
    print(f)
    for r in pair:
        print(r)
(root/'inbox-measure.json').write_text(json.dumps(data,indent=2)+'\n')
