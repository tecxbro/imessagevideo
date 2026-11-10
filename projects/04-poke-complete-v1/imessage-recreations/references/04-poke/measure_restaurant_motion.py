"""Measure a short fast-dismissal trajectory using authentic photo template, no browser."""
from pathlib import Path
import subprocess,json,numpy as np
from PIL import Image
p=Path(__file__).parent;fps=30000/1001;first,last=655,665
from fractions import Fraction
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=time_base,start_pts,avg_frame_rate','-of','json',str(p/'source.mp4')]))['streams'][0]
tb=Fraction(probe['time_base']);pts_step=Fraction(1,1)/Fraction(probe['avg_frame_rate'])/tb
if pts_step.denominator!=1:raise RuntimeError('Noninteger CFR timestamp stride; use explicit original frame index decode')
pts_step=int(pts_step);start_pts=int(probe.get('start_pts',0));first_pts=start_pts+first*pts_step;last_pts=start_pts+last*pts_step
filt=f"select='gte(pts,{first_pts})*lte(pts,{last_pts})',crop=168:1080:294:0"
proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-ss','21.8','-copyts','-i',str(p/'source.mp4'),'-vf',filt,'-fps_mode','passthrough','-frames:v',str(last-first+1),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
t=np.asarray(Image.open(p/'assets/ettan-photo.png').convert('RGB')).astype(np.float32)[:,4:164].reshape(168,20,8,3).mean(2)
rows=[]
for n in range(first,last+1):
 data=proc.stdout.read(168*1080*3)
 if len(data)!=168*1080*3:raise RuntimeError(f'Incomplete source frame{n}')
 a=np.frombuffer(data,dtype=np.uint8).reshape(1080,168,3).astype(np.float32)[:,4:164].reshape(1080,20,8,3).mean(2)
 best=[]
 for y in range(-120,801):
  lo=max(0,-y);hi=min(168,1080-y)
  if hi-lo<45:continue
  e=float(np.mean((t[lo:hi]-a[y+lo:y+hi])**2));best.append((e,y))
 best.sort();cost,y=best[0];rows.append({'frame_index':n,'time':n/fps,'ettan_photo_y':y,'sheet_y':y-320,'color_profile_mse':cost,'runner_up_mse':best[1][0]})
code=proc.wait()
if code:raise RuntimeError(f'FFmpeg exit{code}')
report={'source':'source.mp4','source_timebase':str(tb),'pts_stride':pts_step,'selection':'copyts, exact original timestamps derived from actual stream timebase,655..665','method':'Ettan168px artwork,20column-binned RGB row template; evaluate native vertical translation with partial-top support. Sheet origin=photoY−320. High MSE warrants manual review.','measurements':rows}
(p/'restaurant-motion-measurements.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
