"""Measure Rene's coupled caption, lockscreen, bubble and physical-phone stages."""
from pathlib import Path
import json,copy,sys,subprocess,numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent;BASE=ROOT/'outputs/06-gallery/final-v17'
sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
scene=json.loads((BASE/'scene.json').read_text());OUT=REF/'assets/root-lock';OUT.mkdir(exist_ok=True)
byid={l['id']:l for l in scene['layers']};phone=copy.deepcopy(byid['rene-final11-group-65']);caption_old=byid['rene-final11-group-69'];chat_old=byid['g-1197'];device=copy.deepcopy(byid['g-1237'])
for l in [phone,device]:
 def absolute(n):
  if n.get('src'):n['src']=str((BASE/n['src']).resolve())
  for c in n.get('children',[]):absolute(c)
 absolute(l)
art=np.array(Image.open(phone['children'][0]['src']).convert('RGB'));footer=art[820:1020,40:-40].astype(float)
def blue_mask(a):return (a[:,:,2].astype(int)-a[:,:,0]>35)&(a[:,:,2].astype(int)-a[:,:,1]>10)&(a[:,:,2]>65)
local_blue_bottom=int(np.where(blue_mask(art))[0].max())+1
def gray_boxes(a):
 m=(a.min(2)>212)&(a.max(2)<250)&(a.max(2)-a.min(2)<12);labels,_=ndimage.label(m);boxes=[]
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is None:continue
  y,x=sl;area=int((labels[sl]==i+1).sum());w,h=x.stop-x.start,y.stop-y.start
  if area>3000 and 350<w<1350 and 10<h<500 and y.start>200 and 600<(x.start+x.stop)/2<1200:boxes.append((x.start,y.start,x.stop,y.stop))
 return sorted(boxes,key=lambda b:b[1])[:3]
def blue_box(a):
 mask=(a[:,:,2].astype(int)-a[:,:,0]>60)&(a[:,:,2]>180)&(a[:,:,1]>70);mask[:650]=False;mask[:,:850]=False;mask[:,1300:]=False
 labels,_=ndimage.label(mask);boxes=[]
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is None:continue
  y,x=sl;area=int((labels[sl]==i+1).sum())
  if area>1200 and x.stop-x.start>80 and y.stop-y.start>25:boxes.append((area,(x.start,y.start,x.stop,y.stop)))
 return max(boxes)[1] if boxes else None
def gray_model(a,box,semantic):
 x0,y0,x1,y1=box;roi=a[y0:y1,x0:x1].astype(float);pixels=roi[(roi.mean(2)>212)&(roi.mean(2)<250)]
 colors,counts=np.unique(pixels.astype(np.uint8),axis=0,return_counts=True);bg=colors[counts.argmax()]
 ink_pixels=roi[(roi.mean(2)<150)&(roi.max(2)-roi.min(2)<15)];colors,counts=np.unique(ink_pixels.astype(np.uint8),axis=0,return_counts=True);ink=colors[counts.argmax()]
 alpha=np.clip((bg.mean()-roi.mean(2))/(bg.mean()-ink.mean()),0,1);yy,xx=np.where(alpha>.5);bounds=(int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1)
 d,stats=trace_alpha(alpha,-bounds[0],-bounds[1])
 return dict(d=d,bg=bg.tolist(),ink=ink.tolist(),inkBox=bounds,bodyBox=list(box),semanticText=semantic,stats=stats)
canon=[]
for n,index,text in [(480,0,"Heads up: Your landlord emailed about the renewal. Rent's going up 8%"),(488,1,'3 similar units in your building are listed lower. Want me to write a pushback?'),(550,2,"It's in your drafts. Friendly but firm. You've got this")]:
 a=np.array(Image.open(REF/f'assets/root-lock-measure/frame-{n:04d}.png').convert('RGB'));boxes=gray_boxes(a)
 if len(boxes)<=index:raise ValueError(f'Missing canonical gray bubble {index} at {n}: {boxes}')
 model=gray_model(a,boxes[index],text);model['sourceFrame']=n;canon.append(model)
