from pathlib import Path
from PIL import Image
import numpy as np,sys
p=Path(sys.argv[1]); dirs=(Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),p/'prior-full')
def runs(mask,n=6):
 inds=np.flatnonzero(mask)
 return [(int(g[0]),int(g[-1])) for g in np.split(inds,np.flatnonzero(np.diff(inds)>1)+1) if len(g)>=n]
for f in range(647,661):
 vals=[]
 for root in dirs:
  a=np.asarray(Image.open(root/f'{f:06}.png').convert('RGB'),np.int16)
  patch=a[475:558,292:560]
  R,G,B=patch.transpose(2,0,1)
  gray=(np.maximum.reduce([R,G,B])-np.minimum.reduce([R,G,B])<10)&(R<243)&(R>151)
  hue=(B-R>7)&(B-G>10)&(B>225)&(R>164)&(G>164)
  poses=[]
  for n,m in [('gray',gray),('yes',hue)]:
   v=runs(m[7:60].sum(0)>9)
   result=[]
   for lx,rx in v:
    yy=np.flatnonzero(m[:,lx:rx+1].sum(1)>max(5,(rx-lx)*.45))
    if len(yy): result.append([lx+292,int(yy.min())+475,rx+292,int(yy.max())+475])
   poses.append([n,result])
  vals.append(poses)
 print(f,vals)
