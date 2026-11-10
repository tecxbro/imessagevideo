from pathlib import Path
import sys,json,subprocess
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
P=Path(__file__).resolve().parent
A=P/'lunch-chrome-v16-aperture-source';A.mkdir(exist_ok=True)
measure=json.loads((P/'lunch-chrome-v16-measurements.json').read_text())
by_frame={r['frame']:r for r in measure['frames']}
process=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-filter_threads','1','-i',str(P/'source.mp4'),'-vf',"select='between(n,495,520)'",'-fps_mode','passthrough','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
rows=[]
try:
 for frame in range(495,521):
  needed=1920*1080*3
  raw=bytearray()
  while len(raw)<needed:
   b=process.stdout.read(needed-len(raw))
   if not b:break
   raw.extend(b)
  if len(raw)!=needed:raise ValueError('Incomplete decode'+str(frame))
  image=Image.frombytes('RGB',(1920,1080),bytes(raw));image.save(A/f'{frame:04}.png')
  rgb=np.asarray(image);mask=np.uint8(np.max(rgb[:180,700:1220],axis=2)<45)
  count,labels,stats,centroids=cv2.connectedComponentsWithStats(mask,8)
  found=[]
  for i in range(1,count):
   x,y,w,h,area=stats[i];cx,cy=centroids[i]
   if 150<w<330 and 20<h<100 and 2.5<w/h<5.5 and 950<cx+700<970:
    found.append(dict(bbox=[int(x+700),int(y),int(x+700+w),int(y+h)],black_pixels=int(area),center=[float(x+700+w/2),float(y+h/2)],top_censored=bool(y==0)))
  rows.append(dict(frame=frame,candidates=found,hardware_fit=by_frame[frame]['measurement'],prior=by_frame[frame]['old_camera']))
finally:
 process.stdout.close()
 if process.poll() is None:process.terminate()
 process.wait()
(P/'lunch-chrome-v16-aperture.json').write_text(json.dumps(dict(frames=rows,notice='Opaque Dynamic Island component centers independently measure physicalY while fully visible; outer dark-bezel modes measure scale. Missing/censored island frames keep original physical camera. MessagesUI/header/preview are untouched.'),indent=2))
for row in rows:print(row['frame'],row['candidates'])
