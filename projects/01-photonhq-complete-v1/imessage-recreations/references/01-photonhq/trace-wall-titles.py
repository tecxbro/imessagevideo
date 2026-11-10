from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path('/workspace/imessage-recreations/references/01-photonhq');scene=json.loads((R/'scene-wall-v4.json').read_text())
phases=[('sms',270,'10,000+ SMS'),('calls',336,'8000+ voice minutes'),('imessage',372,'Unlimited iMessage'),('whatsapp',408,'Unlimited WhatsApp'),('telegram',444,'Unlimited Telegram')]
# Directed marching-squares contour segments keep the black foreground on the right; holes therefore have opposite winding.
table={1:[(0,3)],2:[(1,0)],3:[(1,3)],4:[(2,1)],6:[(2,0)],7:[(2,3)],8:[(3,2)],9:[(0,2)],11:[(1,2)],12:[(3,1)],13:[(0,1)],14:[(3,0)]}
ledger=[]
for name,n,copy in phases:
 source=R/f'assets/wall-art/measure/{n:04d}.png';a=np.asarray(Image.open(source).convert('RGB'));alpha=(255-a[:,:,0])/255.;roi=alpha[470:620,200:1720];yy,xx=np.where(roi>.5);box=[int(xx.min()+200),int(yy.min()+470),int(xx.max()+201),int(yy.max()+471)];crop=alpha[box[1]:box[3],box[0]:box[2]];ar=np.pad(crop,1);tl,tr,br,bl=ar[:-1,:-1],ar[:-1,1:],ar[1:,1:],ar[1:,:-1];cases=(tl>=.5).astype(np.uint8)+2*(tr>=.5)+4*(br>=.5)+8*(bl>=.5);ys,xs=np.where((cases>0)&(cases<15));links={};points={}
 for y,x in zip(ys,xs):
  vals=[ar[y,x],ar[y,x+1],ar[y+1,x+1],ar[y+1,x]];case=int(cases[y,x]);segments=table.get(case)
  if case==5:segments=[(0,1),(2,3)] if sum(vals)/4>=.5 else [(0,3),(2,1)]
  if case==10:segments=[(1,2),(3,0)] if sum(vals)/4>=.5 else [(1,0),(3,2)]
  def edge(e):
   if e==0:key=('h',int(y),int(x));v0,v1=vals[0],vals[1];px,py=x,y;dx,dy=1,0
   elif e==1:key=('v',int(y),int(x+1));v0,v1=vals[1],vals[2];px,py=x+1,y;dx,dy=0,1
   elif e==2:key=('h',int(y+1),int(x));v0,v1=vals[3],vals[2];px,py=x,y+1;dx,dy=1,0
   else:key=('v',int(y),int(x));v0,v1=vals[0],vals[3];px,py=x,y;dx,dy=0,1
   f=(.5-v0)/(v1-v0) if v1!=v0 else .5;points[key]=(float(box[0]-.5+px+dx*f),float(box[1]-.5+py+dy*f));return key
  for e0,e1 in segments:
   k0,k1=edge(e0),edge(e1)
   if k0 in links and links[k0]!=k1:raise ValueError('Ambiguous directed boundary')
   links[k0]=k1
 loops=[]
 while links:
  start=next(iter(links));cur=start;poly=[]
  for _ in range(len(links)+1):
   poly.append(points[cur]);nxt=links.pop(cur,None)
   if nxt is None:raise ValueError('Open glyph contour')
   cur=nxt
   if cur==start:break
  else:raise ValueError('Contour did not close')
  # Preserve subpixel positions; collapse only collinear neighboring vertices.
  out=[]
  for i,p in enumerate(poly):
   a0=np.array(poly[i-1]);a1=np.array(p);a2=np.array(poly[(i+1)%len(poly)]);cross=np.cross(a1-a0,a2-a1)
   if abs(float(cross))>.0002:out.append(p)
  if len(out)>=3:loops.append(out)
 def num(v):return f'{v:.3f}'.rstrip('0').rstrip('.')
 d=' '.join('M'+' '.join((num(poly[0][0]),num(poly[0][1])))+' '+' '.join('L'+num(x)+' '+num(y) for x,y in poly[1:])+' Z' for poly in loops)
 index=next(i for i,l in enumerate(scene['layers']) if l.get('type')=='text' and l.get('text')==copy);old=scene['layers'][index];path=dict(id=old['id']+'-source-outlines',type='path',d=d,fill='#000000',start=old.get('start',0),end=old.get('end',scene['duration']),semanticText=copy,sourceFrame=n,sourceBounds=box,editability='Editable vector outlines; semantic copy retained in metadata, glyphs are not live text.')
 scene['layers'][index]=path
 ledger.append(dict(semantic_text=copy,source_frame=n,source_timestamp=n/30,source_bbox=box,source_png_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),mask='luma from red channel of isolated black title; contour threshold0.5; linear subpixel marching squares; foreground-right winding preserves counters',contours=len(loops),vertices=sum(map(len,loops)),path_sha256=hashlib.sha256(d.encode()).hexdigest(),editability=path['editability']))
 print(name,'contours',len(loops),'vertices',sum(map(len,loops)),flush=True)
scene['source']['notes']+=' Five wall headings are editable SVG glyph outlines traced from isolated source word masks; semantic copy and original frame/bounds are retained in provenance. Outlines preserve letter geometry but are not live editable text. Native vector antialiasing is measured separately.'
(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));(R/'wall-title-outline-provenance.json').write_text(json.dumps(ledger,indent=2))
