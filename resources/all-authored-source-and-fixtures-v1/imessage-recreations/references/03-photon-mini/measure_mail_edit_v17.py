"""Observe native Mail text/control states; keep original physical/UI camera unchanged."""
from pathlib import Path
import json,copy,sys,math
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from measure_lunch_refinement_v16 import matrix,find
from apply_menu_thumbnail_clips_v15 import affine_group
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
scene=json.loads((P/'final-v16.scene.json').read_text())
phone=next(n for n in scene['layers'] if n['id']=='p03-86')
cv2.setNumThreads(1)

def image(frame):
 return np.array(Image.open(P/f'mail-edit-v17-source/{frame:04}.png').convert('RGB'))

def alpha_ink(rgb):
 gray=rgb.astype(float).mean(2)
 a=np.clip((253-gray)/253,0,1)
 a[a<.03]=0
 return a

def path_from_region(frame,box,identifier,text,exclude=None):
 x,y,x2,y2=box
 rgb=image(frame)[y:y2,x:x2]
 alpha=alpha_ink(rgb)
 if exclude:
  for left,top,right,bottom in exclude:
   alpha[max(0,top-y):min(y2-y,bottom-y),max(0,left-x):min(x2-x,right-x)]=0
 d,stats=trace_alpha(alpha,x,y)
 return dict(id=identifier,type='path',d=d,fill='#000000',semanticText=text,provenance=dict(kind='Native bounded source glyph outlines',source_frame=frame,source_crop=box,contours=stats,notice='Only semantic email copy ink. No page/hardware/frame raster. Original independently measured camera remains untouched.'))

rows=[]
reference_box=None
for frame in range(230,310):
 rgb=image(frame)
 roi=rgb[650:690,610:1320]
 mask=roi.max(2)<80
 ys,xs=np.where(mask)
 box=[int(xs.min()+610),int(ys.min()+650),int(xs.max()+611),int(ys.max()+651)]
 if frame==240:
  reference_box=box
 rows.append(dict(frame=frame,first_line_ink_box=box))
if reference_box is None:
 raise ValueError('Missing observed reference copy')
for row in rows:
 x,y,x2,y2=row['first_line_ink_box']
 rx,ry,rx2,ry2=reference_box
 scale=(x2-x)/(rx2-rx)
 fit=np.array([[scale,0,x-scale*rx],[0,scale,y-scale*ry],[0,0,1.]])
 _,parent=find(phone,'p03-77',row['frame'])
 row['copy_world_matrix']=fit.tolist()
 row['copy_in_existing_pane_matrix']=(np.linalg.inv(parent)@fit).tolist()
 row['notice']='Uniform copy scale from long first-line width avoids pumping from23/24px quantized capheight; actual first-line left/top independently anchor translation. Physical/UI/paper cameras are unchanged.'
by_frame={r['frame']:r for r in rows}
# Reference first/third lines are static native outlines. The changing second line is independent.
base=path_from_region(240,[600,650,1310,760],'mail-edit-static-first-third-v17',"Just wanted to check if we're still on for dinner this\nknow what works best for you.",exclude=[[610,686,1320,724]])
original_second=path_from_region(240,[600,686,1310,724],'mail-edit-original-secondline-v17',"week. I'm free Thursday or Friday evening. Let me")
original_second.update(start=230/30,end=268/30)

