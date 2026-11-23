from PIL import Image
from pathlib import Path
import numpy as np
from scipy.ndimage import label,find_objects
p=Path(__file__).parent
a=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=p/'combined-frames'
for f in (607,609,611,613,615,617,619):
 print('FRAME',f)
 for root in (a,b):
  q=np.asarray(Image.open(root/f'{f:06}.png').convert('RGB'),dtype=int)
  xg=range(400,601)
  rs=[]
  for y in range(500,925,5):
   row=q[y,370:630]
   blue=(row[:,0]<175)&(row[:,1]>125)&(row[:,2]>225)&(row[:,2]-row[:,0]>55)
   if blue.sum()>95:
    lo,hi=np.flatnonzero(blue)[[0,-1]]+370
    rs.append((y,lo,hi))
  if len(rs)<4:
   continue
  top,bottom=rs[0][0],rs[-1][0]
  print(root.name,'contour',rs[::5])
  for xp in (414,430,565,580):
   for fpart in (.18,.45,.70,.84):
    y=round(top+fpart*(bottom-top))
    rgb=np.rint(np.median(q[y-3:y+4,xp-5:xp+6,:],axis=(0,1))).astype(int)
    print(tuple(rgb),end=' ')
   print(end='/ ')
  crop=q[top+25:min(1000,bottom-7),423:574]
  lbl,n=label((crop[:,:,0]>209)&(crop[:,:,1]>226)&(crop[:,:,2]>234))
  print('ink',[(423+s[1].start,top+25+s[0].start,423+s[1].stop,top+25+s[0].stop,int((lbl[s]==i).sum()))
        for i,s in enumerate(find_objects(lbl),1) if s[0].stop-s[0].start>40 and s[1].stop-s[1].start>16])
