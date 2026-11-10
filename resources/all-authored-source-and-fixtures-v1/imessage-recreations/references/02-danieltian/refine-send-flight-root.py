"""Separate the five-frame flying message material, native copy and send actor."""
from pathlib import Path
import json,numpy as np
from scipy import ndimage
from PIL import Image
from trace_glyphs import trace_alpha
REF=Path(__file__).resolve().parent;AS=REF/'assets/root-send-flight';AS.mkdir(exist_ok=True)
boxes={175:(410,340,1710,710),176:(500,220,1770,560),177:(590,70,1800,410),178:(630,0,1830,255),179:(680,0,1870,130)}
inks={175:(470,410,1600,610),176:(580,285,1710,505),177:(650,130,1750,335),178:(700,0,1780,185),179:(720,0,1820,55)}
layers=[];records=[]
for n in range(175,180):
 a=np.array(Image.open(REF/f'assets/root-early-end-measure/frame-{n:04}.png').convert('RGB'));x0,y0,x1,y1=boxes[n];rgb=a[y0:y1,x0:x1].astype(float);g=rgb.mean(2);inkbounds=inks[n];inkregion=np.zeros(g.shape,bool);ix0,iy0,ix1,iy1=inkbounds;inkregion[max(0,iy0-y0):iy1-y0,max(0,ix0-x0):ix1-x0]=True
 dark=ndimage.grey_closing(g,size=(25,25))-g;inkmask=ndimage.binary_dilation((dark>1.5)&inkregion,iterations=3)&inkregion
 # Remove the separate send control from every material sample, including glow.
 control=(rgb.max(2)-rgb.min(2)>60)&(np.indices(g.shape)[1]+x0>1480)&(np.indices(g.shape)[0]+y0>520);control=ndimage.binary_dilation(ndimage.binary_fill_holes(control),iterations=10)
 valid=~(inkmask|control);den=ndimage.gaussian_filter(valid.astype(float),6);material=np.stack([np.divide(ndimage.gaussian_filter(rgb[:,:,c]*valid,6),den,out=np.full_like(den,253.),where=den>.01) for c in range(3)],2);material=np.clip(material,0,255);asset=AS/f'material-{n}.png';Image.fromarray(np.uint8(np.rint(material))).save(asset)
 children=[dict(id=f'root-send-flight-material-{n}',type='image',src=str(asset),x=x0,y=y0,width=x1-x0,height=y1-y0,semanticText='Procedurally fitted low-frequency moving bubble surface',editability='Smooth RGB material fitted only from non-ink/non-control samples. No original message glyph/caret/control survives; native semantic copy is separate.')]
 alpha=np.clip(((material-rgb)*material).sum(2)/np.maximum((material*material).sum(2),1),0,1)*inkmask;peak=float(alpha.max());previous=0
 if peak>.01:
  for i in range(16):
   d,stats=trace_alpha(alpha/peak,threshold=(i+.5)/16)
   if not d:continue
   cumulative=(i+1)/16;opacity=(cumulative-previous)/max(1-previous,1e-9);previous=cumulative;children.append(dict(id=f'root-send-flight-glyph-{n}-{i}',type='path',d=d,x=x0,y=y0,fill='#000000',opacity=opacity*peak if i==0 else opacity,semanticText='muse, my boss wants a team offsite tmr. can u help?',editability='Native semantic glyph-outline optical pose; not live text.'))
  # Peak opacity must multiply the composite, rather than only its first contour.
  glyphs=children[1:]
  if glyphs:
   glyphs[0]['opacity']/=peak;children=children[:1]+[dict(id=f'root-send-flight-glyphs-{n}',type='group',opacity=peak,children=glyphs)]
 if n<179:
  cr=a[500:760,1480:1760].astype(float);mask=(cr[:,:,2]-cr[:,:,0]>60)&(cr[:,:,1]-cr[:,:,0]>20);lab,_=ndimage.label(mask,np.ones((3,3)));opts=[]
  for i,sl in enumerate(ndimage.find_objects(lab)):
   if sl is None:continue
   yy,xx=sl;count=int((lab[sl]==i+1).sum())
   if count>1500 and yy.stop-yy.start>50:opts.append((count,i+1))
  _,i=max(opts);support=ndimage.binary_dilation(ndimage.binary_fill_holes(lab==i),iterations=10);yy,xx=np.where(support);bx0,bx1,by0,by1=int(xx.min()),int(xx.max()+1),int(yy.min()),int(yy.max()+1);rgba=np.dstack([np.uint8(cr[by0:by1,bx0:bx1]),np.uint8(support[by0:by1,bx0:bx1])*255]);controlfile=AS/f'send-control-{n}.png';Image.fromarray(rgba).save(controlfile);children.append(dict(id=f'root-send-flight-control-{n}',type='image',src=str(controlfile),x=1480+bx0,y=500+by0,width=bx1-bx0,height=by1-by0,sourceFrame=n,semanticText='Original glowing iMessage send control',editability='Strictly bounded independent original control artwork; no message copy or other UI region.'))
 layers.append(dict(id=f'root-send-flight-pose-{n}',type='group',start=n/30,end=(n+1)/30,children=children,sourceFrame=n));records.append(dict(frame=n,materialBounds=list(boxes[n]),inkBounds=list(inks[n]),glyphPeakOpacity=peak,materialSampleMaskExcludesInkAndControl=True))
(REF/'root-send-flight-patch.json').write_text(json.dumps(dict(scope=[[175,179]],layers=layers,measurements=records,notice='The old outgoing message used a later/incorrect font width and an oversized sharp surface. Separate actual native glyph poses and generated non-UI smooth material. Independent original send-control glow175–178; genuine particle burst179+ remains separate. All prior0–174 and180+ states preserved.'),indent=2));print({'frames':len(records),'layers':len(layers)})
