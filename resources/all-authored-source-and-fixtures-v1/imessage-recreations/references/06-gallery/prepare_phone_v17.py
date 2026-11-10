"""Prototype from immutable v16; no full render until checkpoint diagnosis passes."""
from pathlib import Path
import json,os,numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parent.parent;F=R/'outputs/06-gallery/final-v16';s=json.loads((F/'scene.json').read_text());ledger=json.loads((F/'snapshot.json').read_text());assetmap={x['snapshot']:os.path.relpath(x['original'],D) for x in ledger['assets']}
def walk(ls):
 for x in ls:
  if x.get('src') in assetmap:x['src']=assetmap[x['src']]
  walk(x.get('children',[]))
walk(s['layers'])
for f in s.get('fonts',[]):f['src']=assetmap.get(f['src'],f['src'])
thread=json.loads((D/'native-thread-motion-v17.json').read_text());events=json.loads((D/'native-thread-events-v17.json').read_text());by={x['frame']:x for x in events};scroll={x['frame']:x['scroll_y'] for x in thread}
for e in events:
 if e['frame']>=160 and e['priya_mse']<.02:scroll[e['frame']]=e['priya_body_y']-863
scrollpoints=[{'t':f/30,'value':v,'ease':'linear'} for f,v in sorted(scroll.items())]
def find(ident):
 def search(ls):
  for x in ls:
   if x.get('id')==ident:return x
   z=search(x.get('children',[]))
   if z:return z
 return search(s['layers'])
find('rene-final11-group-38')['keyframes']['y']=[{'t':3.7,'value':120,'ease':'linear'}]+scrollpoints
p=find('rene-final11-group-24');p['start']=147/30;p['keyframes']={'opacity':[{'t':147/30,'value':0}]};y=[]
for f in range(148,226):
 e=by[f]
 if e['priya_mse']<.02:
  y.append({'t':f/30,'value':e['priya_body_y']-863-scroll[f],'ease':'linear'});p['keyframes']['opacity'].append({'t':f/30,'value':e['priya_alpha'],'ease':'linear'})
p['keyframes']['y']=y
# Preserve fully rendered original Book artwork; derive source birth fade/bounce.
b=find('rene-final11-group-29');baseline=28000;full=by[195]['book_saturation']-baseline;birth=[e for e in events if e['frame']<200 and (e['book_saturation']-baseline)/full>.01];first=birth[0]['frame'];b['start']=(first-1)/30;b['keyframes']={'opacity':[{'t':(first-1)/30,'value':0}],'y':[]}
asset=np.asarray(Image.open(D/'assets/intro-message-book.png').convert('RGB')).astype(float);mask=(asset[:,:,2]-asset[:,:,0]>20)&(asset[:,:,2]>asset[:,:,1]*1.05);yy,xx=np.nonzero(mask);lastblue=int(yy.max()+1)
for e in birth:
 alpha=float(np.clip((e['book_saturation']-baseline)/full,0,1));b['keyframes']['opacity'].append({'t':e['frame']/30,'value':alpha,'ease':'linear'})
 if e['book_blue_box']:b['keyframes']['y'].append({'t':e['frame']/30,'value':e['book_blue_box'][3]-1033-scroll[e['frame']]-lastblue,'ease':'linear'})
b['keyframes']['y'].append({'t':200/30,'value':0,'ease':'linear'});b['keyframes']['opacity'].append({'t':200/30,'value':1})
done=find('rene-final11-group-37');done['keyframes']['y']=[{'t':e['frame']/30,'value':e['done_body_y']-1235-scroll[e['frame']],'ease':'linear'} for e in events if e['frame']>=204 and e['done_mse']<.02]
# Composer and keyboard poses derive from source cross/panel positions.
for ident,key,base in [('rene-final11-group-61','plus_top',886),('rene-final11-group-62','keyboard_top',1010)]:
 node=find(ident);oldlast=node['keyframes']['y'][-1];node['keyframes']['y']=[{'t':3.7,'value':30}]+[{'t':r['frame']/30,'value':r[key]-base,'ease':'linear'} for r in thread if r[key] is not None]+[oldlast]
