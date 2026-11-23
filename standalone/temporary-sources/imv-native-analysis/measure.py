from PIL import Image
import numpy as np, subprocess, pathlib
film='05-linq'
source=f'projects/{film}-complete-v1/imessage-recreations/references/{film}/source.mp4'
a,b=1080,1140
raw=subprocess.check_output(['ffmpeg','-v','error','-i',source,'-vf',f'select=between(n\\,{a}\\,{b})','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
frames=np.frombuffer(raw,np.uint8).reshape(-1,720,960,3)
for frame,im in enumerate(frames,a):
  cut=im[355:590].astype(float)
  paper=np.median(cut[:,130:175,:],axis=(0,1))
  diff=np.mean(np.abs(cut-paper),axis=2)
  interior=np.mean(diff>17,axis=0)>.24
  edges=np.flatnonzero(interior[1:]!=interior[:-1])+1
  if frame==a or frame<=1125 or frame%5==0:
   print(frame,edges.tolist(),np.round(np.mean(np.abs(im[:291].astype(float)-frames[1090-a,:291]),axis=(0,1)),3))
