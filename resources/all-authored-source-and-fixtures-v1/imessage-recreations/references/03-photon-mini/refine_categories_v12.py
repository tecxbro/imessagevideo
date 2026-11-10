"""Measure independent category icon/word transforms from native frames.
Only isolated icon artwork is raster. Copy is semantic native vector outlines.
"""
from pathlib import Path
import json,copy,hashlib,sys,colorsys
import numpy as np
from scipy import ndimage
from PIL import Image
p=Path(__file__).parent
sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'final-v11.scene.json').read_text())
rows=[('agentic apps','category-native/01.png',353.5),('generative UIs','category-native/07.png',59),('games','category-native/11.png',201.5),('sign-in requests','category-native/14.png',127.6),('live screen sharing','category-fast-native/05.png',187.3),('live delivery tracking','category-native/16.png',38.2),('menus','category-native/17.png',15.9),('dashboards','category-native/19.png',272.4),('mini apps','category-native/21.png',None)]
old_ids=['p03-'+str(656+5*i) for i in range(9)]
s['layers']=[x for x in s['layers'] if x['id'] not in old_ids]
provenance=[];templates=[];groups=[]
def components(a):
 roi=a[:1080,1080:1280];m=(roi.max(2)-roi.min(2)>4)&(roi.min(2)<250);l,n=ndimage.label(m);choices=[]
 for j,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start
  if w>60 and h>35:
   rgb=roi[b][l[b]==j].mean(0);hue=colorsys.rgb_to_hsv(*(rgb/255))[0]*360;choices.append({'box':(1080+x.start,y.start,1080+x.stop,y.stop),'hue':hue})
 return choices

def gray_component(a):
 roi=a[:1080,1080:1280];l,n=ndimage.label(roi.max(2)<120);choices=[]
 for j,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start
  if w>62 and h>25:choices.append((1080+x.start,y.start,1080+x.stop,y.stop))
 return max(choices,key=lambda b:(b[0]+b[2])/2) if choices else None

def hue_delta(a,b):return abs((a-b+180)%360-180)
def inkbox(a,x0=0,x1=1155):
 m=a[450:640,x0:x1].max(2)<80;y,x=np.where(m)
 if not len(x):return None,0
 col=m.any(0);ix=np.flatnonzero(col);blocks=[]
 for xx in ix:
  if not blocks or xx>blocks[-1][1]+13:blocks.append([int(xx),int(xx)])
  else:blocks[-1][1]=int(xx)
 return [x0+int(x.min()),450+int(y.min()),x0+int(x.max()+1),450+int(y.max()+1)],min(5,len(blocks))

def alpha_at(a,mask,box,x,y,sx,sy):
 # Fit opacity against the interior of an independently transformed word.
 w=max(1,round(mask.shape[1]*sx));h=max(1,round(mask.shape[0]*sy));m=np.array(Image.fromarray((mask*255).astype('uint8')).resize((w,h),Image.Resampling.BICUBIC))/255
 left=round(x+box[0]*sx);top=round(y+box[1]*sy);x0=max(0,left);y0=max(0,top);x1=min(1920,left+w);y1=min(1080,top+h)
 if x1<=x0 or y1<=y0:return 0
 patch=a[y0:y1,x0:x1].mean(2);mm=m[y0-top:y1-top,x0-left:x1-left];core=mm>.8
 if core.sum()<5:return 0
 return float(np.clip(np.median((253-patch[core])/253),0,1))

# Original held outline word templates also supply measured prefix camera/exit.
origin=(270,493);base=np.array(Image.open(p/'measured/33.5.png').convert('RGB'),dtype='float64');prefix=next(x for x in s['layers'] if x['id']=='measured-prefix-reveal-v6')
word_boxes=[(274,500,429,582),(441,500,598,582),(612,500,813,582),(829,500,956,582),(973,500,1140,582)]
prefix_templates=[]
for b in word_boxes:
 crop=base[b[1]:b[3],b[0]:b[2]];al=np.clip((253-crop.mean(2))/253,0,1);ys,xs=np.where(al>.68);prefix_templates.append({'alpha':al,'box':(b[0]-270,b[1]-493,b[2]-270,b[3]-493),'ink':(b[0]+int(xs.min()),b[1]+int(ys.min()),b[0]+int(xs.max()+1),b[1]+int(ys.max()+1))})
