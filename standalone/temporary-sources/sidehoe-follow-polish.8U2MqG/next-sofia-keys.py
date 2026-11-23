from pathlib import Path
from PIL import Image
import numpy as np
import json,sys

p=Path(sys.argv[1])
scene=json.loads((p/'sofia-next/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

result={}
for f in range(343,352):
    reg=scene['threadRegistration']['sofia'][str(f)]
    image=np.asarray(Image.open(src/f'{f:06}.png').convert('RGB'))
    data=[]
    for x,y,pitch,w,h,n in reg['keys'][2][:2]:
        if y+h+9>=1000:
            data.append(None)
            continue
        row=[]
        for j in range(n):
            cx=round(x+j*pitch+w/2)
            xx=round(x+j*pitch); yy=round(y)
            left=max(0,xx-7)
            right=round(xx+w)+8
            v=image[yy+12,left:right,0]>238
            a=np.flatnonzero(v)
            if len(a)<30 or a[-1]-a[0]>w+6:
                break
            # The white front face and the darker shadow have independent extents.
            profile=image[yy-6:yy+round(h)+8,cx-4:cx+5,0]
            ys=np.flatnonzero(profile.mean(axis=1)>237)
            near=ys[(ys<22)|(ys>=round(h)-6)]
            if len(near)<3: break
            box=[left+int(a[0]),yy-6+int(near[0]),left+int(a[-1]),yy-6+int(near[-1])]
            if not abs(box[0]-xx)<5 or not abs(box[1]-y)<4 or not abs(box[3]-y-h)<5:
                break
            l,t,r,b=box
            crop=image[t+round(h*.19):b-round(h*.08),l+round(w*.10):r-round(w*.10),0]
            iy,ix=np.where(crop<121)
            if len(ix)<30: break
            ink=[int(l+round(w*.10)+ix.min()),int(t+round(h*.19)+iy.min()),
                 int(ix.max()-ix.min()+1),int(iy.max()-iy.min()+1)]
            row.append([box,ink])
        data.append(row if len(row)==n else None)
    result[str(f)]=data
    print(f,[len(row) if row else None for row in data])
(p/'next-sofia-keys.json').write_text(json.dumps(result,indent=2)+'\n')
