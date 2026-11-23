from pathlib import Path
import csv
import subprocess
import sys

import numpy as np

source, prior, revised, out = map(Path, sys.argv[1:])
x,y,w,h=1700,650,182,390
frames=list(range(646,660))
def decode(video):
    command=['ffmpeg','-nostdin','-v','error','-i',str(video),'-an',
            '-vf',f"select=between(n\\,{frames[0]}\\,{frames[-1]}),format=rgb24,crop={w}:{h}:{x}:{y}",
            '-fps_mode','passthrough','-c:v','rawvideo','-threads:v','1','-f','rawvideo','-']
    data=subprocess.run(command,check=True,capture_output=True).stdout
    return np.frombuffer(data,np.uint8).reshape(len(frames),h,w,3).astype(np.int16)

s,p,c=map(decode,(source,prior,revised))
def measures(image, frame):
    d=(s[frame]-image[frame]).astype(np.float32)
    return float(abs(d).mean()),float((d*d).mean()),int(np.any(d!=0,axis=-1).sum())
with out.open('w',newline='') as handle:
    writer=csv.writer(handle)
    writer.writerow(['frame','pts','x','y','width','height','prior_rgb_mae','prior_rgb_mse','prior_changed_pixels','revised_rgb_mae','revised_rgb_mse','revised_changed_pixels'])
    for index,f in enumerate(frames):
        writer.writerow([f,f*2400,x,y,w,h,*measures(p,index),*measures(c,index)])
print(out)
