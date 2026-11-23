"""Measure the pastel Yes capsule and cursor tip from decoded follow-up frames."""
import argparse
from collections import deque
import csv
import math
from pathlib import Path

import numpy as np
from compare_visual import frames, SIDE, CODED


def components(mask):
    points=set(zip(*np.nonzero(mask)))
    while points:
        origin=points.pop()
        found=[origin]
        backlog=deque([origin])
        while backlog:
            y,x=backlog.popleft()
            for j,k in ((y-1,x),(y+1,x),(y,x-1),(y,x+1),(y-1,x-1),(y+1,x+1),(y-1,x+1),(y+1,x-1)):
                if (j,k) in points:
                    points.remove((j,k))
                    backlog.append((j,k))
                    found.append((j,k))
        yield np.array(found)


def inspect(image):
    scale=CODED/SIDE
    x0,y0,x1,y1=(round(v/scale) for v in (610,920,1230,1350))
    r,g,b=image[y0:y1,x0:x1].astype(np.int16).transpose(2,0,1)
    vivid=(b>211)&(b-r>7)&(b-g>8)&(r>165)&(g>145)
    chroma=[c for c in components(vivid) if len(c)>140]
    chip=max(chroma,key=len)
    rect=(chip[:,1].min()+x0,chip[:,0].min()+y0,chip[:,1].max()+x0,chip[:,0].max()+y0)
    candidates=[]
    for pts in components((r<44)&(g<44)&(b<49)):
        y,x=pts.T
        if np.ptp(y)>=7 and np.ptp(x)>=5 and len(pts)>30 and x.min()+x0>rect[0]+.42*(rect[2]-rect[0]):
            candidates.append(pts)
    if not candidates:
        return rect, None, None
    mark=max(candidates,key=len)
    tip=min(mark,key=lambda q: q[0]+q[1]*.35)
    point=(tip[1]+x0,tip[0]+y0)
    gap=math.hypot(max(rect[0]-point[0],0,point[0]-rect[2]),max(rect[1]-point[1],0,point[1]-rect[3]))
    return tuple(round(z*scale,1) for z in rect),tuple(round(z*scale,1) for z in point),round(gap*scale,1)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("movies",type=Path,nargs="+")
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    with args.out.open("w",newline="") as out:
        w=csv.writer(out)
        w.writerow(["movie","frame","seconds","chip bounds x1 y1 x2 y2","tip x y","gap coded px"])
        for path in args.movies:
            for f,pic in enumerate(frames(path)):
                if 673<=f<=688:
                    w.writerow([str(path),f,f/25,*inspect(pic)])
    print(args.out)


if __name__=="__main__":
    main()
