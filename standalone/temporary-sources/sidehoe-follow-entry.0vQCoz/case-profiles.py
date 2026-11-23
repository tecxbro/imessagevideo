from measure import *
import re
roots=[SRC,PRE,ROOT/'probe']
def spans(q, rect, level):
    x,y,roi=crop(q,rect)
    yy,xx=np.where(roi.max(2)<level)
    return ((x+xx.min(),y+yy.min(),x+xx.max()+1,y+yy.max()+1) if xx.size else None)
for f in (636,649,655,657,658,659):
    print(f,camera(f))
    for root in roots:
        q=np.array(Image.open(root/f'{f:06d}.png').convert('RGB'))
        x,y,s,aspect,ky=camera(f)
        s_y=s*aspect
        print(root.name,
              'top',spans(q,(420,y-16,581,y+16),104),
              'floor',spans(q,(419,y+811*s_y,581,y+845*s_y),104),
              'curve',spans(q,(x-18,max(0,y),x+85*s,y+89*s_y),98),
              'left',spans(q,(x-16,y+225*s_y,x+40*s,y+264*s_y),96),
              'right',spans(q,(x+365*s,y+225*s_y,x+414*s,y+264*s_y),96))
