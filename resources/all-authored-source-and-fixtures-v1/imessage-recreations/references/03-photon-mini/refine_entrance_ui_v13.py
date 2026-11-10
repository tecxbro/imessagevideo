"""Restore actual typing/message states and use high-resolution header outlines."""
from pathlib import Path
import copy,json,sys,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'entrance-v13.scene.json').read_text());ui=next(x for x in s['layers'] if x['id']=='measured-entrance-ui-v13');meta=json.loads((p/'entrance-v13-changes.json').read_text());rows=json.loads((p/'entrance-v13-measurements.json').read_text());rows=[r for r in rows if 436<=r['frame']<495];reference=Image.open(p/'measured/16.5.png').convert('RGB');ref=np.array(reference,dtype='float64');macro=Image.open(p/'peak-source-native/02.png').convert('RGB')

def coords(box):return ((box[0]-546)/1.035,(box[1]-35)/1.035,(box[2]-box[0])/1.035,(box[3]-box[1])/1.035)
def path_from(image,box,target,semantic,fill,gray):
 a=np.array(image.crop(box),dtype='float64');alpha=np.clip((253-a.mean(2))/(253-gray),0,1);yy,xx=np.where(alpha>.5);ink=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));d,stats=trace_alpha(alpha);x,y,w,h=coords(target);sx=w/(ink[2]-ink[0]);sy=h/(ink[3]-ink[1]);return {'type':'path','d':d,'x':x-ink[0]*sx,'y':y-ink[1]*sy,'scaleX':sx,'scaleY':sy,'fill':fill,'semanticText':semantic,'provenance':{'source_box':list(box),'target_native_reference_box':list(target),'native_outlines':True}}
for semantic,box,target,fill,gray in [
 ('Team Lunch',(646,750,1238,835),(859,321,1049,345),'#000000',0),
 ('›',(1255,748,1306,849),(1057,319,1070,351),'#8e8e8e',142),
 ('Today 11:20 AM',(731,971,1231,1047),(889,394,1044,413),'#8e8e8e',142)]:
 old=next(c for c in ui['children'] if c.get('semanticText')==semantic);new=path_from(macro,box,target,semantic,fill,gray);new['id']=old['id'];ui['children'][ui['children'].index(old)]=new
# The title pill materializes after the initially plain kinetic title.
pill=next(c for c in ui['children'] if c['id']=='entrance-p03-103');pill['x']=276;pill['y']=261;pill['width']=248;pill['keyframes']={'opacity':[{'t':14.633333333333333,'value':0},{'t':14.9,'value':1,'ease':'linear'}]}

# Source16.5 is a clean reference for caption glyphs and incoming Memoji assets.
actors={}
for name,caption_id,avatar_id,full_id,caption_box,avatar_box in [
 ('alice','entrance-p03-113','entrance-p03-114','entrance-p03-118',(724,429,791,462),(606,481,684,560)),
 ('bob','entrance-p03-119','entrance-p03-120','entrance-p03-124',(724,570,789,605),(606,627,684,706))]:
 old=next(c for c in ui['children'] if c['id']==caption_id);ca=np.array(reference.crop(caption_box),dtype='float64');cy0,cx0=np.where((253-ca.mean(2))/(253-153)>.5);target=(caption_box[0]+int(cx0.min()),caption_box[1]+int(cy0.min()),caption_box[0]+int(cx0.max()+1),caption_box[1]+int(cy0.max()+1));new=path_from(reference,caption_box,target,name.title(),'#999999',153);new['id']=caption_id;new['keyframes']={'opacity':[],'y':[]};ui['children'][ui['children'].index(old)]=new
 avatar=next(c for c in ui['children'] if c['id']==avatar_id);file=f'assets/incoming-{name}-original-v13.png';reference.crop(avatar_box).save(p/file);x,y,w,h=coords(avatar_box);avatar.update(src=file,x=x,y=y,width=w,height=h,keyframes={'y':[],'opacity':[]})
 full=next(c for c in ui['children'] if c['id']==full_id);full['keyframes']={k:[] for k in ['x','y','opacity']};rect=next(c for c in full['children'] if c['type']=='rect');rect['keyframes']={'width':[]}
 typing=copy.deepcopy(full);typing['id']='entrance-typing-'+name
 for c in typing['children']:c['id']='typing-'+c['id']
 typing['children']=[c for c in typing['children'] if c['type']!='text'];typing_rect=next(c for c in typing['children'] if c['type']=='rect');typing_rect['width']=160;typing_rect['keyframes']={'width':[]}
 for i,cx in enumerate([42,80,118]):typing['children'].append({'id':f'entrance-typing-dot-{name}-{i}','type':'circle','x':cx-11,'y':26,'width':22,'height':22,'fill':'#ababab','keyframes':{'opacity':[]}})
 typing['keyframes']={k:[] for k in ['x','y','opacity']};ui['children'].append(typing)
 actors[name]={'caption':new,'caption_base_y':new['y'],'caption_box':caption_box,'avatar':avatar,'avatar_box':avatar_box,'full':full,'rect':rect,'typing':typing,'typing_rect':typing_rect}

def sample(track,t):
 keys=sorted(track,key=lambda q:q['t'])
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:
   u=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*u
 return keys[-1]['value']

