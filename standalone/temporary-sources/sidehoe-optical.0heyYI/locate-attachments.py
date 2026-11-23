from pathlib import Path
from PIL import Image
import numpy as np, subprocess
p=Path('/Users/darshan/.codex/attachments/3f90843a-693a-4d44-85bf-3e6826a82d73')
files=[Path('/Users/darshan/Downloads/sidehoe.mp4'),Path('sidehoe-skill-trial/finish/sidehoe.mp4')]
filters=['scale=136:136:flags=area,format=rgb24']
for id in (1,2):
 img=Image.open(p/f'image-{id}.png').convert('RGB')
 # The pictures are full-width squares with a short vertical crop in the capture.
 boxes=([(7,15,866,866),(866,15,1725,866)] if id==1
        else [(0,0,856,842),(856,0,1715,842)])
 for side,(box,media) in enumerate(zip(boxes,files)):
  b=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(media),'-an','-vf',filters[0],'-f','rawvideo','-'])
  v=np.frombuffer(b,np.uint8).reshape(-1,136,136,3)
  crop=img.crop(box); h=round(crop.height/crop.width*136)
  crop=np.asarray(crop.resize((136,h),Image.Resampling.LANCZOS),dtype=np.int16)
  # Score the screenshot's actual visible half. Subpixel registration is deferred to the nearest native frame.
  loss=np.full(v.shape[0],np.inf)
  for off in range(137-h):
   d=np.abs(v[:,off:off+h].astype(np.int16)-crop).mean((1,2,3))
   loss=np.minimum(loss,d)
  ids=np.argsort(loss)[:8]
  print('screenshot',id,'source' if side==0 else 'older reconstruction',[(int(i),round(float(loss[i]),3)) for i in ids])