captured=np.array(Image.open(REF/'assets/root-lock-measure/frame-0417.png').convert('RGB'))
caption_models=[]
for name,(x0,x1) in [('Watches your',(200,1100)),('inbox',(1280,1750))]:
 roi=captured[350:1000,x0:x1];mask=(roi.max(2)-roi.min(2)<12)&(roi.max(2)<90);yy,xx=np.where(mask);box=(x0+int(xx.min()),350+int(yy.min()),x0+int(xx.max())+1,350+int(yy.max())+1)
 bx,by,br,bb=box;alpha=np.clip((255-captured[by:bb,bx:br].mean(2))/255,0,1);d,stats=trace_alpha(alpha)
 caption_models.append(dict(name=name,d=d,box=box,stats=stats))
green=(captured[:,:,1].astype(int)-captured[:,:,0]>50)&(captured[:,:,1].astype(int)-captured[:,:,2]>30)&(captured[:,:,1]>150);green[:350]=False;yy,xx=np.where(green);icon_box=(int(xx.min())-2,int(yy.min())-2,int(xx.max())+3,int(yy.max())+3);icon_file=OUT/'messages-icon-canonical.png';Image.fromarray(captured).crop(icon_box).save(icon_file)
icon_size=(icon_box[2]-icon_box[0],icon_box[3]-icon_box[1]);icon_states=[];caption_states=[[],[]];lock_states=[];chat_layers=[];text_states=[[],[],[]];camera=[];source_records=[]
first,last=408,554;proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',f"select='between(n,{first},{last})'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
for n in range(first,last+1):
 raw=proc.stdout.read(1920*1080*3)
 if len(raw)!=1920*1080*3:raise ValueError('Incomplete native stage decode')
 a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);t=n/30;lock_y=-1020.
 if n<461:
  m=blue_mask(a);m[:,:391]=False;m[:,1531:]=False;ys=np.where(m)[0]
  if len(ys)>30:
   guess=int(ys.max())+1-local_blue_bottom
   def error(y):
    lo=max(0,y+820);hi=min(1080,y+1020)
    if hi-lo<4:return 1e10
    return float(((art[lo-y:hi-y,40:-40].astype(float)-a[lo:hi,431:1491].astype(float))**2).mean())
   lock_y=float(min(range(guess-5,guess+6),key=error))
  lock_states.append(dict(frame=n,y=lock_y));bottom=lock_y+1020
  lower=max(300,round(bottom+70))
  if lower<1080:
   for index,model in enumerate(caption_models):
    x0,x1=(200,1100) if index==0 else (1280,1750);roi=a[lower:1080,x0:x1];mask=(roi.max(2)-roi.min(2)<12)&(roi.max(2)<90);yy,xx=np.where(mask)
    if len(xx)>20:
     box=(x0+int(xx.min()),lower+int(yy.min()),x0+int(xx.max())+1,lower+int(yy.max())+1);w=model['box'][2]-model['box'][0];h=model['box'][3]-model['box'][1];scale=(box[2]-box[0])/w
     if box[3]-box[1]<h*.75:scale=1.
     caption_states[index].append(dict(frame=n,x=box[0],y=box[1],scale=scale))
   green=(a[:,:,1].astype(int)-a[:,:,0]>50)&(a[:,:,1].astype(int)-a[:,:,2]>30)&(a[:,:,1]>150);green[:lower]=False;green[:,:950]=False;green[:,1400:]=False;yy,xx=np.where(green)
   if len(xx)>50:
    width=int(xx.max()-xx.min()+5);icon_states.append(dict(frame=n,x=int(xx.min())-2,y=int(yy.min())-2,width=width,height=width*icon_size[1]/icon_size[0]))
 if n<461:continue
 boxes=gray_boxes(a)
 if boxes:
  x0,y0,x1,y1=boxes[0];sx=(x1-x0)/480;sy=(y1-y0)/137
  camera.append(dict(frame=n,x=x0-43*sx,y=y0-334*sy,scaleX=sx,scaleY=sy))
 for index,box in enumerate(boxes):
  model=canon[index];x0,y0,x1,y1=box;roi=a[y0:y1,x0:x1].astype(float);pixels=roi[(roi.mean(2)>212)&(roi.mean(2)<250)];colors,counts=np.unique(pixels.astype(np.uint8),axis=0,return_counts=True);bg=colors[counts.argmax()]
  body_alpha=np.clip((255-roi.mean(2))/(255-bg.mean()),0,1);d,stats=trace_alpha(body_alpha)
  chat_layers.append(dict(id=f'root-rene-gray-{index}-body-{n}',type='path',d=d,x=x0,y=y0,fill='#'+''.join(f'{v:02x}' for v in bg),start=t,end=(n+1)/30,semanticText=model['semanticText'],sourceFrame=n,editability='Native measured bubble outline'))
  dark=roi[(roi.mean(2)<150)&(roi.max(2)-roi.min(2)<15)]
  colors,counts=np.unique(dark.astype(np.uint8),axis=0,return_counts=True);actual_ink=colors[counts.argmax()] if len(colors) else np.array(model['ink'])
  alpha=np.clip((bg.mean()-roi.mean(2))/(bg.mean()-actual_ink.mean()),0,1);yy,xx=np.where(alpha>.5)
  if not len(xx):continue
  actual_path,actual_stats=trace_alpha(alpha)
  chat_layers.append(dict(id=f'root-rene-gray-{index}-glyph-pose-{n}',type='path',d=actual_path,x=x0,y=y0,fill='#'+''.join(f'{v:02x}' for v in actual_ink),start=t,end=(n+1)/30,semanticText=model['semanticText'],sourceFrame=n,editability='Native measured semantic glyph-outline pose; not live text'))
  ink_box=(int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1);cx0,cy0,cx1,cy1=model['inkBox'];bw=model['bodyBox'][2]-model['bodyBox'][0];scale=(x1-x0)/bw
  if y1>=1079 and (ink_box[3]-ink_box[1])<(cy1-cy0)*scale*.85:
   pose=dict(frame=n,x=x0+cx0*scale,y=y0+cy0*scale,scaleX=scale,scaleY=scale)
  else:pose=dict(frame=n,x=x0+ink_box[0],y=y0+ink_box[1],scaleX=(ink_box[2]-ink_box[0])/(cx1-cx0),scaleY=(ink_box[3]-ink_box[1])/(cy1-cy0))
  text_states[index].append(pose)
 source_records.append(dict(frame=n,grayBoxes=boxes,blueBox=blue_box(a)))
