"""Measured opaque native SMS/mail components between authorized flip phases."""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image
from scipy import ndimage,optimize
P=Path(__file__).parent;B=P/'early-walls-v7-measure';A=P/'assets/early-wall-cards-v7';A.mkdir(exist_ok=True)
def source(f):return B/f'frame-{f-(248 if f<282 else 263):03d}.png'
def components(im,phase):
 a=np.asarray(im).astype(np.int16);r,g,b=a.transpose(2,0,1);lo=a.min(2);hi=a.max(2);masks={'mail':lo<249}if phase=='mail'else{'green':(g-r>8)&(g-b>8),'gray':(hi-lo<9)&(lo>170)&(hi<250)};out=[]
 for material,mask in masks.items():
  mask[470:610]=False;mask=ndimage.binary_closing(mask,structure=np.ones((3,3)if phase=='mail'else(2,2)));labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel())
  for i,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is None:continue
   yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start;area=int(sizes[i]);edge=xx.start<3 or xx.stop>1917 or yy.start<3 or yy.stop>1077
   if not ((area>500 and w>50 and h>8 and w/h>1.35)or(edge and area>100 and w>35 and h>2)):continue
   if h>250 or w>1000 or(phase=='mail'and not((w>150 and h>50)or edge)):continue
   body=ndimage.binary_fill_holes(labels[sl]==i);box=[xx.start,yy.start,xx.stop,yy.stop];crop=np.array(im.crop(box));crop[~body]=253;fp=np.asarray(Image.fromarray(crop).resize((80,24),Image.Resampling.BILINEAR),dtype=np.float32)/255
   out.append({'box':box,'w':w,'h':h,'cx':(box[0]+box[2])/2,'cy':(box[1]+box[3])/2,'area':area,'material':material,'fp':fp})
 # A border component can enclose separate internal copy fragments. They are
 # parts of this same notification, never another card or output texture.
 return [q for q in out if not any(q is not o and q['w']*q['h']<o['w']*o['h'] and q['box'][0]>=o['box'][0]and q['box'][1]>=o['box'][1]and q['box'][2]<=o['box'][2]and q['box'][3]<=o['box'][3]for o in out)]
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['all','sms','mail'],default='all');parser.add_argument('--reuse-observations',action='store_true');args=parser.parse_args()
tracks=[];frames={};selected=list(range(249,282))+list(range(297,315))
if args.phase=='sms':selected=list(range(249,282))
if args.phase=='mail':selected=list(range(297,315))
if args.reuse_observations:
 tracks=json.load(open(B/('observations-'+args.phase+'.json')))
 for t in tracks:
  for r in t['records']:frames.setdefault(r['frame'],[]).append(r)
else:
 for f in selected:
  phase='sms'if f<282 else'mail';im=Image.open(source(f)).convert('RGB');cs=components(im,phase);frames[f]=cs;active=[t for t in tracks if t['records'][-1]['frame']==f-1];cost=np.full((len(active),len(cs)),1e4)
  for i,t in enumerate(active):
   prev=t['records'][-1]
   for j,c in enumerate(cs):
    if c['material']!=prev['material']:continue
    dx=abs(c['cx']-prev['cx']);dy=abs(c['cy']-prev['cy'])
    if dx>250 or dy>180:continue
    mse=float(((c['fp']-prev['fp'])**2).mean());size=abs(np.log(c['w']/prev['w']))+abs(np.log(c['h']/prev['h']));cost[i,j]=mse*10+.3*(dx/300+dy/180)+.05*size
  assigned=set()
  if len(active)and cs:
   ii,jj=optimize.linear_sum_assignment(cost)
   for i,j in zip(ii,jj):
    if cost[i,j]<.9:active[i]['records'].append({'frame':f,**cs[j]});assigned.add(j)
  for j,c in enumerate(cs):
   if j not in assigned:tracks.append({'id':f'early-wall-native-v7-{phase}-{len(tracks):03d}','records':[{'frame':f,**c}]})
  print(f,phase,len(cs),'cards',len(tracks),flush=True)
