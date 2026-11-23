from pathlib import Path
from PIL import Image
import numpy as np
import json,sys

root=Path(sys.argv[1])
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
results={}
for f in range(673,691):
    reg=scene['threadRegistration']['follow'][str(f)]
    src=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB')).astype(int)
    t=reg['no'][1]
    l=reg['no'][0]
    chips=[]
    for active in (False,True):
        center=l+(72 if not active else 244)
        select=(l-14,l+151) if not active else (l+150,l+327)
        x0,x1=select
        body=src[t-9:t+76,x0:x1]
        mask=(body[:,:,0]<244) | (body[:,:,1]<237)
        assert x0<center<x1 and mask.shape[0]==85
        yids=np.flatnonzero(mask[:,center-x0])
        rows=np.flatnonzero(yids<75)
        top=t-9+yids.min()
        bottom=t-9+yids[rows].max()
        # The upper third has the full sidewall and no cursor overlap.
        column=np.flatnonzero(mask[round(top-t+9+(bottom-top)*.28)])
        left,right=x0+column.min(),x0+column.max()
        # Detach the face and editable label from the button fill.
        sx=(right-left)/155
        bx,ex=int(left+14*sx),int(left+(98 if active else 81)*sx)
        y0,y1=int(top+9*sx),int(top+53*sx)
        patch=src[y0:y1,bx:ex]
        ink=(patch.max(axis=-1)<159)
        ys,xs=np.where(ink)
        label=[int(xs.min()+bx),int(ys.min()+y0),int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1)]
        label_color=int(np.percentile(patch[ink,0],12.5))
        ox=int(left+(98 if active else 82)*sx); ex=int(right-10*sx)
        patch=src[y0:y1,ox:ex]
        gold=(patch[:,:,0]>150)&(patch[:,:,0]-patch[:,:,2]>47)&(patch[:,:,1]-patch[:,:,2]>6)
        ys,xs=np.where(gold)
        x,y=xs.min()+ox,ys.min()+y0
        w=xs.max()-xs.min()+1
        h=ys.max()-ys.min()+1 if not active else w
        yrow=round(top+(bottom-top)*.13)
        pigments=[src[yrow: yrow+2, round(left+(right-left)*fraction)-2:round(left+(right-left)*fraction)+3].reshape(-1,3)
                  for fraction in (.18,.50,.82)]
        fill=[np.rint(np.median(region,axis=0)).astype(int).tolist() for region in pigments]
        if active:
            edge0=np.rint(np.array(fill[0])-(np.array(fill[1])-fill[0])*.56).astype(int).clip(0,255)
            edge1=np.rint(np.array(fill[-1])+(np.array(fill[2])-fill[1])*.56).astype(int).clip(0,255)
        else:
            edge0=edge1=np.rint(np.array(fill).mean(axis=0)).astype(int)
        spec={'box':[int(left), int(top), int(right), int(bottom)],
              'gradient':[edge0.tolist(),edge1.tolist()],
              'label':label,'ink':label_color,
              'emoji':[int(x)-1,int(y)-1,int(w)+2,int(h)+2]}
        chips.append(spec)
    results[str(f)]=chips
    print(f,chips)
(root/'chips.json').write_text(json.dumps(results,indent=2)+'\n')
