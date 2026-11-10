"""Native two-camera phone entrance and independently measured Memoji."""
from pathlib import Path
import copy,json,hashlib,sys
import numpy as np
from scipy import ndimage
from PIL import Image
p=Path(__file__).parent;sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'final-v12.scene.json').read_text());measure=json.loads((p/'entrance-v13-measurements.json').read_text());rows=[r for r in measure if r['t']>=436/30];phone=next(x for x in s['layers'] if x['id']=='p03-204');phone['start']=16.5;old=next(x for x in s['layers'] if x['id']=='measured-avatar-transition-v5');old['end']=436/30
normal={'x':546,'y':35,'scaleX':1.035,'scaleY':1.035};reference=Image.open(p/'measured/16.5.png').convert('RGB');ref=np.array(reference,dtype='float64')

def local(point):return ((point[0]-546)/1.035,(point[1]-35)/1.035)
def outline(box,fill,semantic,identifier,gray=0):
 crop=ref[box[1]:box[3],box[0]:box[2]];alpha=np.clip((253-crop.mean(2))/(253-gray),0,1);d,stats=trace_alpha(alpha);x,y=local((box[0],box[1]));return {'id':identifier,'type':'path','d':d,'x':x,'y':y,'scaleX':1/1.035,'scaleY':1/1.035,'fill':fill,'semanticText':semantic,'provenance':{'source_time':16.5,'box':list(box),'native_outline':True}}

def reid(layer):
 layer['id']='entrance-'+layer['id']
 for c in layer.get('children',[]):reid(c)
ui_children=copy.deepcopy(phone['children'][6:]);ui_children=[x for x in ui_children if x['id'] not in ['p03-102','p03-104','p03-105','p03-106']]
# Header copy uses original glyph outlines so its camera has no font-metric bias.
ui_children.append(outline((855,317,1053,350),'#000000','Team Lunch','entrance-header-title'))
ui_children.append(outline((1054,315,1073,354),'#8e8e93','›','entrance-header-chevron',142))
ui_children.append(outline((884,389,1049,418),'#8e8e93','Today 11:20 AM','entrance-header-date',142))
for c in ui_children:
 if c['id']=='p03-97':c['x']=58;c['y']=160
 if c['id']=='p03-99':c['y']=160
 reid(c)
# Physical hardware including the actual camera aperture, separate from UI.
hardware=copy.deepcopy(phone['children'][:3]);assetbox=(840,92,1080,165);reference.crop(assetbox).save(p/'assets/dynamic-island-original.png');x,y=local((assetbox[0],assetbox[1]));hardware.append({'id':'dynamic-island-original','type':'image','src':'assets/dynamic-island-original.png','x':x,'y':y,'width':(assetbox[2]-assetbox[0])/1.035,'height':(assetbox[3]-assetbox[1])/1.035})
for c in hardware:reid(c)
ui={'id':'measured-entrance-ui-v13','type':'group','children':ui_children,'start':436/30,'end':16.5,'keyframes':{k:[] for k in ['x','y','scaleX','scaleY','opacity']}}
device={'id':'measured-entrance-device-v13','type':'group','children':hardware,'start':436/30,'end':16.5,'keyframes':{k:[] for k in ['x','y','scaleX','scaleY','opacity']}}

# Linear interpolation only between adjacent native observations.
def interp(samples,t,key,default):
 if not samples:return default
 samples=sorted(samples,key=lambda q:q['t'])
 if t<=samples[0]['t']:return samples[0][key]
 for a,b in zip(samples,samples[1:]):
  if t<=b['t']:
   u=(t-a['t'])/(b['t']-a['t']);return a[key]+(b[key]-a[key])*u
 return samples[-1][key]
