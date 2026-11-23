from pathlib import Path
import numpy as np,subprocess,sys
base=Path('/Users/darshan/Documents/ChatGPT/imessage-video/sidehoe-skill-trial/motion-review')
args=['ffmpeg','-hide_banner','-v','error','-threads','4','-ss','15.40','-i']
formats=['-vf','scale=64:36:flags=area,format=gray','-frames:v','32','-f','rawvideo','-']
ref='/Users/darshan/Downloads/sidehoe.mp4'
old=str(base/'candidate/sidehoe.mp4')
a,b=[np.frombuffer(subprocess.check_output(args+[x]+formats),dtype=np.uint8).reshape(-1,36,64).astype(float) for x in (ref,old)]
for i in range(389,417):
 j=i-385
 e,r=[np.abs(np.diff(z[j-1:j+1],axis=0)[0]) for z in [a,b]]
 tiles=(e-r).reshape(6,6,8,8).mean((1,3))
 print(i,round(e.mean(),3),round(r.mean(),3),round(np.abs(a[j]-b[j]).mean(),3))
 if 399<=i<=403:
  print(np.round(tiles,1))
