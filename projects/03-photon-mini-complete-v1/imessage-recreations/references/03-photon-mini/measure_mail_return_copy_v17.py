"""Measure the final Mail copy after the special310–334camera, keeping all cameras intact."""
from pathlib import Path
import sys,json,copy
import numpy as np
from PIL import Image
from measure_lunch_refinement_v16 import find
from apply_menu_thumbnail_clips_v15 import affine_group
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
scene=json.loads((P/'final-v16.scene.json').read_text())
phone=next(n for n in scene['layers']if n['id']=='p03-86')

def source(frame):
 return np.array(Image.open(P/f'mail-edit-v17-source/{frame:04}.png').convert('RGB'))

def ink_box(rgb,box,first_run=False):
 x,y,x2,y2=box
 black=rgb[y:y2,x:x2].max(2)<80
 if first_run:
  counts=black.sum(1)
  first=int(np.where(counts>2)[0][0])
  last=first
  while last+1<len(counts)and counts[last+1]>0:
   last+=1
  black[:first]=False
  black[last+1:]=False
 yy,xx=np.where(black)
 return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)]

observations=[]
for frame in range(335,345):
 rgb=source(frame)
 title=ink_box(rgb,[680,180,1130,270])
 first=ink_box(rgb,[690,540,1225,610],True)
 observations.append(dict(frame=frame,title_ink_box=title,first_line_ink_box=first))
reference=observations[-1]
def corners(box):
 x,y,x2,y2=box
 return np.array([[x,y],[x2,y],[x2,y2],[x,y2]],float)
ref=np.concatenate([corners(reference['title_ink_box']),corners(reference['first_line_ink_box'])])
for row in observations:
 target=np.concatenate([corners(row['title_ink_box']),corners(row['first_line_ink_box'])])
 X=np.column_stack([ref,np.ones(len(ref))])
 M=np.linalg.lstsq(X,target,rcond=None)[0].T
 row['copy_world_matrix']=M.tolist()
 row['anchor_RMS']=float(np.sqrt(np.mean(np.sum((X@M.T-target)**2,axis=1))))
 _,parent=find(phone,'p03-77',row['frame'])
 row['copy_in_existing_pane_matrix']=(np.linalg.inv(parent)@np.vstack([M,[0,0,1]])).tolist()

reference_image=source(344)
regions=[
 ('title',[695,205,1085,256],'Dinner This Week','black'),
 ('to',[699,303,733,329],'To:','gray'),
 ('alice',[734,302,795,330],'Alice','blue'),
 ('from',[699,368,1050,398],'Cc/Bcc, From: ryan@photon.codes','gray'),
 ('subject-label',[699,432,785,461],'Subject:','gray'),
 ('subject',[786,432,971,461],'Dinner This Week','black'),
 ('greeting',[699,514,793,545],'Hi Alice,','black'),
 ('body',[699,565,1208,642],"Just wanted to check if we're still on for dinner this\nweek. I'm free Saturday or Sunday evening. Let me\nknow what works best for you.",'black'),
 ('looking',[699,662,1020,694],'Looking forward to catching up.','black'),
 ('best',[699,710,763,743],'Best,','black'),
 ('signature',[699,758,763,790],'Ryan','black'),
]
children=[]
for name,box,semantic,kind in regions:
 x,y,x2,y2=box
 rgb=reference_image[y:y2,x:x2].astype(float)
 gray=rgb.mean(2)
 background=252.
 if kind=='blue':
  red=rgb[:,:,0]
  core=rgb[red<np.percentile(red,8)]
  foreground=np.median(core,axis=0)
  direction=foreground-background
  alpha=np.clip(np.sum((rgb-background)*direction,axis=2)/np.sum(direction*direction),0,1)
 else:
  if kind=='black':
   cutoff=120
  else:
   cutoff=210
  pixels=gray[gray<cutoff]
  foreground=np.array([np.percentile(pixels,8)]*3)
  alpha=np.clip((background-gray)/(background-float(foreground[0])),0,1)
 alpha[alpha<.03]=0
 d,stats=trace_alpha(alpha,x,y)
 color='#'+''.join(f'{int(round(v)):02x}'for v in foreground)
 children.append(dict(id='mail-return-copy-'+name+'-v17',type='path',d=d,fill=color,semanticText=semantic,provenance=dict(kind='Native original semantic glyph outlines',source_frame=344,source_crop=box,foreground_rgb=foreground.tolist(),contours=stats,notice='Only this named copy role is outlined. Actualfinalperiod/no caret is preserved; native physical/UI/paper camera and bounded projected-pane exit345+remain unchanged.')))
for index,(y,x,x2)in enumerate([(348,701,1220),(413,701,1220),(478,701,1220)]):
 value=reference_image[y:y+1,x+10:x2-10].mean((0,1))
 color='#'+''.join(f'{int(round(v)):02x}'for v in value)
 children.append(dict(id=f'mail-return-separator-{index}-v17',type='rect',x=x,y=y,width=x2-x,height=1,fill=color,semanticText='Mail field separator',provenance=dict(kind='Native measured fieldseparator',source_frame=344,source_bounds=[x,y,x2,y+1])))
body=affine_group(np.array(observations[0]['copy_in_existing_pane_matrix'])[:2],'mail-return-copy-controller-v17',children)
body.update(start=335/30,end=345/30)
body['keyframes']={k:[]for k in ['x','y','scaleX','scaleY','rotation']}
body['children'][0]['keyframes']={'rotation':[]}
for row in observations:
 pose=affine_group(np.array(row['copy_in_existing_pane_matrix'])[:2],'unused',[])
 for key in body['keyframes']:
  body['keyframes'][key].append(dict(t=row['frame']/30,value=pose[key],ease='hold'))
 body['children'][0]['keyframes']['rotation'].append(dict(t=row['frame']/30,value=pose['children'][0]['rotation'],ease='hold'))
body['provenance']=dict(kind='Independent native Mail copy plane',source_frame=344,scope=[335,344],notice='Actualtitle andfirstline anchors measure this finalcopy plane independently of the unchanged physical/UI/paper camera. No rastercopy or completeframe. Only observedglyphroles/separators are replaced;310–334and345+are preserved.')
spec=dict(scope=[335,344],body=body,observations=observations,old_ids=['p03-60','p03-61','p03-62','p03-63','p03-64','p03-65','p03-66','p03-67','p03-68','p03-69','p03-70','p03-71','p03-72','p03-73','p03-74'])
(P/'mail-return-copy-v17-elements.json').write_text(json.dumps(spec,indent=2))
print([(r['frame'],r['title_ink_box'],r['first_line_ink_box'],round(r['anchor_RMS'],3))for r in observations])
