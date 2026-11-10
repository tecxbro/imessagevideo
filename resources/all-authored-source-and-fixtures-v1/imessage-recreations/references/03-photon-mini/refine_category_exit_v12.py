"""Keep the category camera independent from the exiting prefix camera.
The last two prefix frames expose fewer words; infer their visible semantic span.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy import ndimage
from PIL import Image
p=Path(__file__).parent;sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'final-v12.scene.json').read_text());proof=json.loads((p/'final-v12-changes.json').read_text())
def gray(a):
 roi=a[:,980:1280];l,n=ndimage.label(roi.max(2)<120);opts=[]
 for j,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start;density=float((l[b]==j).mean())
  if w>62 and h>25 and density<.4:opts.append((980+x.start,y.start,980+x.stop,y.stop))
 return max(opts,key=lambda q:(q[0]+q[2])/2) if opts else None

def opacity(a,mask,box,x,y,sx,sy):
 w=max(1,round(mask.shape[1]*sx));h=max(1,round(mask.shape[0]*sy));m=np.array(Image.fromarray((mask*255).astype('uint8')).resize((w,h),Image.Resampling.BICUBIC))/255
 xx=round(x+box[0]*sx);yy=round(y+box[1]*sy);x0=max(0,xx);x1=min(1920,xx+w);y0=max(0,yy);y1=min(1080,yy+h)
 if x1<=x0 or y1<=y0:return 0
 mm=m[y0-yy:y1-yy,x0-xx:x1-xx];core=mm>.8
 if core.sum()<4:return 0
 return float(np.clip(np.median((253-a[y0:y1,x0:x1].mean(2)[core])/253),0,1))
# The final mini-app row settles independently of the caption's exit zoom.
reference=np.array(Image.open(p/'category-native/26.png').convert('RGB'));refblack=gray(reference);core=(refblack[0]-14,refblack[1]-15,refblack[2]+14,refblack[3]+15);l,top,r,bottom=core
assetbox=(l-4,top-4,r+4,bottom+4);Image.fromarray(reference).crop(assetbox).save(p/'assets/category-8-original.png');icon=np.array(Image.fromarray(reference).crop(assetbox),dtype='float64')
box=(1270,495,1920,590);al=np.clip((253-reference[box[1]:box[3],box[0]:box[2]].mean(2))/253,0,1);cols=np.flatnonzero((al>.5).any(0));blocks=[]
for x in cols:
 if not blocks or x>blocks[-1][1]+13:blocks.append([int(x),int(x)])
 else:blocks[-1][1]=int(x)
children=[{'id':'category-icon-v12-8','type':'image','src':'assets/category-8-original.png','x':assetbox[0]-l,'y':assetbox[1]-top,'width':icon.shape[1],'height':icon.shape[0],'keyframes':{'opacity':[],'blur':[]}}];templates=[]
for j,(left,right) in enumerate(blocks):
 x0=left-2;x1=right+3;mask=al[:,x0:x1];local=(box[0]+x0-l,box[1]-top,box[0]+x1-l,box[3]-top);d,stats=trace_alpha(mask,local[0],local[1]);children.append({'id':f'category-word-v12-8-{j}','type':'path','d':d,'fill':'#000000','semanticText':['mini','apps'][j],'keyframes':{'opacity':[],'blur':[]}});templates.append((mask,local))
refmask=reference[450:700,1270:].max(2)<80;yy,xx=np.where(refmask);refink=(1270+int(xx.min()),450+int(yy.min()),1270+int(xx.max()+1),450+int(yy.max()+1))
g=next(x for x in s['layers'] if x['id']=='category-native-outline-v12-8');g['children']=children;g['keyframes']={k:[] for k in ['x','y','scaleX','scaleY']}
# Prefix word templates are reused only to fit observed opacity, not as video frames.
prefix=next(x for x in s['layers'] if x['id']=='measured-prefix-reveal-v6');source=np.array(Image.open(p/'measured/33.5.png').convert('RGB'));pboxes=[(274,500,429,582),(441,500,598,582),(612,500,813,582),(829,500,956,582),(973,500,1140,582)];pt=[]
for b in pboxes:
 mask=np.clip((253-source[b[1]:b[3],b[0]:b[2]].mean(2))/253,0,1);iy,ix=np.where(mask>.68);pt.append((mask,(b[0]-270,b[1]-493,b[2]-270,b[3]-493),(b[0]+int(ix.min()),b[1]+int(iy.min()),b[0]+int(ix.max()+1),b[1]+int(iy.max()+1))))
records=[]
for i,file in enumerate(sorted((p/'category-all-native').glob('*.png'))):
 t=(1000+i)/30;a=np.array(Image.open(file).convert('RGB'));tri=gray(a);active=t>=35.333333333333336 and tri is not None
 x=l;y=top;sx=sy=1
 if active:
  lower=tri[2]+15;m=a[450:700,lower:].max(2)<100;iy,ix=np.where(m)
  if len(ix):
   ink=(lower+int(ix.min()),450+int(iy.min()),lower+int(ix.max()+1),450+int(iy.max()+1));sx=(ink[2]-ink[0])/(refink[2]-refink[0]);sy=(ink[3]-ink[1])/(refink[3]-refink[1]);x=ink[0]-(refink[0]-l)*sx;y=ink[1]-(refink[1]-top)*sy
 for k,v in [('x',x),('y',y),('scaleX',sx),('scaleY',sy)]:g['keyframes'][k].append({'t':t,'value':v,'ease':'linear'})
 iconalpha=0
 if active:
  ww=max(1,round(icon.shape[1]*sx));hh=max(1,round(icon.shape[0]*sy));rr=np.array(Image.fromarray(icon.astype('uint8')).resize((ww,hh),Image.Resampling.BICUBIC),dtype='float64');xx=round(x+(assetbox[0]-l)*sx);yy=round(y+(assetbox[1]-top)*sy);x0=max(0,xx);x1=min(1920,xx+ww);y0=max(0,yy);y1=min(1080,yy+hh)
  if x1>x0 and y1>y0:
   d=253-rr[y0-yy:y1-yy,x0-xx:x1-xx];q=253-a[y0:y1,x0:x1].astype('float64');iconalpha=float(np.clip(np.sum(d*q)/np.sum(d*d),0,1))
 blur=2 if 35.4<=t<35.6 else (1 if 35.6<=t<35.8 else 0)
 g['children'][0]['keyframes']['opacity'].append({'t':t,'value':iconalpha,'ease':'linear'});g['children'][0]['keyframes']['blur'].append({'t':t,'value':blur,'ease':'linear'})
 for child,(mask,local) in zip(children[1:],templates):
  op=opacity(a,mask,local,x,y,sx,sy) if active else 0;child['keyframes']['opacity'].append({'t':t,'value':op,'ease':'linear'});child['keyframes']['blur'].append({'t':t,'value':3 if t>36.45 and child['semanticText']=='apps' else 0,'ease':'linear'})
 if t>=36.4:
  boundary=tri[0]-10 if tri else 1155;m=a[450:640,:boundary].max(2)<80;iy,ix=np.where(m);count=1 if t>36.45 else (2 if t>36.416 else 3);visible=pt[-count:];left=min(q[2][0] for q in visible);right=max(q[2][2] for q in visible);tt=min(q[2][1] for q in visible);bb=max(q[2][3] for q in visible)
  if len(ix):
   px=(int(ix.max())+1-int(ix.min()))/(right-left);py=(int(iy.max())+1-int(iy.min()))/(bb-tt);gx=int(ix.min())-(left-270)*px;gy=450+int(iy.min())-(tt-493)*py
   for key,value in [('x',gx),('y',gy),('scaleX',px),('scaleY',py)]:
    track=prefix['keyframes'][key];next(q for q in track if abs(q['t']-t)<1e-8)['value']=value
   for child,(mask,local,_) in zip(prefix['children'],pt):next(q for q in child['keyframes']['opacity'] if abs(q['t']-t)<1e-8)['value']=opacity(a,mask,local,gx,gy,px,py)
 records.append({'t':t,'active':active,'x':x,'y':y,'sx':sx,'sy':sy,'icon_alpha':iconalpha})
proof['asset_and_outline_provenance'][-1].update(reference_file='category-native/26.png',source_time=36,icon_box=list(assetbox),word_source_box=list(box));proof['miniapp_independent_camera']=records;proof['exit_diagnosis']='Prefix andcategory have independent exit projections; settled miniappasset replaces blurredarrivalasset. Lasttwo prefixframes contain2 then1 words and are measured from those semanticspans.'
f=p/'final-v12.scene.json';f.write_text(json.dumps(s,indent=2));proof['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();(p/'final-v12-changes.json').write_text(json.dumps(proof,indent=2));print(proof['sha256'])
# The last source frame contains chromatic motion blur. Its colored fringes
# confuse the hue classifier and its glyphs are no longer suitable camera ink.
# Use the prior native pose plus the observed leftward exit, with independent
# editable blur/fringe paths; do not substitute a source frame or row bitmap.
s=json.loads(f.read_text());last=1094/30;previous=1093/30
for layer in s['layers']:
 if layer['id'].startswith('category-native-outline-v12-') and layer['id']!='category-native-outline-v12-8':
  for child in layer['children']:
   for key in child.get('keyframes',{}).get('opacity',[]):
    if abs(key['t']-last)<1e-8:key['value']=0
mini=next(x for x in s['layers'] if x['id']=='category-native-outline-v12-8')
for key,offset in [('x',-49),('y',0),('scaleX',0),('scaleY',0)]:
 track=mini['keyframes'][key];old=next(q['value'] for q in track if abs(q['t']-previous)<1e-8);next(q for q in track if abs(q['t']-last)<1e-8)['value']=old+offset
for child in list(mini['children']):
 for q in child['keyframes']['opacity']:
  if abs(q['t']-last)<1e-8:q['value']=1
 for q in child['keyframes']['blur']:
  if abs(q['t']-last)<1e-8:q['value']=9 if child.get('semanticText')=='apps' else 1.5
 if child['type']=='path':
  for offset,color in [(-3,'#ff5757'),(3,'#54cfd4')]:
   fringe=json.loads(json.dumps(child));fringe['id']+=('-red' if offset<0 else '-cyan');fringe['x']=offset;fringe['fill']=color;fringe['start']=last;fringe['end']=36.5;fringe['opacity']=.2;fringe['keyframes']['opacity']=[{'t':last,'value':.2}];mini['children'].append(fringe)
# Avoid iterating newly appended fringe copies in subsequent authoring passes.
f.write_text(json.dumps(s,indent=2));proof=json.loads((p/'final-v12-changes.json').read_text());proof['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();proof['final_frame_effect']='Frame1094 hue detector rejected chromatic blur; prior native pose exits49px left, with editable perword blur/redcyanfringes. Approximate1-frame motionblur, no source row/frame bitmap.';(p/'final-v12-changes.json').write_text(json.dumps(proof,indent=2));print(proof['sha256'])