ui_poses=[];device_poses=[]
for r in measure:
 if 'title_ink' in r and 'first_T' in r:
  b=r['title_ink'];sx=(b[2]-b[0])/((1049-859)/1.035);sy=sx if b[3]>=1080 else (b[3]-b[1])/((345-321)/1.035);ui_poses.append({'t':r['t'],'x':b[0]-(859-546)/1.035*sx,'y':r['first_T']['y']-(322-35)/1.035*sy,'scaleX':sx,'scaleY':sy})
 if 'island' in r:
  b=r['island'];sx=(b[2]-b[0])/((1077-843)/1.035)
  if b[0]<=0 or b[2]>=1920:sx*=1.08
  sy=sx if b[1]==0 else (b[3]-b[1])/((162-95)/1.035);device_poses.append({'t':r['t'],'x':(b[0]+b[2])/2-400*sx,'y':b[3]-(162-35)/1.035*sy,'scaleX':sx,'scaleY':sy})
for r in rows:
 t=r['t']
 for group,poses in [(ui,ui_poses),(device,device_poses)]:
  for key in ['x','y','scaleX','scaleY']:group['keyframes'][key].append({'t':t,'value':interp(poses,t,key,normal[key]),'ease':'linear'})
  group['keyframes']['opacity'].append({'t':t,'value':1 if poses and t>=poses[0]['t'] else 0,'ease':'linear'})

# Genuine isolated full Memoji artwork from the first fully exposed arrangement.
canonical=next(r for r in measure if r['frame']==439);picture=np.array(Image.open(p/'peak-source-native/01.png').convert('RGB'));assets=[];carriers=[]
for name in ['bob','laptop','robot','alice']:
 pose=canonical['avatars'][name];cx,cy,radius=pose['cx'],pose['cy'],pose['radius'];box=(int(np.floor(cx-radius-3)),int(np.floor(cy-radius-3)),int(np.ceil(cx+radius+3)),int(np.ceil(cy+radius+3)));crop=picture[box[1]:box[3],box[0]:box[2]];yy,xx=np.indices(crop.shape[:2]);xx=xx+box[0]-cx;yy=yy+box[1]-cy;dist=np.hypot(xx,yy);annulus=(dist>radius*.86)&(dist<radius*.96);background=np.median(crop[annulus],0);rgb=crop.astype('float64');neutral=(rgb.max(2)-rgb.min(2)<6)&(rgb.min(2)>243);same=np.max(np.abs(rgb-background),2)<18;bg=neutral|same;seed=np.zeros(bg.shape,dtype=bool);seed[0]=bg[0];seed[-1]=bg[-1];seed[:,0]|=bg[:,0];seed[:,-1]|=bg[:,-1];removed=ndimage.binary_propagation(seed,mask=bg);alpha=np.where(removed,0,255).astype('uint8');alpha[dist>radius+1]=0;labels,count=ndimage.label(ndimage.binary_dilation(alpha>0,iterations=1));sizes=np.bincount(labels.ravel());sizes[0]=0;alpha[labels!=int(np.argmax(sizes))]=0;rgba=np.dstack([crop,alpha]);file=f'assets/avatar-full-{name}-v13.png';Image.fromarray(rgba).save(p/file);fill='#'+''.join(f'{round(v):02x}' for v in background);center=(cx-box[0],cy-box[1]);art={'id':'entrance-avatar-art-'+name,'type':'image','src':file,'x':0,'y':0,'width':crop.shape[1],'height':crop.shape[0]};bgcircle={'id':'entrance-avatar-circle-'+name,'type':'circle','x':center[0]-radius,'y':center[1]-radius,'width':2*radius,'height':2*radius,'fill':fill};carrier={'id':'entrance-avatar-'+name,'type':'group','children':[bgcircle,art],'keyframes':{k:[] for k in ['x','y','scaleX','scaleY']}};carriers.append((name,carrier,radius,center));assets.append({'file':file,'source_time':439/30,'source_box':list(box),'circle':pose,'background':fill,'matte':'Connected exterior background only; internal eye/teeth/Apple-logo whites retained, outside-circle stage text excluded.'})
