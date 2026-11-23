from pathlib import Path
from PIL import Image
import numpy as np
import sys
p=Path(sys.argv[1])
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def runs(seq,th,start=0,less=True):
    signs=(seq<th if less else seq>th)
    boxes=[]
    for x in range(len(seq)):
        if signs[x] and (x==0 or not signs[x-1]):
            boxes.append([x+start,x+start])
        if signs[x]:
            boxes[-1][-1]=x+start
    return boxes
for f in (672,675,678,681,686,690,693):
    src=np.array(Image.open(source/f'{f:06}.png').convert('RGB'))[:,:,0]
    raw=np.array(Image.open(p/'prior-probe'/f'{f:06}.png').convert('RGB'))[:,:,0]
    print(f)
    for a in (src,raw):
        print(' outline y',runs(a[600:780,520],229,600),'x',runs(a[682,130:875],221,130))
        print(' plus y',runs(a[610:725,178],219,610))
        print(' key y',runs(a[742:,407],210,742))
        print(' left edge',[(x,runs(a[:470,x],213)) for x in (82,84,86,88,90,92,94,96,98,100,102,104)])
        if f==681:
            for yy in (0,12,20,29,35,42,49,55,60,70,675,680,683,689):
                v=a[yy,396:816]
                print(yy,runs(v,235,396,less=yy>100)[:48])