proc.stdout.close();proc.wait()
def keys(states,property):return [{'t':s['frame']/30,'value':s[property]} for s in states]
phone['start']=408/30;phone['end']=461/30;phone['keyframes']={'y':keys(lock_states,'y')}
caption=[]
for index,model in enumerate(caption_models):
 states=caption_states[index];caption.append(dict(id=f'root-rene-watch-word-{index}',type='path',d=model['d'],fill='#000000',start=states[0]['frame']/30,end=(states[-1]['frame']+1)/30,semanticText=model['name'],sourceFrame=417,keyframes={p:keys(states,'scale' if p.startswith('scale') else p) for p in ['x','y','scaleX','scaleY']}))
caption.append(dict(id='root-rene-watch-icon',type='image',src=str(icon_file),start=icon_states[0]['frame']/30,end=(icon_states[-1]['frame']+1)/30,keyframes={p:keys(icon_states,p) for p in ['x','y','width','height']},semanticText='Messages app icon',sourceFrame=417,width=icon_size[0],height=icon_size[1]))
caption_group=dict(id=caption_old['id'],type='group',start=408/30,end=461/30,children=caption)
chat=dict(id=chat_old['id'],type='group',start=461/30,end=555/30,children=chat_layers)
# The incoming bubbles are independent native objects while the phone materializes.
# Preserve blue/draft controls until a following native checkpoint diagnoses them.
device['children']=[c for c in device['children'] if c['id'] not in ['g-1200','g-1204','g-1212']]
camera=[c for c in camera if c['frame']>=483];device['start']=483/30;device['keyframes']={p:keys(camera,p) for p in ['x','y','scaleX','scaleY']}
for c in device['children']:
 if c['id']=='g-1208':c['start']=499/30
patch=dict(replacements={phone['id']:phone,caption_group['id']:caption_group,chat['id']:chat,device['id']:device},changed_ranges=[[408,554]],
 provenance=dict(lockStates=lock_states,captionStates=caption_states,iconStates=icon_states,camera=camera,bubbles=source_records,canonicals=canon,notes='Independent native bubble bodies/glyphs, physical device and caption. Original bounded lockscreen product artwork retained; no full-frame/video layer.'))
(REF/'root-lock-patch.json').write_text(json.dumps(patch,indent=2));print(json.dumps({'lockFrames':len(lock_states),'captionFrames':list(map(len,caption_states)),'bubbles':len(chat_layers),'cameraFrames':len(camera)}))
