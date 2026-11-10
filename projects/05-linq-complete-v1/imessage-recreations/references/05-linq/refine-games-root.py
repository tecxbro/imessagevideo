"""Replace placeholder Games tiles with six independent authentic UI animations."""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
MEASURE=REF/'assets/root-games-measure';OUT=REF/'assets/root-late/games';OUT.mkdir(parents=True,exist_ok=True)
reference=np.array(Image.open(MEASURE/'frame-0136.png').convert('RGB'))
tiles=[('8 BALL',(137,127,352,354),(165,360,320,398)),('CHESS',(374,128,588,354),(405,360,565,398)),
 ('FOUR IN A ROW',(608,128,825,354),(608,360,830,398)),('WORD GAMES',(137,419,352,645),(132,650,357,693)),
 ('CRAZY 8',(374,419,590,645),(400,650,568,693)),('CUP PONG',(609,419,826,645),(635,650,825,693))]
def box_at(a,box,dy=0,broad=False):
 x0,y0,x1,y1=box;margin=95 if broad else 12;lo=max(0,round(y0+dy-margin));hi=min(720,round(y1+dy+margin));left=max(0,x0-8);right=min(960,x1+8)
 roi=a[lo:hi,left:right];mask=(roi.max(2)-roi.min(2)>35)&(roi.min(2)<200)
 if not broad:
  yy,xx=np.where(mask)
  if len(xx)<100:raise ValueError('No saturated tile pixels in '+str(box))
  return (left+int(xx.min()),lo+int(yy.min()),left+int(xx.max())+1,lo+int(yy.max())+1)
 labels,n=ndimage.label(mask,np.ones((3,3)));candidates=[]
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is None:continue
  y,x=sl;area=int((labels[sl]==i+1).sum())
  if x.stop-x.start>100 and y.stop-y.start>100:candidates.append((area,(left+x.start,lo+y.start,left+x.stop,lo+y.stop)))
 if not candidates:raise ValueError('No colored tile in '+str(box))
 return max(candidates)[1]
base_boxes=[box_at(reference,box) for _,box,_ in tiles]
layers=[];ledger=[];measurements=[]
for index,(name,base,labelbox) in enumerate(tiles):
 bx=base_boxes[index];prior=None
 for n in range(130,147):
  a=np.array(Image.open(MEASURE/f'frame-{n:04d}.png').convert('RGB'))
  common_dy=box_at(a,tiles[0][1],broad=True)[1]-base_boxes[0][1]
  b=box_at(a,base,dy=common_dy)
  # Native crop includes the rounded tile's original white corners and blur.
  # Its own boundaries and lifetime remain independently editable.
  x0,y0,x1,y1=b;pad=2;crop=(max(0,x0-pad),max(0,y0-pad),min(960,x1+pad),min(720,y1+pad))
  dest=OUT/f'tile-{index}-{n}.png';Image.fromarray(a).crop(crop).save(dest)
  layer=dict(id=f'root-games-tile-{index}-pose-{n}',type='image',src=str(dest),x=crop[0],y=crop[1],width=crop[2]-crop[0],height=crop[3]-crop[1],start=n/30,end=(n+1)/30,
   semanticText=name,sourceFrame=n,sourceBounds=list(crop),editability='Independent game-preview artwork; internal animated UI pixels are original bounded bitmap poses')
  layers.append(layer);prior=layer
  measurements.append(dict(frame=n,tile=name,bounds=b))
  if n==136:
   x0,y0,x1,y1=labelbox;roi=a[y0:y1,x0:x1].astype(float)
   pixels=roi[(roi.mean(2)<140)&(roi.max(2)-roi.min(2)<20)].astype(np.uint8)
   colors,counts=np.unique(pixels,axis=0,return_counts=True);ink=colors[counts.argmax()]
   alpha=np.clip((255-roi.mean(2))/(255-float(ink.mean())),0,1);d,stats=trace_alpha(alpha,x0,y0)
   outline=dict(id=f'root-games-label-{index}',type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in ink),semanticText=name,start=131/30,end=149/30,
    keyframes={'y':[],'opacity':[]},editability='Native source glyph outlines, not live text',sourceFrame=136)
   ledger.append(dict(kind='native label outline',semanticText=name,sourceFrame=136,bounds=labelbox,**stats))
 # Preserve the last uncontaminated preview underneath the entering chess card.
 prior=dict(prior);prior.update(id=f'root-games-tile-{index}-exit',start=147/30,end=149/30,keyframes={'opacity':[{'t':147/30,'value':.65},{'t':148/30,'value':.3}]});layers.append(prior)
 for n in range(131,149):
  anchor=next(m['bounds'] for m in measurements if m['tile']==name and m['frame']==min(n,146));dy=anchor[1]-bx[1]
  outline['keyframes']['y'].append({'t':n/30,'value':dy})
  outline['keyframes']['opacity'].append({'t':n/30,'value':1 if n<147 else (.65 if n==147 else .3)})
 layers.append(outline)
 # First blurred label is a short bounded source-glyph pose.
 x0,y0,x1,y1=labelbox;dy=next(m['bounds'][1]-bx[1] for m in measurements if m['tile']==name and m['frame']==130)
 a=Image.open(MEASURE/'frame-0130.png').convert('RGB');crop=(x0,max(0,y0+dy-8),x1,min(720,y1+dy+8));dest=OUT/f'label-{index}-blur-130.png';a.crop(crop).save(dest)
 layers.append(dict(id=f'root-games-label-{index}-blur',type='image',src=str(dest),x=crop[0],y=crop[1],width=crop[2]-crop[0],height=crop[3]-crop[1],start=130/30,end=131/30,semanticText=name,sourceFrame=130,sourceBounds=crop))
