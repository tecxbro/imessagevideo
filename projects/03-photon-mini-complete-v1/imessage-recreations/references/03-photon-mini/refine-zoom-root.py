"""Reconstruct the four actual Zoom-card entry poses, independently of other cards."""
from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
AS=REF/'assets/root-zoom';AS.mkdir(exist_ok=True);N=REF/'assets/root-zoom-measure';layers=[];records=[]
for n in range(899,903):
 a=np.array(Image.open(N/f'frame-{n}.png').convert('RGB')).astype(float);g=a.mean(2);mask=(g>218)&(g<240)&(a.max(2)-a.min(2)<12);mask[550:]=0;lab,_=ndimage.label(mask,np.ones((3,3)));options=[]
 for i,sl in enumerate(ndimage.find_objects(lab)):
  if sl is not None:
   yy,xx=sl;area=int((lab[sl]==i+1).sum())
   if xx.start>600 and area>1000:options.append((area,i+1,sl))
 _,label,sl=max(options);yy,xx=sl;core=lab==label
 # Fill each horizontal material span, including black/gray copy, while retaining
 # the actual curved outer boundary and the sloped perspective top edge.
 filled=np.zeros_like(core)
 for y in range(yy.start,yy.stop):
  xs=np.where(core[y])[0]
  if len(xs):filled[y,xs[0]:xs[-1]+1]=True
 extent=ndimage.binary_dilation(filled,iterations=3);x0=max(0,xx.start-3);x1=min(1920,xx.stop+3);y0=max(0,yy.start-3);y1=min(1080,yy.stop+3);roi=a[y0:y1,x0:x1];gray=g[y0:y1,x0:x1];local=extent[y0:y1,x0:x1]
 colors,counts=np.unique(roi[(core[y0:y1,x0:x1])].astype(np.uint8),axis=0,return_counts=True);body_color=colors[counts.argmax()];body_gray=float(body_color.mean());alpha=np.clip((253-gray)/(253-body_gray),0,1)*local;alpha[filled[y0:y1,x0:x1]]=1
 children=[]
 # The outer material is native, including its per-pose corner/perspective shape.
 previous=0.
 for level in range(5):
  d,_=trace_alpha(alpha,threshold=(level+.5)/5)
  if not d:continue
  cumulative=(level+1)/5;opacity=(cumulative-previous)/max(1-previous,1e-9);previous=cumulative;children.append({'id':f'root-zoom-body-{n}-{level}','type':'path','d':d,'fill':'#'+''.join(f'{int(v):02x}' for v in body_color),'opacity':opacity})
 # Actual semantic footer outlines preserve the changing perspective/kerning.
 # Black title and gray subtitle are separated by their actual connected ink rows.
 ink=(body_gray-gray).clip(0);ink*=ndimage.binary_erosion(filled[y0:y1,x0:x1],iterations=3,border_value=1);ys=np.where((ink>10).sum(1)>10)[0];rows=[]
 for y in ys:
  if not rows or y>rows[-1][-1]+8:rows.append([int(y)])
  else:rows[-1].append(int(y))
 rows=[r for r in rows if r[-1]-r[0]>3]
 for ri,row in enumerate(rows):
  gy0=max(0,row[0]-3);gy1=min(ink.shape[0],row[-1]+4);z=ink[gy0:gy1];positive=z[z>8];peak=float(np.percentile(positive,97));alph=np.clip(z/max(peak,1),0,1);previous=0.
  for level in range(5):
   d,_=trace_alpha(alph,threshold=(level+.5)/5)
   if not d:continue
   cumulative=(level+1)/5*peak/body_gray;opacity=(cumulative-previous)/max(1-previous,1e-9);previous=cumulative;children.append({'id':f'root-zoom-footer-{n}-row{ri}-contour{level}','type':'path','d':d,'y':gy0,'fill':'#000000','opacity':opacity,'semanticText':'Zoom Meeting' if ri==0 else 'Join in 5 minutes','editability':'Native semantic glyph outlines with measured perspective and softness; not live text.'})
 # The white/purple rich-card interior is a bounded original UI texture. It ends
 # exactly at the measured native footer frontier, never includes another card.
 if n>=901:
  width=x1-x0;height=max(0,yy.start+25);rgba=np.zeros((height,width,4),np.uint8);rgba[:,:,:3]=a[:height,x0:x1].astype(np.uint8)
  # Each column's first footer material pixel defines its sloped upper edge.
  for cx in range(width):
   x=x0+cx;ys_=np.where(filled[:,x])[0]
   if len(ys_):stop=int(ys_[0]);rgba[:min(height,stop),cx,3]=255
  # Exclude optical crop margin outside the actual card plane.
  rgba[:,:max(0,xx.start-x0),3]=0;rgba[:,xx.stop-x0:,3]=0
  asset=AS/f'zoom-ui-{n}.png';Image.fromarray(rgba).save(asset);layers.append({'id':f'root-zoom-ui-{n}','type':'image','src':str(asset),'x':x0,'y':0,'width':width,'height':height,'start':n/30,'end':(n+1)/30,'sourceFrame':n,'editability':'Strictly bounded original rich-card UI interior, bitmap copy. Independent native placement; no other card/background/full frame.'})
 layers.append({'id':f'root-zoom-native-pose-{n}','type':'group','children':children,'x':x0,'y':y0,'start':n/30,'end':(n+1)/30,'sourceFrame':n,'semanticText':'Zoom Meeting / Join in 5 minutes'})
 records.append({'frame':n,'footerBounds':[xx.start,yy.start,xx.stop,yy.stop],'bodyColor':body_color.tolist(),'footerInkRows':[[r[0]+y0,r[-1]+y0+1] for r in rows]})
spec={'scope':[[891,902]],'layers':layers,'measurements':records,'notice':'891–898 Zoom is absent; 899–902 actual independent card poses. Native material/footer outline geometry, bounded original UI art for 901–902 only. No full-frame playback.'};(REF/'root-zoom-patch.json').write_text(json.dumps(spec,indent=2));print(records)
