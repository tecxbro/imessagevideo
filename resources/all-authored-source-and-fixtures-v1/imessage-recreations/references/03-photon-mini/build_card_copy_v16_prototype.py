from pathlib import Path
import sys,json,copy
import numpy as np
from PIL import Image
from measure_lunch_refinement_v16 import P,SCENE,root,find,source
from apply_menu_thumbnail_clips_v15 import affine_group
sys.path.insert(0,str(P.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=copy.deepcopy(SCENE)
r=next(n for n in s['layers'] if n['id']=='p03-204')
text,M=find(r,'p03-132',605)
para,paragraph_matrix=find(r,'p03-133',605)
x,y,x2,y2=728,368,1245,491
im=source(605)[y:y2,x:x2].astype(float)
bg=float(np.median(im[:2]));alpha=np.clip((bg-im.mean(2))/bg,0,1);alpha[alpha<.025]=0
path,stats=trace_alpha(alpha,x,y)
node=dict(id='lunch-paragraph-source-outline-v16',type='path',d=path,fill='#000000',semanticText=text['text'],provenance=dict(kind='Native source glyph outlines',source_frame=605,source_crop=[x,y,x2,y2],background_rgb=bg,contours=stats,notice='Three paragraph lines only. Glyphs are native editable path geometry in the original independently animated bubble; no card, phone, or frame raster. Semantic text retained.'))
new=affine_group(np.linalg.inv(paragraph_matrix)[:2],'lunch-paragraph-outline-local-v16',[node])
para['children'].append(new)
text['opacity']=0
# Measured card press is a material effect over the existing native body+tail union.
inner,_=find(r,'measured-preview-inner-affine-v14',605)
body,_=find(r,'p03-135',605);tail,_=find(r,'p03-134',605)
rows=json.loads((P/'card-press-v16-measurements.json').read_text())['frames']
press=[q for q in rows if 605<=q['frame']<=614]
for item in [body,tail]:
 original=item['fill'];item.setdefault('keyframes',{})['fill']=[dict(t=0,value=original,ease='hold'),dict(t=605/30,value='#e8e8e8',ease='hold'),dict(t=615/30,value=original,ease='hold')]
black=[]
for item in [tail,body]:
 q={k:copy.deepcopy(v) for k,v in item.items() if k not in ['id','keyframes']};q.update(id='card-press-v16-'+item['id'],fill='#000000');black.append(q)
inner['children'].append(dict(id='card-press-material-v16',type='group',start=605/30,end=615/30,children=black,keyframes=dict(opacity=[dict(t=q['frame']/30,value=q['press_alpha'],ease='hold') for q in press]),semanticText='Pressed Uber Eats rich card',provenance=dict(kind='Native pressed-card black material over the body/tail union',measured_frames=[605,614],notice='Three independent empty-panel RGB probes measure opacity; the gray footer verifies card-only press. The page is not dimmed.')))
(P/'card-copy-v16-prototype.scene.json').write_text(json.dumps(s,indent=2))
(P/'card-copy-v16-outline.json').write_text(json.dumps(dict(outline=new,press_frames=press),indent=2))
print('Built glyph-outline + measured605–614press prototype',stats)
