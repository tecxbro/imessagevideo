from pathlib import Path
from scipy import ndimage
import numpy as np,json,subprocess
P=Path('/workspace/imessage-recreations/references/03-photon-mini');proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(P/'source.mp4'),'-vf','select=between(n\\,495\\,617)','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE);out=[]
for f in range(495,618):
 a=np.frombuffer(proc.stdout.read(1920*1080*3),'uint8').reshape(1080,1920,3)[:450,800:1120];gray=a.mean(2);d=a.max(2).astype('int16')-a.min(2);record={'frame':f}
 for role,m,lo,hi,ctr in [('word',a.max(2)<120,150,230,954),('date',(a.max(2)<220)&(a.min(2)>80)&(d<8),130,190,967)]:
  lab,n=ndimage.label(ndimage.binary_closing(m,structure=np.ones((1,20))));cs=[]
  for i,b in enumerate(ndimage.find_objects(lab),1):
   if b is None:continue
   y,x=b;w=x.stop-x.start;h=y.stop-y.start
   if lo<w<hi and 12<h<45 and abs((x.start+x.stop)/2+800-ctr)<30:cs.append({'bbox':[x.start+800,y.start,x.stop+800,y.stop],'area':int((lab[b]==i).sum()),'top_censored':y.start==0})
  cs.sort(key=lambda q:q['bbox'][1]);record[role]=cs[0] if cs else None;record[role+'_candidates']=cs
 
 if record['date']:
  expected=record['date']['bbox'][1]-73;cs=record['word_candidates'];record['word']=min(cs,key=lambda q:abs(q['bbox'][1]-expected)) if cs else None
  if record['word'] and abs(record['word']['bbox'][1]-expected)>25:record['word']=None
 else:record['word']=None
 out.append(record)
proc.wait();(P/'lunch-header-v14-measurements.json').write_text(json.dumps(out,indent=2));print([r for r in out if r['frame'] in [495,510,530,551,560,563,566,570,575,617]])
