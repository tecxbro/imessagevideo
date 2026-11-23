from pathlib import Path
from PIL import Image
import numpy as np, subprocess
from scipy.optimize import minimize
from scipy.ndimage import map_coordinates
d=Path('/Users/darshan/.codex/attachments/3f90843a-693a-4d44-85bf-3e6826a82d73')
clips=['/Users/darshan/Downloads/sidehoe.mp4','sidehoe-skill-trial/finish/sidehoe.mp4']
for i,lo,hi in [(1,701,710),(2,185,197)]:
 img=np.asarray(Image.open(d/f'image-{i}.png').convert('RGB'),dtype=np.float32)
 per=[]
 for side,clip in enumerate(clips):
  if i==1:
   x0=7+859*side; y0=15
   bounds=(300+859*side,309,570+859*side,577)
  else:
   x0=-3+859*side; y0=-12
   bounds=(142+859*side,345,720+859*side,520)
  decoder=['ffmpeg','-nostdin','-v','error','-i',clip,'-an','-vf',
           f'select=between(n\\,{lo}\\,{hi}),scale=540:540:flags=area,format=rgb24',
           '-fps_mode','passthrough','-f','rawvideo','-']
  v=np.frombuffer(subprocess.check_output(decoder),np.uint8).reshape(-1,540,540,3).astype(np.float32)
  x1,y1,x2,y2=bounds
  yy,xx=np.mgrid[y1:y2:3,x1:x2:3]
  ref=img[yy,xx,:]
  def cost(a,w):
   dx,dy,g=w
   X=(xx-x0+dx)*540/859*(1+g)
   Y=(yy-y0+dy)*540/859*(1+g)
   look=np.stack([map_coordinates(a[:,:,c],(Y,X),order=1,mode='nearest') for c in range(3)],axis=2)
   return float(np.abs(ref-look).mean())
  k=[]
  for frame in v:
   q=minimize(lambda w:cost(frame,w),[0,0,0],method='Powell',
              bounds=[(-6,6),(-13,13),(-.014,.014)])
   k.append(q.fun)
  per.append(np.array(k))
  print(i,side,[(lo+int(k2),round(k[k2],2)) for k2 in np.argsort(k)[:4]])
 comb=sum(per)
 print('joint',i,[(lo+int(k),round(float(comb[k]),2)) for k in np.argsort(comb)[:5]])