# Authentic bounded header and independently animated message artwork.
ref=Image.open(D/'keyframes/026.50.png').convert('RGBA');newassets=[]
# Source5 residual diagnosis isolates native composer/keyboard artwork and hardware pose.
ref5=Image.open(D/'keyframes/005.00.png').convert('RGBA');ref7=Image.open(D/'keyframes/007.50.png').convert('RGBA')
ref5.crop((424,810,1490,970)).save(D/'assets/intro-composer-original-v17.png')
comp=find('rene-final11-group-61');comp['children']=[{'type':'image','id':'phone-v17-intro-composer','src':'assets/intro-composer-original-v17.png','x':424,'y':838,'width':1066,'height':160}]
k7=np.asarray(ref7.convert('RGB')).astype(float);kr=k7[850:,800:1100];km=(kr[:,:,2]-kr[:,:,0]>2)&(kr.mean(axis=2)<244)&(kr.mean(axis=2)>180);detector=int(np.where(km.sum(axis=1)>150)[0].min()+850)
ref7.crop((389,918,1540,1080)).save(D/'assets/intro-keyboard-original-v17.png');kb=find('rene-final11-group-62');background=kb['children'][0];kb['children']=[background,{'type':'image','id':'phone-v17-intro-keyboard','src':'assets/intro-keyboard-original-v17.png','x':395,'y':1010-(detector-918),'width':1151,'height':162}];kb['keyframes']['y'][-1]={'t':7.5,'value':detector-1010,'ease':'linear'}
original=Image.open(D/'assets/lower-phone-hardware.png').convert('RGBA');extended=Image.new('RGBA',(original.width,1880));extended.paste(original,(0,400));extended.paste(original.crop((0,0,original.width,1)).resize((original.width,400)),(0,0));extended.paste(original.crop((0,original.height-1,original.width,original.height)).resize((original.width,400)),(0,1480));extended.save(D/'assets/lower-phone-hardware-extended-v17.png');hw=find('rene-final11-image-60');hw['src']='assets/lower-phone-hardware-extended-v17.png';hw['height']=1880;hw['keyframes']={'y':[{'t':k['t'],'value':k['value']+66-400,'ease':'linear'} for k in comp['keyframes']['y']]}
newassets.extend([{'path':'assets/intro-composer-original-v17.png','frame':5,'box':[424,810,1490,970],'kind':'bounded static input-row artwork; internal UI text bitmap; outer pose editable'},{'path':'assets/intro-keyboard-original-v17.png','frame':7.5,'box':[389,918,1540,1080],'kind':'bounded static prediction-bar/visible-key artwork; internal UI text bitmap; outer pose editable'},{'path':'assets/lower-phone-hardware-extended-v17.png','frame':6.5,'box':[337,0,1593,1080],'kind':'physical hardware only; transparent screen; uniform bottom border texture extended for native camera motion'}])
def crop(name,box):
 path='assets/'+name+'.png';ref.crop(box).save(D/path);newassets.append({'path':path,'frame':26.5,'box':list(box),'kind':'bounded static birthday UI component; internal text bitmap; outer native lifecycle/camera editable'});return path
header=crop('birthday-header-original',(649,24,1271,305))
phone=ref.crop((620,0,1302,1080));outer=Image.new('L',phone.size);draw=ImageDraw.Draw(outer);draw.rounded_rectangle((0,0,681,1479),radius=135,fill=255);draw.rounded_rectangle((29,24,650,1479),radius=110,fill=0);phone.putalpha(outer);phone.save(D/'assets/birthday-hardware-original.png');newassets.append({'path':'assets/birthday-hardware-original.png','frame':26.5,'box':[620,0,1302,1080],'kind':'genuine physical hardware only; screen interior cleared'})
configs=[('Emma',(664,325,1115,401),22.9),('Fuji',(664,403,1165,562),23.8),('Wait',(888,569,1258,646),24.5),('Order',(896,648,1258,738),24.9),('Done',(664,733,978,809),25.5),('Remember',(664,812,1033,903),26)]
children=[{'type':'rect','id':'phone-v17-background','x':29,'y':24,'width':622,'height':1456,'radius':110,'fill':'#fafafa'},{'type':'image','id':'phone-v17-hardware','src':'assets/birthday-hardware-original.png','x':0,'y':0,'width':682,'height':1080},{'type':'group','id':'phone-v17-header-clip','clip':{'x':29,'y':24,'width':622,'height':1456,'radius':110},'children':[{'type':'image','id':'phone-v17-header','src':header,'x':29,'y':24,'width':622,'height':281}]}]
for name,box,start in configs:
 path=crop('birthday-message-'+name.lower(),box);node={'type':'image','id':'phone-v17-message-'+name,'src':path,'x':box[0]-620,'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':start}
 if name=='Order':node['keyframes']={'y':[{'t':24.9,'value':box[1]+12},{'t':25,'value':box[1]+5},{'t':25.25,'value':box[1]}]}
 children.append(node)