source_frames=[];camera=[]
for index,file in enumerate(sorted((p/'category-all-native').glob('*.png'))):
 a=np.array(Image.open(file).convert('RGB'),dtype='uint8');t=(1000+index)/30
 boundary=gray_component(a) if t>=36.3 else None
 prefix_right=min(1155,boundary[0]-12) if boundary else 1155
 b,count=inkbox(a,x1=prefix_right)
 if b is None:
  previous=copy.deepcopy(camera[-1]);previous['t']=t;previous['visible_words']=0;camera.append(previous);source_frames.append((t,a));continue
 visible=prefix_templates[-max(1,count):];left=min(q['ink'][0] for q in visible);top=min(q['ink'][1] for q in visible);right=max(q['ink'][2] for q in visible);bottom=max(q['ink'][3] for q in visible)
 sx=(b[2]-b[0])/(right-left);sy=(b[3]-b[1])/(bottom-top);x=b[0]-(left-270)*sx;y=b[1]-(top-493)*sy
 camera.append({'t':t,'x':x,'y':y,'scaleX':sx,'scaleY':sy,'visible_words':count,'bbox':b});source_frames.append((t,a))
for key in ['x','y','scaleX','scaleY']:
 old=prefix['keyframes'][key];old=[k for k in old if k['t']<=33.3]
 if not any(abs(k['t']-33.3)<1e-8 for k in old):
  vals=sorted(prefix['keyframes'][key],key=lambda q:q['t']);v=vals[-1]['value']
  for i in range(1,len(vals)):
   if vals[i-1]['t']<=33.3<=vals[i]['t']:
    u=(33.3-vals[i-1]['t'])/(vals[i]['t']-vals[i-1]['t']);v=vals[i-1]['value']+(vals[i]['value']-vals[i-1]['value'])*u;break
  old.append({'t':33.3,'value':v,'ease':'linear'})
 prefix['keyframes'][key]=old+[{'t':q['t'],'value':q[key],'ease':'linear'} for q in camera]
for child,template in zip(prefix['children'],prefix_templates):
 child['keyframes']={'opacity':[{'t':33.3,'value':1}]+[{'t':q['t'],'value':alpha_at(a,template['alpha'],template['box'],q['x'],q['y'],q['scaleX'],q['scaleY']),'ease':'linear'} for (t,a),q in zip(source_frames,camera)]}

def nearest_camera(t):return min(camera,key=lambda q:abs(q['t']-t))
for index,(label,ref,hue) in enumerate(rows):
 image=Image.open(p/ref).convert('RGB');a=np.array(image,dtype='float64')
 if hue is None:
  black=gray_component(a);core=(black[0]-14,black[1]-15,black[2]+14,black[3]+15)
 else:core=min(components(a),key=lambda c:hue_delta(c['hue'],hue))['box']
 l,top,r,bottom=core;assetbox=(l-4,max(0,top-4),r+4,min(1080,bottom+4));asset=f'assets/category-{index}-original.png';image.crop(assetbox).save(p/asset)
 # Extract only this active row's visible bounded label. Right-edge copy may be
 # partially cropped by the source stage; no unobserved glyphs are invented.
 wordbox=(1270,max(0,top-5),1920,min(1080,bottom+5));crop=a[wordbox[1]:wordbox[3],wordbox[0]:wordbox[2]];al=np.clip((253-crop.mean(2))/253,0,1);m=al>.5;columns=np.flatnonzero(m.any(0));blocks=[]
 for xx in columns:
  if not blocks or xx>blocks[-1][1]+13:blocks.append([int(xx),int(xx)])
  else:blocks[-1][1]=int(xx)
 children=[{'id':f'category-icon-v12-{index}','type':'image','src':asset,'x':assetbox[0]-l,'y':assetbox[1]-top,'width':assetbox[2]-assetbox[0],'height':assetbox[3]-assetbox[1],'keyframes':{'opacity':[]}}];wordtemplates=[]
 words=label.split(' ')
 for j,(left,right) in enumerate(blocks):
  x0=max(0,left-2);x1=min(al.shape[1],right+3);mask=al[:,x0:x1];localbox=(wordbox[0]+x0-l,wordbox[1]-top,wordbox[0]+x1-l,wordbox[3]-top);path,stats=trace_alpha(mask,localbox[0],localbox[1]);semantic=words[j] if j<len(words) else label
  children.append({'id':f'category-word-v12-{index}-{j}','type':'path','d':path,'fill':'#000000','semanticText':semantic,'keyframes':{'opacity':[]}});wordtemplates.append((mask,localbox))
 ref_t=33.5 if ref.endswith('01.png') and index==0 else (34.93333333333333 if index==4 else 33.5+(int(Path(ref).stem)-1)*.1)
 refcamera=nearest_camera(ref_t);g={'id':f'category-native-outline-v12-{index}','type':'group','children':children,'start':1000/30,'end':36.5,'semanticText':label,'keyframes':{key:[] for key in ['x','y','scaleX','scaleY']}}
 templates.append({'label':label,'core':core,'hue':hue,'image':np.array(image.crop(assetbox),dtype='float64'),'assetbox':assetbox,'refcamera':refcamera,'wordtemplates':wordtemplates});groups.append(g)
 provenance.append({'semantic_text':label,'reference_file':ref,'source_time':ref_t,'icon_asset':asset,'icon_box':list(assetbox),'word_source_box':list(wordbox),'word_outline_count':len(wordtemplates),'bitmap_text':False,'partial_right_edge':label in ['live screen sharing','live delivery tracking']})

