"""Measure actual typed/revealed text poses, preserving native graphic geometry."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy import ndimage
from PIL import Image
from trace_glyphs import trace_alpha
REF=Path(__file__).resolve().parent;AS=REF/'assets/root-copy';AS.mkdir(exist_ok=True);N=REF/'assets/root-copy-measure';N.mkdir(exist_ok=True)
intervals=[(95,174),(1143,1250)];layers=[];records=[];expr='+'.join(f'between(n,{a},{b})' for a,b in intervals);frames=[n for lo,hi in intervals for n in range(lo,hi+1)]
proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',f"select='{expr}'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
def contours(alpha,prefix,fill,semantic,levels=10):
 children=[];previous=0.
 for level in range(levels):
  d,_=trace_alpha(alpha,threshold=(level+.5)/levels)
  if not d:continue
  cumulative=(level+1)/levels;opacity=(cumulative-previous)/max(1-previous,1e-9);previous=cumulative
  children.append({'id':prefix+f'-contour{level}','type':'path','d':d,'fill':fill,'opacity':opacity,'semanticText':semantic,'editability':'Native semantic glyph/outline pose; not live text.'})
 return children
for n in frames:
 raw=proc.stdout.read(1920*1080*3)
 if len(raw)!=1920*1080*3:raise ValueError('Incomplete source stream')
 a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3)
 if n in (95,110,126,145,165,174,1143,1158,1170,1180,1200,1214,1220,1237,1240,1250):Image.fromarray(a).save(N/f'frame-{n}.png')
 composer=n<200;x0,y0,x1,y1=(260,400,1540,675) if composer else (0,350,1920,750);rgb=a[y0:y1,x0:x1].astype(float);g=rgb.mean(2);neutral=rgb.max(2)-rgb.min(2)<18
 support=ndimage.binary_dilation(neutral&(g<180),iterations=2) if composer else neutral&(g<251)
 alpha=np.clip((253-g)/253,0,1)*neutral*support;semantic='muse, my boss wants a team offsite tmr. can u help? (partial typing/caret)' if composer else 'It brings [provider] into your group chats. / It brings all the agents into your group chats.'
 children=contours(alpha,f'root-copy-black-{n}','#000000',semantic)
 colored=(rgb.max(2)-rgb.min(2)>20)&(rgb.min(2)<230)
 if not composer and n<1236:
  lab,_=ndimage.label(colored,np.ones((3,3)))
  for i,sl in enumerate(ndimage.find_objects(lab)):
   if sl is None:continue
   yy,xx=sl;count=int((lab[sl]==i+1).sum())
   if count<5:continue
   mask=ndimage.binary_dilation(ndimage.binary_fill_holes(lab[sl]==i+1),iterations=1);crop=rgb[sl].astype(np.uint8);rgba=np.dstack([crop,np.uint8(mask)*255]);rgba[~mask,:3]=0;asset=AS/f'provider-color-{n}-{i}.png';Image.fromarray(rgba).save(asset);children.append({'id':f'root-copy-brand-color-{n}-{i}','type':'image','src':str(asset),'x':xx.start,'y':yy.start,'width':xx.stop-xx.start,'height':yy.stop-yy.start,'sourceFrame':n,'editability':'Strictly bounded original colored provider icon artwork. Native copy and lifetimes are separate.'})
 if not composer and n>=1236 and colored.sum()>20:
  pixels=rgb[colored].astype(np.uint8);colors,c=np.unique(pixels,axis=0,return_counts=True);ink=colors[c.argmax()];blue_alpha=np.clip((253-rgb[:,:,0])/max(1,253-float(ink[0])),0,1)*ndimage.binary_dilation(colored,iterations=1);fill='#'+''.join(f'{int(v):02x}' for v in ink);children.extend(contours(blue_alpha,f'root-copy-cta-{n}',fill,'photon.codes/beta'))
 if children:layers.append({'id':f'root-copy-pose-{n}','type':'group','x':x0,'y':y0,'start':n/30,'end':(n+1)/30,'children':children,'sourceFrame':n,'semanticText':semantic})
 records.append({'frame':n,'composer':composer,'nativeContourLayers':sum(c['type']=='path' for c in children),'boundedOriginalColorLayers':sum(c['type']=='image' for c in children)})
proc.stdout.close();assert proc.wait()==0
spec={'scope':intervals,'layers':layers,'measurements':records,'notice':'Actual per-native-frame typed/caret and provider/final-copy outline poses. Colored provider marks remain bounded original artwork; no source-video or full-frame raster layer. Query body/send and all reserved flight/header/phonebook work retained.'};(REF/'root-copy-patch.json').write_text(json.dumps(spec,indent=2));print({'frames':len(records),'layers':len(layers)})