def fit_patch(a,template,x,y,w,h,search=False):
 ww=max(1,round(w));hh=max(1,round(h));rr=np.array(template.resize((ww,hh),Image.Resampling.BICUBIC),dtype='float64');d=253-rr;den=np.sum(d*d)
 if den<1:return 0,0
 best=(0,0,0)
 for dy in (np.arange(-12,13,1) if search=='caption' else np.arange(0,52,3) if search else [0]):
  xx=round(x);yy=round(y+dy);x0=max(0,xx);x1=min(1920,xx+ww);y0=max(0,yy);y1=min(1080,yy+hh)
  if x1<=x0 or y1>1080 or y1<=y0:continue
  dd=d[y0-yy:y1-yy,x0-xx:x1-xx];ss=253-a[y0:y1,x0:x1].astype('float64');den0=np.sum(dd*dd)
  if den0<1:continue
  dot=np.sum(dd*ss);quality=dot*dot/den0;alpha=float(np.clip(dot/den0,0,1))
  if quality>best[0]:best=(quality,alpha,float(dy))
 return best[1],best[2]

records=[]
for row in rows:
 t=row['t'];a=np.array(Image.open(p/'entrance-native'/f"{row['frame']-434:03}.png").convert('RGB'));ux=sample(ui['keyframes']['x'],t);uy=sample(ui['keyframes']['y'],t);sx=sample(ui['keyframes']['scaleX'],t);sy=sample(ui['keyframes']['scaleY'],t)
 rgb=a.astype('int16');gray=(rgb.max(2)-rgb.min(2)<4)&(rgb.mean(2)>231)&(rgb.mean(2)<242);gray=ndimage.binary_erosion(gray,iterations=1);l,n=ndimage.label(gray);found={}
 for j,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  yy,xx=b;w=(xx.stop-xx.start+2)/sx;h=(yy.stop-yy.start+2)/sy;lx=(xx.start-1-ux)/sx;ly=(yy.start-1-uy)/sy
  if not 130<lx<170 or not 80<w<650 or not 22<h<120:continue
  name='alice' if ly<510 else 'bob';state='full' if w>(400 if name=='alice' else 260) else 'typing'
  if name not in found or w>found[name]['width']:found[name]={'x':lx,'y':ly,'width':w,'state':state,'box':[xx.start-1,yy.start-1,xx.stop+1,yy.stop+1]}
 rec={'t':t,'frame':row['frame'],'states':{}}
 for name,data in actors.items():
  state=found.get(name);defaulty=420 if name=='alice' else 560;xx=state['x'] if state else 150;yy=state['y'] if state else defaulty;ww=state['width'] if state else 160
  for group,is_typing in [(data['full'],False),(data['typing'],True)]:
   active=state is not None and ((state['state']=='typing')==is_typing)
   for k,v in [('x',xx),('y',yy),('opacity',1 if active else 0)]:group['keyframes'][k].append({'t':t,'value':v,'ease':'linear'})
  data['rect']['keyframes']['width'].append({'t':t,'value':ww if state and state['state']=='full' else (568 if name=='alice' else 350),'ease':'linear'});data['typing_rect']['keyframes']['width'].append({'t':t,'value':ww if state and state['state']=='typing' else 160,'ease':'linear'})
  for index,dot in enumerate([c for c in data['typing']['children'] if c['type']=='circle']):
   px=round(ux+(xx+[42,80,118][index])*sx);py=round(uy+(yy+37)*sy);value=float(a[py-1:py+2,px-1:px+2].mean()) if 2<px<1918 and 2<py<1078 else 236;alpha=float(np.clip((236-value)/65,0,1));dot['keyframes']['opacity'].append({'t':t,'value':alpha,'ease':'linear'})
  avatar=data['avatar'];x=ux+avatar['x']*sx;y=uy+coords(data['avatar_box'])[1]*sy;refavatar=reference.crop(data['avatar_box']);op,dy=fit_patch(a,refavatar,x,y,avatar['width']*sx,avatar['height']*sy,True);avatar['keyframes']['y'].append({'t':t,'value':coords(data['avatar_box'])[1]+dy/sy,'ease':'linear'});avatar['keyframes']['opacity'].append({'t':t,'value':op,'ease':'linear'})
  cb=data['caption_box'];cx,cy,cw,ch=coords(cb);opcap,caption_dy=fit_patch(a,reference.crop(cb),ux+cx*sx,uy+cy*sy,cw*sx,ch*sy,'caption');opcap=opcap if opcap>.25 else 0;data['caption']['keyframes']['opacity'].append({'t':t,'value':opcap,'ease':'linear'});data['caption']['keyframes']['y'].append({'t':t,'value':data['caption_base_y']+caption_dy/sy,'ease':'linear'});rec['states'][name]={'bubble':state,'avatar_opacity':op,'avatar_dy':dy,'caption_opacity':opcap}
 records.append(rec)
s['source']['notes']+=' V13 UI refinement: high-resolution header glyphoutlines from15.233restpose, authentic incoming Memoji, actual perframe Alice/Bob typing/fullmessage states, animated typingdot opacity and avatarentrance fits.'
f=p/'entrance-v13.scene.json';f.write_text(json.dumps(s,indent=2));meta['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();meta['message_state_measurements']=records;meta['macro_header_source_time']=457/30;(p/'entrance-v13-changes.json').write_text(json.dumps(meta,indent=2));print(meta['sha256']);print([(r['frame'],{k:v['bubble']['state'] if v['bubble'] else None for k,v in r['states'].items()}) for r in records if r['frame'] in [439,457,472,480,486,490,494]])
