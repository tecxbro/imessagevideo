from PIL import Image
import numpy as np, json, sys

mine=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
src=np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)

def inkbox(arr, reg, mode):
    x0,y0,x1,y1=reg
    sub=arr[y0:y1,x0:x1]
    if mode=='white': m=np.all(sub>240,axis=2)
    elif mode=='blue': m=(sub[:,:,2]>200)&(sub[:,:,0]<120)
    else: m=np.all(sub<150,axis=2)
    ys,xs=np.where(m)
    if not len(ys): return None
    return (x0+int(xs.min()), y0+int(ys.min()), x0+int(xs.max()+1), y0+int(ys.max()+1))

for name, reg, mode in [
  ('sam',(430,60,530,105),'dark'),
  ('chevron',(30,50,65,90),'blue'),
  ('text-out',(590,185,860,235),'white'),
  ('text-in1',(70,275,360,325),'dark'),
  ('doors-text',(70,365,330,410),'dark'),
]:
    s=inkbox(src,reg,mode); m=inkbox(mine,reg,mode)
    print(name,'src',s,'mine',m, 'shift', None if (s is None or m is None) else (m[0]-s[0],m[1]-s[1]))
