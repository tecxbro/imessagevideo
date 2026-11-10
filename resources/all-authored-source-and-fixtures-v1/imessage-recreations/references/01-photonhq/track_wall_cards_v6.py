"""Independent opaque UI components, measured per material, never whole rows.

The former nonwhite union joined neighboring materials at a handoff. Separate
body-color masks preserve individual boundaries; internal holes are filled so
copy remains in its bounded component. Only static component artwork is saved.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage,optimize
P=Path(__file__).parent;B=P/'wall-v6-measure';A=P/'assets/wall-cards-v6';A.mkdir(exist_ok=True)

def source(f):return B/('wall' if f<391 else 'wall-late')/f'{f-(335 if f<391 else 390):03d}.png'
def components(im):
 a=np.asarray(im).astype(np.int16);r,g,b=a.transpose(2,0,1);lo=a.min(2);hi=a.max(2)
 masks={'calls':hi<78,'blue':(b-r>55)&(b-g>7),'green':(g-r>8)&(g-b>8),'telegram':(b-r>12)&(b-r<=70)&(b-g>4)&(r>150),'gray':(hi-lo<9)&(lo>175)&(hi<250)}
 out=[]
 for material,raw in masks.items():
  raw[450:640]=False
  # Closing repairs letters/copy within a body but cannot bridge separate cards.
  mask=ndimage.binary_closing(raw,structure=np.ones((2,2)),border_value=0)
  labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel())
  for i,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is None:continue
   yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start;area=int(sizes[i]);edge=xx.start<3 or xx.stop>1917 or yy.start<3 or yy.stop>1077
   if not ((area>500 and w>50 and h>8 and w/h>1.35) or (edge and area>120 and w>35 and h>2)):continue
   if w>1250 or h>310 or (material=='calls' and (h<35 or area/(w*h)<.4)):continue
   body=ndimage.binary_fill_holes(labels[sl]==i)
   # Copy alpha includes body and enclosed text, not adjacent cards/corner pixels.
   box=(xx.start,yy.start,xx.stop,yy.stop);crop=np.array(im.crop(box));crop[~body]=253
   fp=np.asarray(Image.fromarray(crop).resize((80,24),Image.Resampling.BILINEAR),dtype=np.float32)/255
   out.append({'box':list(map(int,box)),'w':w,'h':h,'cx':(box[0]+box[2])/2,'cy':(box[1]+box[3])/2,'area':area,'material':material,'fp':fp})
 # Gray controls/portraits enclosed in a black call are not a separate bubble.
 calls=[x for x in out if x['material']=='calls']
 return [x for x in out if x['material']!='gray' or not any(x['box'][0]>=c['box'][0] and x['box'][1]>=c['box'][1] and x['box'][2]<=c['box'][2] and x['box'][3]<=c['box'][3] for c in calls)]

def overlap(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
tracks=[];frames={}
for f in range(336,465):
 im=Image.open(source(f)).convert('RGB');current=components(im);frames[f]=current;active=[t for t in tracks if t['records'][-1]['frame']==f-1];cost=np.full((len(active),len(current)),1e4)
 for i,t in enumerate(active):
  prev=t['records'][-1]
  for j,c in enumerate(current):
   if c['material']!=prev['material']:continue
   dx=abs(c['cx']-prev['cx']);dy=abs(c['cy']-prev['cy'])
   if dx>250 or dy>140:continue
   mse=float(((c['fp']-prev['fp'])**2).mean());size=abs(np.log(c['w']/prev['w']))+abs(np.log(c['h']/prev['h']));cost[i,j]=mse*10+.3*(dx/300+dy/150)+.05*size
 assigned=set()
 if len(active) and current:
  ii,jj=optimize.linear_sum_assignment(cost)
  for i,j in zip(ii,jj):
   if cost[i,j]<.9:active[i]['records'].append({'frame':f,**current[j]});assigned.add(j)
 for j,c in enumerate(current):
  if j not in assigned:tracks.append({'id':f'wall-native-card-v6-{len(tracks):03d}','records':[{'frame':f,**c}]})
 print(f,'components',len(current),'tracks',len(tracks),flush=True)
ledgers=[];layers=[]
for t in tracks:
 rs=t['records'];material=rs[0]['material']
 def quality(r):
  x1,y1,x2,y2=r['box'];xc=x1<3 or x2>1917;yc=y1<3 or y2>1077
  return (int(not xc)+int(not yc),r['area'])
 ref=max(rs,key=quality);box=ref['box'];im=Image.open(source(ref['frame'])).convert('RGB');art=im.crop(box).convert('RGBA')
 # Recover this component's body alpha in the reference material only.
 aa=np.asarray(im).astype(np.int16);r,g,b=aa.transpose(2,0,1);lo=aa.min(2);hi=aa.max(2)
 raw={'calls':hi<78,'blue':(b-r>55)&(b-g>7),'green':(g-r>8)&(g-b>8),'telegram':(b-r>12)&(b-r<=70)&(b-g>4)&(r>150),'gray':(hi-lo<9)&(lo>175)&(hi<250)}[material]
 raw=raw[box[1]:box[3],box[0]:box[2]];raw=ndimage.binary_fill_holes(ndimage.binary_closing(raw,structure=np.ones((2,2)),border_value=1));art.putalpha(Image.fromarray(np.uint8(raw)*255))
 asset=A/(t['id']+'.png');art.save(asset);rw,rh=art.size;tracks_out={k:[]for k in ['x','y','scaleX','scaleY']}
 for r in rs:
  x1,y1,x2,y2=r['box'];sx=r['w']/rw;sy=r['h']/rh;tx=x1;ty=y1;xc=x1<3 or x2>1917;yc=y1<3 or y2>1077
  if yc and not xc:
   sy=sx
   if y1<3:ty=y2-rh*sy
  elif xc and not yc:
   sx=sy
   if x1<3:tx=x2-rw*sx
  elif xc and yc:
   hs=[c['h']for c in frames[r['frame']]if c['material']==material and c['box'][1]>3 and c['box'][3]<1077];rhs=[c['h']for c in frames[ref['frame']]if c['material']==material and c['box'][1]>3 and c['box'][3]<1077]
   scale=float(np.median(hs)/np.median(rhs)) if hs and rhs else max(sx,sy);sx=sy=scale
   if x1<3:tx=x2-rw*sx
   if y1<3:ty=y2-rh*sy
  for k,v in [('x',tx),('y',ty),('scaleX',sx),('scaleY',sy)]:tracks_out[k].append({'t':r['frame']/30,'value':float(v),'ease':'linear'})
 layer={'id':t['id'],'type':'image','src':str(asset.resolve()),'width':rw,'height':rh,'start':rs[0]['frame']/30,'end':(rs[-1]['frame']+1)/30,'keyframes':tracks_out,'opacity':1,'semanticText':'Independent original '+material+' UI component','bitmapLimitation':'Internal static copy/artwork is bitmap; native position/scale/lifetime remain editable. No inferred fade or vertical collapse at OCR loss.'}
 layers.append(layer);ledgers.append({'id':t['id'],'material':material,'source_frame':ref['frame'],'source_bounds':box,'asset':str(asset.relative_to(P)),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'first_frame':rs[0]['frame'],'last_frame':rs[-1]['frame'],'observations':len(rs),'clipped_reference':box[0]<3 or box[1]<3 or box[2]>1917 or box[3]>1077})
 # All tracks remain inspectable without retaining raster frames in memory.
(B/'wall-native-layers.json').write_text(json.dumps(layers,indent=2)+'\n');(B/'wall-card-provenance.json').write_text(json.dumps({'cards':ledgers,'diagnosis':'OCR loss was treated as a fade and scaleY collapse even while opaque source cards remained. Track actual component poses/lifetimes and keep opacity1; separate material masks prevent contamination from neighboring cards.'},indent=2)+'\n')
print('native static cards',len(layers))