states=[
 (268,270,''),
 (270,271,'Satu'),
 (271,272,'Saturd'),
 (272,273,'Saturda'),
 (273,277,'Saturday'),
 (277,279,'Saturday '),
 (279,281,'Saturday o'),
 (281,283,'Saturday or'),
 (283,284,'Saturday or '),
 (284,285,'Saturday or S'),
 (285,287,'Saturday or Su'),
 (287,288,'Saturday or Sun'),
 (288,289,'Saturday or Sund'),
 (289,290,'Saturday or Sunda'),
 (290,291,'Saturday or Sunday'),
 (291,294,'Saturday or Sunday '),
 (294,295,'Saturday or Sunday e'),
 (295,296,'Saturday or Sunday ev'),
 (296,297,'Saturday or Sunday eve'),
 (297,298,'Saturday or Sunday even'),
 (298,299,'Saturday or Sunday eveni'),
 (299,300,'Saturday or Sunday evenin'),
 (300,302,'Saturday or Sunday evening'),
 (302,309,'Saturday or Sunday evening.'),
 (309,310,'Saturday or Sunday evening.'),
]
children=[base,original_second]
state_records=[]
for start,end,typed in states:
 ref=start
 data=by_frame[ref]
 world=np.array(data['copy_world_matrix'])
 # The observed first line supplies the copy camera; project the reference line2 window.
 corners=world@np.array([[610,1310,1310,610],[686,686,724,724],[1,1,1,1.]])
 box=[int(math.floor(corners[0].min())),int(math.floor(corners[1].min())),int(math.ceil(corners[0].max())),int(math.ceil(corners[1].max()))]
 x,y,x2,y2=box
 rgb=image(ref)[y:y2,x:x2]
 alpha=alpha_ink(rgb)
 # A caret is the unique tall, thin isolated component to the right of the fixed prefix.
 count,labels,stats,centres=cv2.connectedComponentsWithStats(np.uint8(alpha>.5))
 choices=[]
 for index,stat in enumerate(stats[1:],1):
  left,top,width,height,area=map(int,stat)
  if left+x>800 and width<=4 and height>=21:
   choices.append(dict(index=index,bounds=[left+x,top+y,left+x+width,top+y+height],height=height,width=width,area=area))
 caret=None
 if start<309:
  if len(choices)!=1:
   raise ValueError(('Missing/ambiguous observed caret',start,choices))
  choice=choices[0]
  component=alpha*(labels==choice['index'])
  caret_d,caret_stats=trace_alpha(component,x,y)
  caret=dict(id=f'mail-edit-caret-{start}-v17',type='path',d=caret_d,fill='#000000',semanticText='Insertion caret',provenance=dict(kind='Single native observed caret outline',source_frame=ref,source_bounds=choice['bounds'],notice='Separated from copy before tracing, so no baked duplicate caret is retained. The source-state duration controls its presence.'))
  alpha[labels==choice['index']]=0
 elif choices:
  raise ValueError(('Unexpected caret in source309',choices))
 d,stats=trace_alpha(alpha,x,y)
 line=dict(id=f'mail-edit-secondline-{start}-v17',type='path',d=d,fill='#000000',semanticText="week. I'm free "+typed+' Let me',provenance=dict(kind='Native original glyph outlines for one observed edit state',source_frame=ref,source_crop=box,typed_text=typed,notice='Source shows actual intermediate deletion/typing. Full original secondline/caret are gated; no whole-frame or page image.'))
 group_children=[line]
 if caret:
  group_children.append(caret)
 group=affine_group(np.linalg.inv(world)[:2],f'mail-edit-state-{start}-v17',group_children)
 group.update(start=start/30,end=end/30,semanticText="week. I'm free "+typed+' Let me')
 children.append(group)
 state_records.append(dict(start=start,end_exclusive=end,typed_text=typed,source_frame=ref,source_crop=box,caret=caret['provenance'] if caret else None))

