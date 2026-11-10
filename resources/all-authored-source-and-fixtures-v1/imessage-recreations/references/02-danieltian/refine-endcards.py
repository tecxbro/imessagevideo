from pathlib import Path
from PIL import Image
from scipy import ndimage
from trace_glyphs import trace_alpha
import numpy as np,json,hashlib
R=Path('/workspace/imessage-recreations/references/02-danieltian');scene=json.loads((R/'scene-v5-ui.json').read_text());patches={};ledger=[]
def image(n):
 p=R/f'assets/end-measure/{n:04d}.png'
 if n==30:p=R/'keyframes/01.00.png'
 if n==1080:p=R/'keyframes/36.00.png'
 return p,np.array(Image.open(p).convert('RGB'))
def outline(n,rois,semantic,exclude=None,fill='#000000'):
 p,a=image(n);alpha=np.zeros(a.shape[:2],dtype=float)
 for x0,y0,x1,y1 in rois:alpha[y0:y1,x0:x1]=(253-a[y0:y1,x0:x1,:].mean(2))/253
 alpha=np.clip(alpha,0,1)
 if exclude:
  x0,y0,x1,y1=exclude;alpha[y0:y1,x0:x1]=0
 d,stats=trace_alpha(alpha);ledger.append(dict(semanticText=semantic,sourceFrame=n,sourceTime=n/30,regions=rois,excluded=exclude,sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),editability='Native editable glyph outlines, semantic copy retained; not live text.',**stats))
 return dict(id='end-source-outlines-'+str(n),type='path',d=d,fill=fill,semanticText=semantic,sourceFrame=n,editability='Native glyph outlines, not live text.')
intro=next(l for l in scene['layers'] if l.get('type')=='group' and l.get('start')==0 and l.get('end')==2.24)
new={**intro,'children':[c for c in intro['children'] if c['type']=='image']+[outline(30,[(340,420,1580,535),(240,550,340,670),(490,550,940,670),(1085,550,1690,670)],'Introducing Agent to Agent / in iMessage Group Chats')]};patches[intro['id']]=new
first=next(l for l in scene['layers'] if l.get('type')=='text' and l.get('start')==34.2);g=outline(1050,[(150,470,1800,620)],'Your iMessage agent now has');g.update(id=first['id']+'-outlined',start=first['start'],end=first['end']);patches[first['id']]=g
full=next(l for l in scene['layers'] if l.get('type')=='group' and l.get('start')==35.3);new={**full,'children':[c for c in full['children'] if c['type']=='image']+[outline(1080,[(180,470,1860,620)],'Your iMessage agent now has a phone book.',exclude=(1310,480,1418,600))]};patches[full['id']]=new
for start,end,n,name in [(37.65,38.1,1134,'Amazon'),(38.1,38.65,1155,'Uber'),(38.65,39.2,1170,'eBay'),(39.2,39.6,1182,'Muse'),(39.6,40.05,1194,'Grok Bot'),(40.05,40.5,1206,'DoorDash')]:
 old=next(l for l in scene['layers'] if l.get('type')=='group' and l.get('start')==start and l.get('end')==end);p,a=image(n);roi=a[470:620,450:1150];mask=roi.min(2)<249;labels,count=ndimage.label(mask,np.ones((3,3)));boxes=[]
 for s in ndimage.find_objects(labels):
  if s is None:continue
  y,x=s;w=x.stop-x.start;h=y.stop-y.start
  if w>150 and h>55:boxes.append((x.start+450,y.start+470,x.stop+450,y.stop+470))
 if not boxes:raise RuntimeError('No source capsule border for '+name)
 box=min(boxes,key=lambda b:abs((b[0]+b[2])/2-760));box=(box[0]-2,box[1]-2,box[2]+2,box[3]+2);dest=R/'assets'/f'provider-{name.replace(" ","-").lower()}.png';Image.fromarray(a).crop(box).save(dest)
 art=dict(id=f'provider-source-art-{n}',type='image',src='assets/'+dest.name,x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1],semanticText=name,sourceFrame=n,sourceBounds=list(box),editability='Individual original provider capsule artwork; bitmap copy/logo.')
 black=outline(n,[(180,470,1810,620)],f'It brings {name} into your group chats.',exclude=box);patches[old['id']]={**old,'children':[black,art]};ledger.append(dict(kind='provider capsule artwork',semanticText=name,sourceFrame=n,sourceBounds=list(box),asset=art['src']))
last=next(l for l in scene['layers'] if l.get('type')=='text' and l.get('start')==40.5);g=outline(1224,[(150,470,1800,620)],'It brings all the agents into your group chats.');g.update(id=last['id']+'-outlined',start=last['start'],end=last['end']);patches[last['id']]=g
url=next(l for l in scene['layers'] if l.get('type')=='text' and l.get('start')==41.2);p,a=image(1290);rgb=a[470:620,450:1450];sel=(rgb[:,:,0]<220)&(rgb[:,:,2]-rgb[:,:,0]>20);colors,counts=np.unique(rgb[sel],axis=0,return_counts=True);color=colors[counts.argmax()];alpha=np.zeros(a.shape[:2],dtype=float);alpha[470:620,450:1450]=np.clip((253-rgb[:,:,0].astype(float))/(253-int(color[0])),0,1);d,stats=trace_alpha(alpha);g=dict(id=url['id']+'-outlined',type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in color),start=url['start'],end=url['end'],semanticText='photon.codes/beta',sourceFrame=1290,editability='Native glyph outlines, not live text.');patches[url['id']]=g;ledger.append(dict(semanticText='photon.codes/beta',sourceFrame=1290,fill=g['fill'],**stats))
(R/'endcard-refinement.json').write_text(json.dumps(dict(replacements=patches,provenance=ledger,changed_intervals=[[0,2.24],[34.2,1360/30]]),indent=2));print('Prepared source02 end-card replacements',len(patches))
