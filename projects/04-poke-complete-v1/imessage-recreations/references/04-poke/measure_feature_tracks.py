"""Track native gray feature-card bounds from actual source frames; no recreation pixels.
Output is a diagnostic measurement ledger for future motion fitting.
"""
from pathlib import Path
import subprocess,json
import numpy as np
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
p=Path(__file__).parent;s=json.loads((p/'scene.json').read_text())
labels=['Email','Calendar','Reminders','Automations','Image Search & Generation','Web Search & Browse']
groups=[]
for name in labels:
 groups.append(next(l for l in s['layers'] if any(c.get('text')==name for c in l.get('children',[]))))
def sample(track,t):
 keys=sorted(track,key=lambda k:k['t'])
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return keys[-1]['value']
import math
fps=30000/1001
requests=[29.5+i/10 for i in range(72)];frame_indices=[math.ceil(t*fps-1e-8) for t in requests]
select='+'.join(f'eq(n,{n})' for n in frame_indices)
proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(p/'source.mp4'),'-vf',f"select='{select}'",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
rows=[];i=0;shape=(1080,1440,3);nb=int(np.prod(shape))
while True:
 data=proc.stdout.read(nb)
 if not data:break
 if len(data)!=nb:raise RuntimeError('Partial decoded frame')
 requested=requests[i];frame_index=frame_indices[i];t=frame_index/fps;i+=1;a=np.frombuffer(data,dtype=np.uint8).reshape(shape)
 mask=(a.min(2)>210)&(a.max(2)<249)&((a.max(2).astype(int)-a.min(2))<6)
 mask=ndimage.binary_closing(mask,iterations=2); lab,n=ndimage.label(mask);boxes=[]
 for ob in ndimage.find_objects(lab):
  if not ob:continue
  yy,xx=ob;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w>750 and 60<h<300 and yy.start>2 and yy.stop<1078:boxes.append((xx.start,yy.start,w,h))
 if not boxes:continue
 pred=[]
 for g in groups:
  k=g['keyframes'];pred.append([sample(k['x'],t),sample(k['y'],t),1040*sample(k['scaleX'],t)])
 cost=np.array([[abs(b[1]-v[1])+abs(b[0]-v[0])*.4+abs(b[2]-v[2])*.2 for b in boxes] for v in pred])
 ids,cs=linear_sum_assignment(cost)
 for j,c in zip(ids,cs):
  if cost[j,c]>160:continue
  x,y,w,h=boxes[c];rows.append({'time':t,'requested_time':requested,'frame_index':frame_index,'feature':labels[j],'x':x,'y':y,'width':w,'height_including_tail':h,'diagnostic_assignment_cost':float(cost[j,c])})
code=proc.wait()
if code or i!=len(frame_indices):raise RuntimeError(f'Native frame selection failed: exit={code}, frames={i}/{len(frame_indices)}')
out={'source':'source.mp4','sampling_fps':10,'frame_selection':'ceil(requested_time*30000/1001), decoded directly by original frame index, exact presentation time recorded','dimensions':[1440,1080],'method':'Native decoded RGB24; gray component threshold210..249, chroma<6; small closing; full visible card bounds only. Labels assigned by measured anchor trajectory with cost guard. Review ambiguities before applying.','measurements':rows}
(p/'feature-track-measurements.json').write_text(json.dumps(out,indent=2));print('Tracked',len(rows),'card appearances in',i,'native source frames')