serial=[{'id':t['id'],'records':[{k:v for k,v in r.items()if k!='fp'}for r in t['records']]}for t in tracks];(B/('observations-'+args.phase+'.json')).write_text(json.dumps(serial,indent=2)+'\n')
ls=[];ledger=[]
if args.phase!='all' and (B/'native-layers.json').exists():
 oldls=json.load(open(B/'native-layers.json'));oldledger=json.load(open(B/'component-provenance.json'))['cards'];keep={q['id']for q in oldledger if (q['first_frame']>=297 if args.phase=='sms' else q['first_frame']<282)};ls=[l for l in oldls if l['id']in keep];ledger=[q for q in oldledger if q['id']in keep]
for t in tracks:
 rs=t['records'];material=rs[0]['material']
 def quality(r):
  x0,y0,x1,y1=r['box'];xc=x0<3 or x1>1917;yc=y0<3 or y1>1077
  return(int(not xc)+int(not yc),r['w']/r['h']if xc and not yc else r['h']/r['w']if yc and not xc else r['area'])
 front_frame=260 if material!='mail' else 300;front=[r for r in rs if r['frame']==front_frame];ref=front[0] if front else max(rs,key=lambda r:(quality(r)[0],r['area']));box=ref['box'];im=Image.open(source(ref['frame'])).convert('RGB');art=im.crop(box).convert('RGBA')
 if material!='mail':
  a=np.asarray(im).astype(np.int16);r,g,b=a.transpose(2,0,1);raw=(g-r>8)&(g-b>8)if material=='green'else(a.max(2)-a.min(2)<9)&(a.min(2)>170)&(a.max(2)<250);raw=raw[box[1]:box[3],box[0]:box[2]];raw=ndimage.binary_fill_holes(ndimage.binary_closing(raw,structure=np.ones((2,2)),border_value=1));art.putalpha(Image.fromarray(np.uint8(raw)*255))
 asset=A/(t['id']+'.png');art.save(asset);rw,rh=art.size;kf={k:[]for k in ['x','y','scaleX','scaleY']}
 for q in rs:
  x0,y0,x1,y1=q['box'];sx=q['w']/rw;sy=q['h']/rh;tx=x0;ty=y0;xc=x0<3 or x1>1917;yc=y0<3 or y1>1077
  if yc and not xc:
   sy=sx
   if y0<3:ty=y1-rh*sy
  elif xc and not yc:
   sx=sy
   if x0<3:tx=x1-rw*sx
  # A corner fragment uses the shared native material row scale, not its
  # progressively clipped height/width (which invented a scale collapse).
  elif xc and yc:
   hs=[c['h']for c in frames[q['frame']]if c['material']==material and c['box'][1]>3 and c['box'][3]<1077];rhs=[c['h']for c in frames[ref['frame']]if c['material']==material and c['box'][1]>3 and c['box'][3]<1077];s=float(np.median(hs)/np.median(rhs))if hs and rhs else max(sx,sy);sx=sy=s
   if x0<3:tx=x1-rw*s
   if y0<3:ty=y1-rh*s
  for k,v in [('x',tx),('y',ty),('scaleX',sx),('scaleY',sy)]:kf[k].append({'t':q['frame']/30,'value':float(v),'ease':'linear'})
 ls.append({'id':t['id'],'type':'image','src':str(asset.resolve()),'width':rw,'height':rh,'start':rs[0]['frame']/30,'end':(rs[-1]['frame']+1)/30,'opacity':1,'keyframes':kf,'semanticText':'Independent original '+material+' UI component','bitmapLimitation':'Internal original copy/artwork is static bitmap. Native measured camera/pose/lifecycle remain editable; no inferred OCR fade or scale collapse.'});ledger.append({'id':t['id'],'source_frame':ref['frame'],'source_bounds':box,'material':material,'first_frame':rs[0]['frame'],'last_frame':rs[-1]['frame'],'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest()})
(B/'native-layers.json').write_text(json.dumps(ls,indent=2)+'\n');(B/'component-provenance.json').write_text(json.dumps({'cards':ledger,'scope':[[249,281],[297,314]],'diagnosis':'Actual opaque SMS/mail states were incorrectly faded/collapsed when OCR disappeared. Track bodies/lifetimes independently of copy recognition; preserve the separately authorized local 3D component-flip phases.'},indent=2)+'\n');print('complete',len(ls),flush=True)
