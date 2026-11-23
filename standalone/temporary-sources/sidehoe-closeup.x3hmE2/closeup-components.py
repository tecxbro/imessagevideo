from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def bounds(arr,rect,channel,threshold,invert=False):
    l,t,r,b=map(int,rect)
    arr=arr[t:b,l:r,channel]
    y,x=np.where(arr>threshold if invert else arr<threshold)
    return [int(x.min()+l),int(y.min()+t),int(x.max()+l+1),int(y.max()+t+1)] if len(x) else None
for f in (670,673,675,678,681,684,687,690,693):
    fr=s['threadRegistration']['follow'][str(f)]
    src=np.array(Image.open(source/f'{f:06}.png').convert('RGB'))
    raw=np.array(Image.open(p/'prior-probe'/f'{f:06}.png').convert('RGB'))
    regions={}
    x0,y0,x1,y1=fr['blue']
    for j,ry in enumerate([y0+(.20+.37*i)*(y1-y0) for i in range(2)]):
        if ry+21>10:
            region=(x0+19,max(0,ry-3),x1-17,min(y1-9,max(1,ry+32)))
            regions[f'blue{j}']=[bounds(a,region,0,243,True) for a in (src,raw)]
    for j,(x,y,w,h) in enumerate(fr['items'][1][1]):
        region=(x-6,y-5,x+w+9,y+h+5)
        regions[f'in{j}']=[bounds(a,region,0,140) for a in (src,raw)]
    l,r=fr['rails']
    t=fr['keys'][0]
    for name,region,channel,threshold in [
        ('negative',(l+6,t-90,l+99,t-10),0,226),
        ('text',(l+119,t-84,l+295,t-14),0,219),
        ('left',(l-50,0,l-32,450),0,188),
        ('right',(r+31,65,r+48,410),0,188)]:
        if region[0]<region[2]:
            regions[name]=[bounds(a,region,channel,threshold) for a in (src,raw)]
    print(f,json.dumps(regions),flush=True)