selections=[]
for frame in range(242,268):
 rgb=image(frame)
 crop=rgb[630:780,790:1275]
 values=crop.astype(float)
 chroma=values[:,:,2]-values[:,:,0]
 blue=(chroma>10)&(values[:,:,1]-values[:,:,0]>4)
 counts=blue.sum(1)
 good_rows=np.where(counts>counts.max()*.65)[0]
 top=int(good_rows.min());bottom=int(good_rows.max()+1)
 lefts=[]
 rights=[]
 for yy in range(top+2,bottom-2):
  xx=np.where(blue[yy])[0]
  if len(xx)>5:
   lefts.append(xx.min());rights.append(xx.max()+1)
 left=int(np.median(lefts));right=int(np.median(rights))
 inner=values[top+2:bottom-2,left+2:right-2]
 valid=(inner[:,:,0]>175)&(inner[:,:,2]-inner[:,:,0]>10)
 color=np.rint(np.median(inner[valid],axis=0)).astype(int)
 highlight=dict(id=f'mail-edit-selection-fill-{frame}-v17',type='rect',x=790+left,y=630+top,width=right-left,height=bottom-top,fill='#'+''.join(f'{v:02x}'for v in color),semanticText='Selected original availability phrase',provenance=dict(kind='Native measured selection rectangle',source_frame=frame,notice='Black original glyphs are drawn above this measured lightblue material. Extent is observed perframe rather than guessed phrase-wide.'))
 # Saturated selection handles have much greater blue chroma than the flat highlight.
 core_chroma=float(np.median(chroma[top+2:bottom-2,left+2:right-2][valid]))
 peak=float(chroma.max())
 handle_alpha=np.clip((chroma-core_chroma)/(peak-core_chroma),0,1)
 handle_alpha[~blue]=0
 mask=(chroma>core_chroma+.8*(peak-core_chroma))&blue
 handle_color=np.rint(np.median(values[mask],axis=0)).astype(int)
 handle_d,handle_stats=trace_alpha(handle_alpha,790,630)
 handles=dict(id=f'mail-edit-selection-handles-{frame}-v17',type='path',d=handle_d,fill='#'+''.join(f'{v:02x}'for v in handle_color),semanticText='Text selection handles',provenance=dict(kind='Native bounded selection-control outlines',source_frame=frame,contours=handle_stats,notice='Source controls are kept independent from the black glyph copy and lightblue fill. No selection bitmap.'))
 inv=np.linalg.inv(np.array(by_frame[frame]['copy_world_matrix']))[:2]
 under=affine_group(inv,f'mail-edit-selection-under-{frame}-v17',[highlight]);under.update(start=frame/30,end=(frame+1)/30)
 over=affine_group(inv,f'mail-edit-selection-over-{frame}-v17',[handles]);over.update(start=frame/30,end=(frame+1)/30)
 selections.append(dict(frame=frame,highlight=highlight,handles=handles))
 children.insert(0,under)
 children.append(over)

first=np.array(rows[0]['copy_in_existing_pane_matrix'])
body=affine_group(first[:2],'mail-edit-copy-controller-v17',children)
body.update(start=230/30,end=310/30,semanticText='Editable Mail body selection, deletion and typing')
body['keyframes']={k:[]for k in ['x','y','scaleX','scaleY','rotation']}
body['children'][0]['keyframes']={'rotation':[]}
for row in rows:
 pose=affine_group(np.array(row['copy_in_existing_pane_matrix'])[:2],'unused',[])
 for key in body['keyframes']:
  body['keyframes'][key].append(dict(t=row['frame']/30,value=pose[key],ease='hold'))
 body['children'][0]['keyframes']['rotation'].append(dict(t=row['frame']/30,value=pose['children'][0]['rotation'],ease='hold'))
body['provenance']=dict(kind='Native source-observed copy state machine',scope=[230,309],notice='Original physical/UI/paper cameras are unchanged. First-line ink anchors correct only the bodycopy geometry. Static first/third lines and independently editable secondline states/selection controls/singlecaret share this measuredcopy camera. No source raster runtime layer.')
spec=dict(scope=[230,309],body=body,first_line_poses=rows,edit_states=state_records,selections=selections,notice='Native glyph/control outlines only. The original coarseA→Bswitch264 skipped selectionuntil267, deletion268/269 andpartialtyping270–308. OriginalBoutline also baked a source300caret inaddition to nativecaret. Both are gated only230–309. Currentphysical/UI/papercamera and310–334specialfade remain unchanged.')
(P/'mail-edit-v17-elements.json').write_text(json.dumps(spec,indent=2))
print('Measured',len(rows),'copyposes',len(state_records),'editstates',len(selections),'selections')
