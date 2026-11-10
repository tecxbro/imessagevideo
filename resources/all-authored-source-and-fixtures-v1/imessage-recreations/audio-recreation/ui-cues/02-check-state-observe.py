#!/usr/bin/env python3
"""Measure green agent-selection/check states, without inferring visible finger taps."""
from pathlib import Path
import json,subprocess
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
cv2.setNumThreads(1)
w,h=1200,850
producer=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(ROOT/'references/02-danieltian/source.mp4'),'-vf',"select='between(n,436,525)',format=rgb24,crop=1200:850:360:100",'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
records=[]
for n in range(436,526):
 raw=producer.stdout.read(w*h*3)
 if len(raw)!=w*h*3:raise RuntimeError(f'Incomplete frame {n}')
 a=np.frombuffer(raw,np.uint8).reshape(h,w,3).astype(np.int16)
 mask=(a[:,:,1]>a[:,:,0]+35)&(a[:,:,1]>a[:,:,2]+25)&(a[:,:,1]>90)
 count,labels,stats,centers=cv2.connectedComponentsWithStats(mask.astype(np.uint8),8)
 components=[]
 for index in range(1,count):
  x,y,cw,ch,area=stats[index]
  if area>=20 and cw>=4 and ch>=4:
   components.append({'bounds':[int(x+360),int(y+100),int(x+cw+360),int(y+ch+100)],'area':int(area),'center':[round(float(centers[index,0]+360),2),round(float(centers[index,1]+100),2)]})
 records.append({'frame':n,'green_control_components':components})
producer.stdout.close();assert producer.wait()==0
(OUT/'02-phonebook-check-observations.json').write_text(json.dumps({'source':'references/02-danieltian/source.mp4','fps':30,'roi':[360,100,1560,950],'records':records,'interpretation_limit':'Green checks are visible state changes; no pointer/finger action is established.'},indent=2)+'\n')
changes=[];previous=None
for row in records:
 current=len(row['green_control_components'])
 if current!=previous:
  changes.append(row);previous=current
print(json.dumps(changes))