# Header and drawer handle remain separate editable pieces.
for name,box in [('Games',(450,48,595,93))]:
 x0,y0,x1,y1=box;alpha=np.clip((255-reference[y0:y1,x0:x1].mean(2))/255,0,1);d,stats=trace_alpha(alpha,x0,y0)
 layers.append(dict(id='root-games-header',type='path',d=d,fill='#000000',semanticText=name,start=131/30,end=149/30,
  keyframes={'y':[{'t':n/30,'value':next(m['bounds'][1]-base_boxes[0][1] for m in measurements if m['tile']=='8 BALL' and m['frame']==min(n,146))} for n in range(131,149)],
    'opacity':[{'t':146/30,'value':1},{'t':148/30,'value':.3}]},sourceFrame=136))
icon=OUT/'game-pigeon-header-icon.png';Image.fromarray(reference).crop((380,47,443,94)).save(icon)
layers.append(dict(id='root-games-header-icon',type='image',src=str(icon),x=380,y=47,width=63,height=47,start=131/30,end=149/30,
 keyframes={'y':[{'t':n/30,'value':47+next(m['bounds'][1]-base_boxes[0][1] for m in measurements if m['tile']=='8 BALL' and m['frame']==min(n,146))} for n in range(131,149)],'opacity':[{'t':146/30,'value':1},{'t':148/30,'value':.3}]}))
layers.append(dict(id='root-games-drawer-handle',type='rect',x=438,y=11,width=84,height=12,radius=6,fill='#bdbfbd',start=130/30,end=149/30,
 keyframes={'y':[{'t':n/30,'value':11+next(m['bounds'][1]-base_boxes[0][1] for m in measurements if m['tile']=='8 BALL' and m['frame']==min(n,146))} for n in range(130,149)],'opacity':[{'t':146/30,'value':1},{'t':148/30,'value':.3}]}))
patch=dict(replacements={'g-138':dict(id='g-138',type='group',children=layers,start=130/30,end=149/30)},changed_ranges=[[130,148]],
 provenance=dict(note='Six independent authentic animated tile interiors; native held labels and separate header/handle. No complete source frame or video layer.',measurements=measurements,labels=ledger))
(REF/'root-games-patch.json').write_text(json.dumps(patch,indent=2));print(json.dumps({'layers':len(layers),'nativeLabelOutlines':7,'sourceFrames':17,'tiles':6}))