# Gray plate and outer circular mask are measured independently from the avatars.
plate_samples=[dict(r['gray_circle'],t=r['t']) for r in measure if 'gray_circle' in r]
clip={'id':'measured-entrance-avatar-clip-v13','type':'group','start':436/30,'end':16.5,'clip':{'x':0,'y':0,'width':1,'height':1,'radius':.5},'keyframes':{k:[] for k in ['x','y','scaleX','scaleY']},'children':[{'id':'entrance-gray-plate','type':'circle','x':0,'y':0,'width':1,'height':1,'fill':'#ededed','keyframes':{'opacity':[]}}]+[c for _,c,_,_ in carriers]}
for r in rows:
 t=r['t'];ux=interp(ui_poses,t,'x',546);uy=interp(ui_poses,t,'y',35);usx=interp(ui_poses,t,'scaleX',1.035);usy=interp(ui_poses,t,'scaleY',1.035);gcx=ux+400*usx;gcy=uy+215*usy;gr=55*(usx+usy)/2
 actors=[]
 for name,carrier,base_radius,center in carriers:
  samples=[dict(rr['avatars'][name],t=rr['t']) for rr in measure if name in rr['avatars']];actors.append((name,carrier,base_radius,center,interp(samples,t,'cx',960),interp(samples,t,'cy',540),interp(samples,t,'radius',10)))
 pixels=np.array(Image.open(p/'entrance-native'/f"{r['frame']-434:03}.png").convert('RGB'));gray_values=[]
 for angle in np.linspace(0,2*np.pi,24,endpoint=False):
  px=gcx+np.cos(angle)*gr*.78;py=gcy+np.sin(angle)*gr*.78
  if not 2<px<1918 or not 2<py<1078:continue
  if any(np.hypot(px-acx,py-acy)<ar*1.05 for _,_,_,_,acx,acy,ar in actors):continue
  value=pixels[round(py)-1:round(py)+2,round(px)-1:round(px)+2].mean((0,1))
  if value.max()-value.min()<4 and value.min()>230:gray_values.append(float(value.mean()))
 opacity=float(np.clip((253-np.median(gray_values))/16,0,1)) if gray_values and t>=ui_poses[0]['t'] else 0
 enabled=opacity>.2 and all(np.hypot(acx-gcx,acy-gcy)+ar<gr*1.12 for _,_,_,_,acx,acy,ar in actors)
 radius=gr if enabled else 5000;cx=gcx;cy=gcy;left=cx-radius;top=cy-radius;diameter=2*radius
 for k,v in [('x',left),('y',top),('scaleX',diameter),('scaleY',diameter)]:clip['keyframes'][k].append({'t':t,'value':v,'ease':'linear'})
 plate=clip['children'][0]
 for k in ['x','y','scaleX','scaleY']:plate['keyframes'].setdefault(k,[])
 for k,v in [('x',(gcx-gr-left)/diameter),('y',(gcy-gr-top)/diameter),('scaleX',2*gr/diameter),('scaleY',2*gr/diameter),('opacity',opacity)]:plate['keyframes'][k].append({'t':t,'value':v,'ease':'linear'})
 for name,carrier,base_radius,center,acx,acy,ar in actors:
  scale=ar/base_radius
  for k,v in [('x',(acx-scale*center[0]-left)/diameter),('y',(acy-scale*center[1]-top)/diameter),('scaleX',scale/diameter),('scaleY',scale/diameter)]:carrier['keyframes'][k].append({'t':t,'value':v,'ease':'linear'})
# Layer order intentionally lets incoming Memoji overlap the forming title.
index=s['layers'].index(phone);s['layers'][index:index]=[device,ui,clip]
s['source']['notes']+=' V13 entrance branch: per-native-frame independent device aperture, Messages UI title, four colored Memojicircle poses, and grayplate. Old sparse easeInOut endpoint removed; parent correction includes14.533–16.467 only. New full isolated Memoji assets restore hair/body pixels unavailable in the old14.5 edge crops. No sourceframe/video layer.'
f=p/'entrance-v13.scene.json';f.write_text(json.dumps(s,indent=2));sha=hashlib.sha256(f.read_bytes()).hexdigest();(p/'entrance-v13-changes.json').write_text(json.dumps({'sha256':sha,'baseline':'final-v12.scene.json','proposed_inclusive_delta':[436,494],'modified_root_ids':['p03-204','measured-avatar-transition-v5'],'added_root_ids':[device['id'],ui['id'],clip['id']],'assets':assets,'device_poses':device_poses,'ui_poses':ui_poses,'limitations':'New clip/grayplate requires native preview validation; subpixel rasterization and photo texture differences are independent of timing.'},indent=2));print(sha)
