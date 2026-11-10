from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,subprocess
P=Path('/workspace/imessage-recreations/references/03-photon-mini');proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(P/'source.mp4'),'-vf','select=between(n\\,495\\,617)','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE);out=[];size=1920*1080*3
for f in range(495,618):
 raw=proc.stdout.read(size)
 if len(raw)!=size:raise RuntimeError((f,len(raw)))
 a=np.frombuffer(raw,'uint8').reshape(1080,1920,3)[100:1080,800:1420].astype('int16');m=(a[:,:,2]>150)&(a[:,:,1]>100)&(a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]-a[:,:,0]>25);lab,n=ndimage.label(m);cs=[]
 for i,b in enumerate(ndimage.find_objects(lab),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start;area=int((lab[b]==i).sum())
  if w>70 and h>15 and area>500:cs.append({'bbox':[x.start+800,y.start+100,x.stop+800,y.stop+100],'w':w,'h':h,'area':area,'median_RGB':np.median(a[b][lab[b]==i],axis=0).tolist()})
 cs.sort(key=lambda z:z['area'],reverse=True);out.append({'frame':f,'blue':cs[0] if cs else None})
proc.wait();(P/'lunch-blue-v14-measurements.json').write_text(json.dumps(out,indent=2));print([r for r in out if 503<=r['frame']<=521 or r['frame'] in [530,551,600,617]])