measurements=[]
for (t,a),cam in zip(source_frames,camera):
 components_now=components(a);assigned={}
 for c in components_now:
  i=min(range(8),key=lambda i:hue_delta(c['hue'],rows[i][2]));distance=hue_delta(c['hue'],rows[i][2])
  if distance<18 and (i not in assigned or distance<assigned[i][0]):assigned[i]=(distance,c['box'])
 black=gray_component(a)
 # Mini-app icon enters after the dashboard; before that the gray component is
 # the prefix's terminal word at x~1100 and must be rejected.
 if black and t>=35.333333333333336:assigned[8]=(0,(black[0]-14,black[1]-15,black[2]+14,black[3]+15))
 frame_records=[]
 for i,(g,temp) in enumerate(zip(groups,templates)):
  sx=cam['scaleX']/temp['refcamera']['scaleX'];sy=cam['scaleY']/temp['refcamera']['scaleY'];l,top,r,bottom=temp['core'];observed=assigned.get(i);present=observed is not None
  if present:
   ll,tt,rr,bb=observed[1];x=(ll+rr)/2-(r-l)*sx/2;y=(tt+bb)/2-(bottom-top)*sy/2
  else:x=l;y=top
  for key,value in [('x',x),('y',y),('scaleX',sx),('scaleY',sy)]:g['keyframes'][key].append({'t':t,'value':value,'ease':'linear'})
  # Scalar image-opacity fit on the original independently bounded icon.
  icon_alpha=0
  if present:
   ref=temp['image'];ww=max(1,round(ref.shape[1]*sx));hh=max(1,round(ref.shape[0]*sy));res=np.array(Image.fromarray(ref.astype('uint8')).resize((ww,hh),Image.Resampling.BICUBIC),dtype='float64');xx=round(x+(temp['assetbox'][0]-l)*sx);yy=round(y+(temp['assetbox'][1]-top)*sy);x0=max(0,xx);y0=max(0,yy);x1=min(1920,xx+ww);y1=min(1080,yy+hh)
   if x1>x0 and y1>y0:
    rr0=253-res[y0-yy:y1-yy,x0-xx:x1-xx];ss=253-a[y0:y1,x0:x1].astype('float64');den=np.sum(rr0*rr0);icon_alpha=float(np.clip(np.sum(rr0*ss)/den,0,1)) if den else 0
  g['children'][0]['keyframes']['opacity'].append({'t':t,'value':icon_alpha,'ease':'linear'})
  opacities=[]
  for child,(mask,box) in zip(g['children'][1:],temp['wordtemplates']):
   opacity=alpha_at(a,mask,box,x,y,sx,sy) if present else 0;child['keyframes']['opacity'].append({'t':t,'value':opacity,'ease':'linear'});opacities.append(opacity)
  frame_records.append({'row':i,'present':present,'x':x,'y':y,'icon_alpha':icon_alpha,'word_alpha':opacities})
 measurements.append({'t':t,'rows':frame_records})
s['layers'].extend(groups);s['source']['notes']+=' V12: categorycolumn rebuilt from bounded originalicon assets/native semantic glyphoutlines with frame-measured individualposes/opacities; source row timing and delayedfuture-row visibility replace coarse timeline. Prefixcamera and perword exit opacity measured at every nativeframe in33.333–36.467. No fullframe/videoasset.'
f=p/'final-v12.scene.json';f.write_text(json.dumps(s,indent=2));sha=hashlib.sha256(f.read_bytes()).hexdigest();(p/'final-v12-changes.json').write_text(json.dumps({'sha256':sha,'baseline':'final-v11.scene.json','delta_frames_inclusive':[[1000,1094]],'asset_and_outline_provenance':provenance,'prefix_camera':camera,'category_measurements':measurements,'limitations':'Individual native outlines are editable geometry with semantic copy. Right-edge labels contain only visible original glyphs. Measurement follows per-frame source projected geometry; no 3D model inferred.'},indent=2));print(sha)