node=find('g-1306');node['children']=children;node['x']=620;cam=json.loads((D/'native-birthday-camera-v17.json').read_text());centers=json.loads((D/'native-birthday-center-v17.json').read_text())+json.loads((D/'native-birthday-tail-v17.json').read_text());poses={x['frame']:x['camera_y'] for x in cam}
for c in centers:
 if c['frame'] not in poses and c['center_top_y'] is not None:poses[c['frame']]=float(c['center_top_y']-10)
valid=[c['frame'] for c in centers if c['center_top_y'] is not None];node['start']=min(valid)/30;node['end']=(max(valid)+2)/30;poses[max(valid)+1]=1100;node['keyframes']['y']=[{'t':f/30,'value':v,'ease':'linear'} for f,v in sorted(poses.items()) if min(valid)<=f<=max(valid)+1]
# The following large headline enters from above while the phone exits below.
import importlib.util
spec=importlib.util.spec_from_file_location('trace_glyphs',D.parent/'02-danieltian/trace_glyphs.py');tracer=importlib.util.module_from_spec(spec);spec.loader.exec_module(tracer)
measure=json.loads((D/'native-tracks-title-v17.json').read_text());reference=np.asarray(Image.open(D/'keyframes/027.80.png').convert('L')).astype(float);base=next(x['bbox'] for x in measure if x['frame']==834);dark=reference<140;xs=np.where(dark.any(axis=0))[0];gg=[]
for xx in xs:
 if not gg or xx-gg[-1][-1]>45:gg.append([int(xx)])
 else:gg[-1].append(int(xx))
paths=[]
for i,g in enumerate(gg):
 mm=dark[:,g[0]:g[-1]+1];yy,xx=np.nonzero(mm);bb=[g[0]-2,int(yy.min())-2,g[-1]+3,int(yy.max())+3];alpha=1-reference[bb[1]:bb[3],bb[0]:bb[2]]/255;d,stats=tracer.trace_alpha(alpha,bb[0],bb[1]);paths.append({'type':'path','id':'phone-v17-tracks-word-'+str(i),'d':d,'fill':'#000000','semanticText':['Tracks','what'][i]})
newassets.append({'element_id':'phone-v17-tracks-headline','frame':27.8,'box':base,'kind':'original static typography traced to independent native editable word outlines; native motion, no raster playback'})
pose=[];bw,bh=base[2]-base[0],base[3]-base[1]
pose.append((813,[base[0],-214.1,1,1]))
for row in measure:
 if not row['bbox']:continue
 bb=row['bbox']
 if bb[1]==0 and bb[3]-bb[1]<bh-2:values=[base[0],bb[3]-bh,1,1]
 else:values=[bb[0],bb[1],(bb[2]-bb[0])/bw,(bb[3]-bb[1])/bh]
 pose.append((row['frame'],values))
headline={'type':'group','id':'phone-v17-tracks-headline','start':813/30,'end':846/30,'children':[{'type':'group','id':'phone-v17-tracks-local','x':-base[0],'y':-base[1],'children':paths}],'keyframes':{key:[{'t':f/30,'value':v[i],'ease':'linear'} for f,v in pose] for i,key in enumerate(['x','y','scaleX','scaleY'])}}
s['layers']=[headline if x.get('id')=='g-1308' else x for x in s['layers']]
(D/'scene-v17-prototype.json').write_text(json.dumps(s,indent=2)+'\n');(D/'assets/phone-v17-candidate-provenance.json').write_text(json.dumps(newassets,indent=2));print('Prototype ready',node['start'],node['end'],'Pry147,Book',first,'camera25',poses[750])
