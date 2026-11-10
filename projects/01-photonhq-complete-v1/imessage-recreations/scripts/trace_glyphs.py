"""Trace an isolated graphic alpha mask into editable native SVG outlines.
Input must be a bounded graphic element, not a complete video frame.
"""
import numpy as np
TABLE={1:[(0,3)],2:[(1,0)],3:[(1,3)],4:[(2,1)],6:[(2,0)],7:[(2,3)],8:[(3,2)],9:[(0,2)],11:[(1,2)],12:[(3,1)],13:[(0,1)],14:[(3,0)]}
def trace_alpha(alpha,x0=0,y0=0,threshold=.5):
 ar=np.pad(alpha,1);tl,tr,br,bl=ar[:-1,:-1],ar[:-1,1:],ar[1:,1:],ar[1:,:-1];cases=(tl>=threshold).astype(np.uint8)+2*(tr>=threshold)+4*(br>=threshold)+8*(bl>=threshold);ys,xs=np.where((cases>0)&(cases<15));links={};points={}
 for y,x in zip(ys,xs):
  vals=[ar[y,x],ar[y,x+1],ar[y+1,x+1],ar[y+1,x]];case=int(cases[y,x]);pairs=TABLE.get(case)
  if case==5:pairs=[(0,1),(2,3)] if sum(vals)/4>=threshold else [(0,3),(2,1)]
  if case==10:pairs=[(1,2),(3,0)] if sum(vals)/4>=threshold else [(1,0),(3,2)]
  def edge(e):
   if e==0:key=('h',int(y),int(x));a,b=vals[0],vals[1];px,py=x,y;dx,dy=1,0
   elif e==1:key=('v',int(y),int(x+1));a,b=vals[1],vals[2];px,py=x+1,y;dx,dy=0,1
   elif e==2:key=('h',int(y+1),int(x));a,b=vals[3],vals[2];px,py=x,y+1;dx,dy=1,0
   else:key=('v',int(y),int(x));a,b=vals[0],vals[3];px,py=x,y;dx,dy=0,1
   f=(threshold-a)/(b-a) if b!=a else .5;points[key]=(float(x0-.5+px+dx*f),float(y0-.5+py+dy*f));return key
  for e0,e1 in pairs:
   k0,k1=edge(e0),edge(e1)
   if k0 in links and links[k0]!=k1:raise ValueError('Ambiguous directed contour')
   links[k0]=k1
 loops=[]
 while links:
  start=next(iter(links));cur=start;poly=[]
  for _ in range(len(links)+1):
   poly.append(points[cur]);cur=links.pop(cur)
   if cur==start:break
  else:raise ValueError('Open contour')
  clean=[]
  for i,p in enumerate(poly):
   ax,ay=poly[i-1];bx,by=p;cx,cy=poly[(i+1)%len(poly)];cross=(bx-ax)*(cy-by)-(by-ay)*(cx-bx)
   if abs(cross)>.0002:clean.append(p)
  if len(clean)>=3:loops.append(clean)
 def fmt(v):return f'{v:.3f}'.rstrip('0').rstrip('.')
 path=' '.join('M'+fmt(poly[0][0])+' '+fmt(poly[0][1])+' '+' '.join('L'+fmt(x)+' '+fmt(y) for x,y in poly[1:])+' Z' for poly in loops)
 return path,dict(contours=len(loops),vertices=sum(map(len,loops)))
