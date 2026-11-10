"""Native copy/material/composer prototype; preserves accepted menu and food actors."""
from pathlib import Path
import sys,copy,json
import numpy as np
from PIL import Image
from measure_lunch_refinement_v16 import P,SCENE,find,source
from apply_menu_thumbnail_clips_v15 import affine_group
sys.path.insert(0,str(P.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=copy.deepcopy(SCENE)
copy_spec=json.loads((P/'card-copy-v16-outline.json').read_text())
# Store one canonical source-derived native paragraph outline, not a frame raster.
paragraph_outline=copy_spec['outline']
for rid,prefix,start,end in [('p03-204','',541,618),('measured-lunch-ui-v13','lunch13-',735,800)]:
 root=next(n for n in s['layers'] if n['id']==rid)
 para,_=find(root,prefix+'p03-133',605 if not prefix else 750)
 text,_=find(root,prefix+'p03-132',605 if not prefix else 750)
 text.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1,ease='hold'),dict(t=start/30,value=0,ease='hold'),dict(t=end/30,value=1,ease='hold')]
 outlined=copy.deepcopy(paragraph_outline)
 def reid(n):
  n['id']=prefix+n['id']
  for c in n.get('children',[]):reid(c)
 reid(outlined);outlined.update(start=start/30,end=end/30)
 para['children'].append(outlined)
# Press union from only the measured605–614 state.
root=next(n for n in s['layers'] if n['id']=='p03-204')
inner,_=find(root,'measured-preview-inner-affine-v14',605)
body,_=find(root,'p03-135',605);tail,_=find(root,'p03-134',605)
press=[q for q in json.loads((P/'card-press-v16-measurements.json').read_text())['frames'] if 605<=q['frame']<=614]
black=[]
for item in [tail,body]:
 original=item['fill'];item.setdefault('keyframes',{})['fill']=[dict(t=0,value=original,ease='hold'),dict(t=605/30,value='#e8e8e8',ease='hold'),dict(t=615/30,value=original,ease='hold')]
 q={k:copy.deepcopy(v) for k,v in item.items() if k not in ['id','keyframes']};q.update(id='card-press-v16-'+item['id'],fill='#000000');black.append(q)
inner['children'].append(dict(id='card-press-material-v16',type='group',start=605/30,end=615/30,children=black,keyframes=dict(opacity=[dict(t=q['frame']/30,value=q['press_alpha'],ease='hold') for q in press]),semanticText='Pressed Uber Eats rich card',provenance=dict(kind='Native pressed-card union material',measured_frames=[605,614],notice='Source page stays253; only the card receives the independently measured press. Three empty information-panel probes and gray footer measured it.')))
# Composer template has one native geometry and two bounded source glyph outlines.
row=next(r for r in json.loads((P/'return-camera-v16-measurements.json').read_text())['frames'] if r['frame']==750)
inv=np.linalg.inv(np.array(row['ui_matrix']))
im=source(750).astype(float)
composer_children=[dict(id='lunch-composer-plus-material-v16',type='circle',x=83,y=1513,width=74,height=74,fill='url(#lunch-composer-native-material-v16)',blur=1.6),dict(id='lunch-composer-input-material-v16',type='rect',x=180,y=1513,width=540,height=74,radius=37,fill='url(#lunch-composer-native-material-v16)',blur=1.6)]
for name,box,bg,fg,color,blur,semantic in [('plus',[782,947,807,972],244,0,'#000000',0,'Add attachment'),('placeholder',[846,948,936,973],244,200,'#c8c8c8',.6,'iMessage')]:
 x,y,x2,y2=box;gray=im[y:y2,x:x2].mean(2);alpha=np.clip((bg-gray)/(bg-fg),0,1);alpha[alpha<.18]=0
 path,stats=trace_alpha(alpha,x,y)
 leaf=dict(id='lunch-composer-'+name+'-outline-v16',type='path',d=path,fill=color,semanticText=semantic,provenance=dict(kind='Native bounded source glyph outlines',source_frame=750,source_crop=box,background_gray=bg,foreground_gray=fg,contours=stats,notice='Single static UI control/placeholder ink only; geometry remains native and independently positioned.'))
 if blur:leaf['blur']=blur
 composer_children.append(affine_group(inv[:2],'lunch-composer-'+name+'-local-v16',[leaf]))
composer_children.extend([dict(id='lunch-composer-microphone-body-v16',type='rect',x=672,y=1530,width=12,height=24,radius=6,fill='none',stroke='#cccccc',strokeWidth=3.2),dict(id='lunch-composer-microphone-stand-v16',type='path',d='M666 1543 L666 1547 C666 1563 690 1563 690 1547 L690 1543 M678 1559 L678 1567 M670 1567 L686 1567',fill='none',stroke='#cccccc',strokeWidth=3.2,semanticText='Microphone',provenance=dict(kind='Native microphone geometry',notice='Measured capsule/side arcs from source750; lower stand is native continuation hidden by an independently animated Order chip in that source pose. Replaces incorrect music-note character.'))])
s.setdefault('gradients',[]).append(dict(id='lunch-composer-native-material-v16',type='linear',x1='0%',y1='0%',x2='0%',y2='100%',stops=[dict(offset='0%',color='#ededed'),dict(offset='30%',color='#f4f4f4'),dict(offset='70%',color='#f5f5f5'),dict(offset='100%',color='#fdfdfd')]))
for rid,prefix,start,end in [('p03-204','',596,618),('measured-lunch-ui-v13','lunch13-',735,800)]:
 root=next(n for n in s['layers'] if n['id']==rid);old,_=find(root,prefix+'p03-112',605 if not prefix else 750)
 old['opacity']=0
 children=copy.deepcopy(composer_children)
 def reid(n):
  n['id']=prefix+n['id']
  for c in n.get('children',[]):reid(c)
 for child in children:reid(child)
 new=dict(id=prefix+'lunch-composer-measured-v16',type='group',start=start/30,end=end/30,children=children,semanticText='Message composer',provenance=dict(kind='Native composer material/control geometry',measured_source_frame=750,notice='Input left180/top1513,width540; pluscentre119. Source placeholder is left-aligned. Separate background material and glyphs avoid the old blanket8px blur. Main composer appears596–617 before menu; return composer735–799 shares the independent Messages UI camera.'))
 root['children'].insert(root['children'].index(old)+1,new)
s['lunch_material_copy_v16']=dict(scopes=[[541,617],[735,799]],notice='Native paragraph glyph outlines, actual605–614card press and composer lifecycle. Accepted621–729 menu/V5 stencil and all original world food/Order actors remain unchanged.')
(P/'lunch-material-copy-v16-prototype.scene.json').write_text(json.dumps(s,indent=2))
# Durable ID-based changes consumed by the separate immutable application helper.
(P/'lunch-material-copy-v16-elements.json').write_text(json.dumps(dict(paragraph_outline=paragraph_outline,press=press,composer_children=composer_children,gradient=s['gradients'][-1]),indent=2))
print('Built native paragraph/press/composer prototype')
