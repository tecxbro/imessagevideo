"""Measure only the bounded semantic search glyphs during the native fade."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy import ndimage
from PIL import Image
from trace_glyphs import trace_alpha
REF=Path(__file__).resolve().parent;layers=[];records=[];out=REF/'assets/root-query-fade-measure';out.mkdir(exist_ok=True)
proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',"select='between(n,540,564)'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
for n in range(540,565):
 raw=proc.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
 rgb=np.frombuffer(raw,np.uint8).reshape(1080,1920,3)[235:410,395:1565].astype(float);g=rgb.mean(2);neutral=rgb.max(2)-rgb.min(2)<18
 # Reject isolated codec speckle; retain semantic glyph optical support.
 colored=rgb.max(2)-rgb.min(2)>18
 labels,_=ndimage.label(colored,np.ones((3,3)));excluded=np.zeros(g.shape,bool)
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is not None and (labels[sl]==i+1).sum()>40:excluded|=ndimage.binary_fill_holes(labels==i+1)
 excluded=ndimage.binary_dilation(excluded,iterations=5)
 a=np.clip((253-g)/253,0,1)*neutral*(~excluded);a[a<2.5/253]=0
 support=ndimage.binary_dilation(a>5/253,iterations=2);a*=support
 peak=float(a.max());children=[]
 if peak>3/253:
  normalized=a/peak;prev=0
  for i in range(16):
   d,stats=trace_alpha(normalized,threshold=(i+.5)/16)
   if not d:continue
   cumulative=(i+1)/16;opacity=(cumulative-prev)/max(1-prev,1e-9);prev=cumulative
   children.append(dict(id=f'root-query-fade-{n}-outline-{i}',type='path',d=d,fill='#000000',opacity=opacity,semanticText='Searching the Agent Phone Book… — native search capsule border, magnifier and semantic copy',editability='Native semantic glyph optical contour pose; not live text.'))
  layers.append(dict(id=f'root-query-fade-pose-{n}',type='group',x=395,y=235,start=n/30,end=(n+1)/30,opacity=peak,children=children,sourceFrame=n))
 records.append(dict(frame=n,peakAlpha=peak,nativeOutlineLayers=len(children)))
 if n in [540,545,550,555,560,564]:Image.fromarray(rgb.astype('uint8')).save(out/f'query-{n}.png')
proc.stdout.close();assert proc.wait()==0
spec=dict(scope=[[540,564]],layers=layers,measurements=records,notice='Bounded actual search glyph optical poses only. Native contours and separate per-frame opacity preserve actual moving/fading text. No rectangle/source-frame/video imagery; the orbit logos remain independent.')
(REF/'root-query-fade-patch.json').write_text(json.dumps(spec,indent=2));print(dict(frames=len(records),layers=len(layers),last=records[-1]))
