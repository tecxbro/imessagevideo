from pathlib import Path
import json,copy,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';P=R/'verification/fidelity-review/05-games-exit';A=REF/'assets/games-exit-review';A.mkdir(exist_ok=True);S=json.load(open(R/'outputs/05-linq/final-v10/scene.json'));old=next(l for l in S['layers']if l['id']=='g-138');sources={f:np.array(Image.open(REF/'assets/root-games-measure'/f'frame-{f:04d}.png').convert('RGB')).astype(float)/255 for f in [145,146,147,148]};native=np.array(Image.open(R/'outputs/05-linq/frames-gsap/000145.png').convert('RGB')).astype(float)/255
boxes=[(136,126,352,350),(372,126,588,350),(608,126,824,350),(136,416,352,640),(372,416,588,640),(608,416,824,640)];rois=[(185,358,310,394),(414,358,550,394),(610,358,827,394),(136,650,350,686),(409,650,557,686),(638,650,817,686)];artifact=[];actors=[];fits=[]
def sample(vs,t):
 if t<=vs[0]['t']:return vs[0]['value']
 for a,b in zip(vs,vs[1:]):
  if t<=b['t']:
   r=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*r
 return vs[-1]['value']
def freeze(c):
 c=copy.deepcopy(c);c['id']='games-exit-review-'+c['id'];c.pop('start',None);c.pop('end',None)
 for k,vs in c.pop('keyframes',{}).items():c[k]=sample(vs,145/30)
 if c.get('src'):c['src']=str((R/'outputs/05-linq/final-v10'/c['src']).resolve())
 return c
def opfit(f,box):
 x0,y0,x1,y1=box;D=1-native[y0-(4 if box==rois[3] else 0):y1-(4 if box==rois[3] else 0),x0:x1];T=1-sources[f][y0:y1,x0:x1];m=D.max(2)>.08;return float(np.clip((D[m]*T[m]).sum()/max(1e-6,(D[m]*D[m]).sum()),0,1))
for i,box in enumerate(boxes):
 x0,y0,x1,y1=box
 D=1-sources[147][y0:y1,x0:x1];T=1-sources[148][y0:y1,x0:x1]
 # Pool is unobscured by incoming chess, so provides genuine Games fade ratio.
 poolD=1-sources[147][126:350,136:350];poolT=1-sources[148][126:350,136:350];fade=float(np.clip((poolD*poolT).sum()/(poolD*poolD).sum(),0,1))
 for f in [146,147,148]:
  pixels=sources[f][y0:y1,x0:x1]if f<148 else 1-fade*D;path=A/f'tile-{i}-pose-{f}.png';Image.fromarray(np.uint8(np.clip(pixels,0,1)*255+.5)).save(path);actors.append(dict(id=f'games-exit-review-tile-{i}-{f}',type='image',src=str(path),x=x0,y=y0,width=x1-x0,height=y1-y0,start=f/30,end=(f+1)/30));artifact.append(dict(frame=f,component=f'game-tile-{i}',path=str(path),source_box=box,notice='146/147 original bounded animated tile UI pose;148 uses147 pose with measured source pool contrast fade, incoming chess remains independent.'))
# The six tiles keep animating at148. Capture only exposed tile material;
# the incoming widget rectangle is transparent so it is never composited twice.
for i,box in enumerate(boxes):
 x0,y0,x1,y1=box;pix=np.uint8(np.clip(sources[148][y0:y1,x0:x1],0,1)*255+.5);al=np.ones((y1-y0,x1-x0),dtype='uint8')*255;xx=np.arange(x0,x1)[None,:];yy=np.arange(y0,y1)[:,None];al[(xx>=351)&(xx<861)&(yy>=158)&(yy<551)]=0;path=A/f'tile-{i}-visible-material-148.png';Image.fromarray(np.dstack((pix,al))).save(path);actors.append(dict(id=f'games-exit-review-tile-{i}-visible148',type='image',src=str(path),x=x0,y=y0,width=x1-x0,height=y1-y0,start=148/30,end=149/30));artifact.append(dict(frame=148,component=f'game-tile-{i}-unobscured-material',path=str(path),source_box=box,notice='Original animated game artwork only outside the incoming chess-widget rectangle; no duplicate widget pixels.'))
for i,box in enumerate(rois):
 c=freeze(next(c for c in old['children']if c['id']==f'root-games-label-{i}'));vals=[(f,opfit(f,box))for f in [146,147,148]];c['y']=c.get('y',0)+(4 if i==3 else 0);c['keyframes']={'opacity':[dict(t=f/30,value=v,ease='linear')for f,v in vals]};actors.append(c);fits.append(dict(id=c['id'],opacities=vals))
for id,box in [('root-games-header',(452,46,578,95)),('root-games-header-icon',(380,47,443,94)),('root-games-drawer-handle',(438,11,522,23))]:
 c=freeze(next(c for c in old['children']if c['id']==id));vals=[(f,opfit(f,box))for f in [146,147,148]];c['keyframes']={'opacity':[dict(t=f/30,value=v,ease='linear')for f,v in vals]};actors.append(c);fits.append(dict(id=c['id'],opacities=vals))
# Source148 has the first chess-card overlap; accepted149+ actors untouched.
poster=freeze(next(l for l in S['layers']if l['id']=='broad-v5-group-2'));poster['id']='games-exit-review-chess148';poster['x']=351;poster['y']=158;poster['opacity']=.30;poster['start']=148/30;poster['end']=149/30;poster['children']=copy.deepcopy(next(l for l in S['layers']if l['id']=='broad-v5-group-2')['children'])
for ch in poster['children']:
 ch['id']='games-exit-review-'+ch['id'];ch['src']=str((R/'outputs/05-linq/final-v10'/ch['src']).resolve())
poster['opacity']=1;poster['children'][0]['src']=str(A/'chess-entry-color-pose-148.png');actors.append(poster);new=dict(id='games-exit-review-146-148',type='group',start=146/30,end=149/30,children=actors);spec=dict(changed_frame_ranges=[[146,148]],gate_id='g-138',gate_end=146/30,insert_after={'g-138':[new]},provenance=dict(tiles=artifact,native_opacity_fits=fits,poster='Bounded148 chess entry RGBA color pose unmixes actual source widget against computed Games backdrop; native camera/clip/lifetime begins148; original149+ parent untouched.'))
(REF/'games-exit-review-elements.json').write_text(json.dumps(spec,indent=2));print('fits',fits,'fade148',fade)
