"""Measure native phone-number cell outlines through the rapid unfold.
Each path is one bounded text element; no video or whole-frame layer is used.
"""
from pathlib import Path
import json,subprocess,sys,copy,hashlib
import numpy as np
from scipy import ndimage
from PIL import Image
from trace_glyphs import trace_alpha
REF=Path(__file__).resolve().parent;ROOT=REF.parents[1];first,last=420,434
out=REF/'assets/phonebook-unfold-measure';out.mkdir(exist_ok=True)
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',f"select='between(n,{first},{last})'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
layers=[];records=[]
for n in range(first,last+1):
 raw=p.stdout.read(1920*1080*3)
 if len(raw)!=1920*1080*3:raise ValueError('Incomplete native source')
 a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);g=a.mean(2);Image.fromarray(a).save(out/f'frame-{n}.png')
 ys=np.where((g<246).sum(1)>20)[0];rows=[]
 for y in ys:
  if not rows or y>rows[-1][-1]+3:rows.append([int(y)])
  else:rows[-1].append(int(y))
 counts=[]
 for ri,row in enumerate(rows):
  y0=max(0,row[0]-2);y1=min(1080,row[-1]+3);mask=g[y0:y1]<246;xs=np.where(mask.any(0))[0];spans=[]
  for x in xs:
   if not spans or x>spans[-1][-1]+22:spans.append([int(x)])
   else:spans[-1].append(int(x))
  counts.append(len(spans))
  for ci,span in enumerate(spans):
   x0=max(0,span[0]-2);x1=min(1920,span[-1]+3);ink=np.clip(253-g[y0:y1,x0:x1],0,253);positive=ink[ink>7]
   if not len(positive):continue
   peak=float(np.percentile(positive,95));alpha=np.clip(ink/max(peak,1),0,1)
   # Restrict the small cell to the actual number's glyph frontier.
   alpha*=ndimage.binary_dilation(ink>4,iterations=1)
   contours=[];previous=0.
   for level in range(5):
    d,stats=trace_alpha(alpha,threshold=(level+.5)/5)
    if not d:continue
    cumulative=(level+1)/5*peak/253;opacity=(cumulative-previous)/max(1-previous,1e-9);previous=cumulative
    contours.append({'id':f'pb-native-unfold-{n}-r{ri}-c{ci}-contour{level}','type':'path','d':d,'fill':'#000000','opacity':opacity})
   if contours:layers.append({'id':f'pb-native-unfold-{n}-r{ri}-c{ci}','type':'group','children':contours,'x':x0,'y':y0,'start':n/30,'end':(n+1)/30,'sourceFrame':n,'semanticText':'Phone-number field cell','editability':'Native nested semantic glyph contours preserving optical softness; not live text. Independently bounded number cell and frame pose.','measuredBounds':[x0,y0,x1,y1]})
 records.append({'frame':n,'rows':len(rows),'cellsPerRow':counts})
p.stdout.close();assert p.wait()==0
spec={'changed_frame_ranges':[[first,last]],'gate_start':435/30,'gatedPrefixes':['pb-early-','pb-number-','pb-glyph-'],'layers':layers,'measurements':records,'notice':'Native bounded phone-number glyph outlines for changing tracking/kerning; no complete-frame/runtime source-video asset.'}
(REF/'phonebook-native-unfold.json').write_text(json.dumps(spec,indent=2));print(json.dumps({'layers':len(layers),'measurements':records}))
