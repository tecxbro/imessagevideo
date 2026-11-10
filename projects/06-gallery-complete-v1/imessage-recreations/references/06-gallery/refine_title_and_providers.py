"""Fit native title poses and independently animate genuine provider artwork."""
from pathlib import Path
import json,importlib.util,subprocess
import numpy as np
from PIL import Image,ImageFont,ImageDraw
D=Path(__file__).resolve().parent;R=D.parent.parent
s=json.loads((D/'scene.json').read_text());prov=json.loads((D/'assets/asset-provenance.json').read_text())
rows=json.loads((D/'native-title-component-tracks.json').read_text())
s['layers']=[x for x in s['layers'] if not x.get('id','').startswith('rene-v16-')]
prov=[x for x in prov if not x.get('element_id','').startswith('rene-v16-') and not x.get('path','').startswith('native-path:rene-v16-') and not x.get('path','').startswith('assets/provider-')]
spec=importlib.util.spec_from_file_location('trace_glyphs',D.parent/'02-danieltian/trace_glyphs.py');tracer=importlib.util.module_from_spec(spec);spec.loader.exec_module(tracer)
def mt(frame):return frame/30 if frame<1230 else (frame-181)/30
def box(mask,x0=0,y0=0):
 y,x=np.nonzero(mask)
 return None if len(x)<20 else [int(x.min()+x0),int(y.min()+y0),int(x.max()+1+x0),int(y.max()+1+y0)]
def groups(mask,x0=0,y0=0,gap=25):
 xs=np.where(mask.any(axis=0))[0];gg=[]
 for x in xs:
  if not gg or x-gg[-1][-1]>gap:gg.append([int(x)])
  else:gg[-1].append(int(x))
 out=[]
 for g in gg:
  bb=box(mask[:,g[0]:g[-1]+1],g[0]+x0,y0)
  if bb:out.append(bb)
 return out
def tracks(points,key):return [{'t':mt(f),'value':float(v[key]),'ease':'linear'} for f,v in points]
def text_node(label,points,ident,color='#000000',fontSize=126):
 font=ImageFont.truetype(str(R/'shared/fonts/SF-Pro-Display-Medium.otf'),fontSize)
 im=Image.new('L',(1800,250),255);ImageDraw.Draw(im).text((0,0),label,font=font,fill=0);bb=box(np.asarray(im)<180);w,h=bb[2]-bb[0],bb[3]-bb[1]
 pose=[]
 for f,b in points:
  sx,sy=(b[2]-b[0])/w,(b[3]-b[1])/h;pose.append((f,[b[0]-bb[0]*sx,b[1]-bb[1]*sy,sx,sy]))
 return {'type':'text','id':ident,'text':label,'x':0,'y':0,'fontSize':fontSize,'fontFamily':'SF Pro Display','fontWeight':500,'lineHeight':fontSize*1.2,'fill':color,'start':mt(points[0][0]),'end':mt(points[-1][0]+1),'keyframes':{k:tracks(pose,i) for i,k in enumerate(['x','y','scaleX','scaleY'])}}
# Replace the two guessed Introducing scenes by one continuous editable word.
s['layers']=[x for x in s['layers'] if x.get('id') not in ['g-1161','g-1165']]
intro=[(r['frame'],r['parts']['Introducing']) for r in rows if 'Introducing' in r['parts']]
font=ImageFont.truetype(str(R/'shared/fonts/SF-Pro-Display-Medium.otf'),126)
im=Image.new('L',(1000,250),255);ImageDraw.Draw(im).text((0,0),'Introducing',font=font,fill=0);ib=box(np.asarray(im)<180)
rest=next(b for f,b in intro if f==300);iw,ih=rest[2]-rest[0],rest[3]-rest[1];sx,sy=iw/(ib[2]-ib[0]),ih/(ib[3]-ib[1])
word={'type':'text','id':'rene-v16-introducing-native','text':'Introducing','x':-ib[0]*sx,'y':-ib[1]*sy,'fontSize':126,'fontFamily':'SF Pro Display','fontWeight':500,'fill':'#000000','scaleX':sx,'scaleY':sy}
cover={'type':'rect','id':'rene-v16-introducing-reveal','x':0,'y':-100,'width':2000,'height':500,'fill':'#ffffff','keyframes':{'x':[{'t':mt(f),'value':b[2]-b[0],'ease':'linear'} for f,b in intro]}}
s['layers'].append({'type':'group','id':'rene-v16-introducing','children':[word,cover],'start':mt(intro[0][0]),'end':mt(intro[-1][0]+1),'keyframes':{'x':[{'t':mt(f),'value':b[0],'ease':'linear'} for f,b in intro],'y':[{'t':mt(f),'value':b[1],'ease':'linear'} for f,b in intro],'scaleY':[{'t':mt(f),'value':min(1,(b[3]-b[1])/91),'ease':'linear'} for f,b in intro]}})
source=np.asarray(Image.open(D/'keyframes/010.00.png').convert('RGB')).astype(float)
for name,bounds in [('mascot',(1063,489,1156,592)),('Rene',(1187,496,1448,584))]:
 crop=source[bounds[1]:bounds[3],bounds[0]:bounds[2]];alpha=1-crop.mean(axis=2)/255;d,stats=tracer.trace_alpha(alpha,bounds[0],bounds[1]);points=[(r['frame'],r['parts'][name]) for r in rows if name in r['parts']]
 b0=[1065,491,1154,590] if name=='mascot' else [1189,498,1446,582]
 outline={'type':'group','id':'rene-v16-'+name+'-local','x':-b0[0],'y':-b0[1],'children':[{'type':'path','id':'rene-v16-'+name+'-native','d':d,'fill':'#000000'}]}
 pose=[]
 for f,b in points:
  shift=min(0,b[1]-b0[1]);px=b[0] if name=='Rene' else b0[0];left=0 if name=='Rene' else max(0,b[0]-b0[0]);right=b[2]-b[0] if name=='Rene' else b[2]-b0[0];pose.append((f,[px,b0[1]+shift,left,right,max(0,b[1]-b0[1]-shift),b[3]-b0[1]-shift]))
 bw,bh=b0[2]-b0[0],b0[3]-b0[1]
 masks=[{'type':'rect','id':'rene-v16-'+name+'-leftmask','x':-3,'y':-3,'width':3,'height':bh+6,'fill':'#ffffff','keyframes':{'width':[{'t':mt(f),'value':v[2]+3,'ease':'linear'} for f,v in pose]}},{'type':'rect','id':'rene-v16-'+name+'-rightmask','x':bw,'y':-3,'width':3,'height':bh+6,'fill':'#ffffff','keyframes':{'x':tracks(pose,3),'width':[{'t':mt(f),'value':max(0,bw-v[3]+3),'ease':'linear'} for f,v in pose]}},{'type':'rect','id':'rene-v16-'+name+'-topmask','x':-3,'y':-3,'width':bw+6,'height':3,'fill':'#ffffff','keyframes':{'height':[{'t':mt(f),'value':v[4]+3,'ease':'linear'} for f,v in pose]}},{'type':'rect','id':'rene-v16-'+name+'-bottommask','x':-3,'y':bh,'width':bw+6,'height':3,'fill':'#ffffff','keyframes':{'y':tracks(pose,5),'height':[{'t':mt(f),'value':max(0,bh-v[5]+3),'ease':'linear'} for f,v in pose]}}]
 s['layers'].append({'type':'group','id':'rene-v16-'+name,'children':[outline]+masks,'start':mt(points[0][0]),'end':mt(points[-1][0]+1),'keyframes':{'x':tracks(pose,0),'y':tracks(pose,1)}})
 prov.append({'element_id':'rene-v16-'+name,'frame':'010.00','box':list(bounds),'kind':'bounded original brand traced to native editable path; native rectangular reveal masks','trace':stats})
# Fit each independently editable first-title phrase and second line from measured masks.
labels=['The','best contact','in your phone','with multiplayer mode']
for l in s['layers']:
 def has(q):return q.get('text') in labels or any(has(c) for c in q.get('children',[]))
 if has(l):l['_replace_v16']=True
s['layers']=[x for x in s['layers'] if not x.get('_replace_v16')]
for i,label in enumerate(labels):
 pts=[(r['frame'],r['parts'][label]) for r in rows if label in r['parts']]
 if pts:s['layers'].append(text_node(label,pts,'rene-v16-title-'+str(i),'#218567' if label=='best contact' else '#000000'))
# Preserve the original portrait choreography but fix the measured title dimensions.
for l in s['layers']:
 if l.get('id')=='g-1239':
  t=l['children'][0];t.update(x=958.037,y=452.961,scaleX=.991*1192/1214,scaleY=110/103)
# Decode only the bounded provider strip. Each text/icon remains an independent node.
cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','44.4','-i',str(D/'source.mp4'),'-t','3','-vf','crop=1320:400:300:350','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1']
(D/'provider-measurements').mkdir(exist_ok=True)
p=subprocess.Popen(cmd,stdout=subprocess.PIPE);provider=[]
for f in range(1332,1422):
 data=p.stdout.read(1320*400*3)
 if len(data)!=1320*400*3:raise RuntimeError('Incomplete provider reference decode')
 a=np.frombuffer(data,np.uint8).reshape(400,1320,3);z=a.astype(float);parts={}
 if f==1416:Image.fromarray(a).save(D/'provider-measurements/001416.png')
 black=groups(np.max(a,axis=2)<140,300,350,gap=35)
 if f<=1417:
  if black:parts['already']=black[0]
  if len(black)>1:parts['text']=[black[1][0],min(x[1] for x in black[1:]),black[-1][2],max(x[3] for x in black[1:])]
 green=groups((z[:,:,1]>z[:,:,0]*1.2)&(z[:,:,1]>z[:,:,2]*1.15)&(z[:,:,0]<230),300,350)
 blue=groups((z[:,:,2]>z[:,:,1]*1.1)&(z[:,:,2]>z[:,:,0]*1.2)&(z[:,:,1]>60),300,350)
 if green:parts['Messages']=green[0]
 if len(green)>1:parts['WhatsApp']=green[-1]
 if blue:parts['Telegram']=blue[0]
 if f>=1418 and black:parts['mascot']=black[0]
 provider.append({'frame':f,'parts':parts})
p.wait();assert p.returncode==0
(D/'native-provider-component-tracks.json').write_text(json.dumps(provider,indent=2))
s['layers']=[x for x in s['layers'] if x.get('id') not in ['g-1338','g-1349']]
for label in ['already','text']:
 pts=[(r['frame'],r['parts'][label]) for r in provider if label in r['parts']]
 s['layers'].append(text_node(label,pts,'rene-v16-provider-'+label))
base=Image.open(D/'provider-measurements/001416.png').convert('RGB')
for label,pad in [('Messages',12),('Telegram',25),('WhatsApp',12)]:
 bb=next(r['parts'][label] for r in provider if r['frame']==1416);cropbox=[bb[0]-pad,bb[1]-pad,bb[2]+pad,bb[3]+pad];local=[cropbox[0]-300,cropbox[1]-350,cropbox[2]-300,cropbox[3]-350];name='assets/provider-'+label.lower()+'-original.png';asset=base.crop(local);asset.save(D/name)
 pts=[]
 for r in provider:
  if label not in r['parts']:continue
  b=r['parts'][label];sx=(b[2]-b[0])/(bb[2]-bb[0]);sy=(b[3]-b[1])/(bb[3]-bb[1]);pts.append((r['frame'],[b[0]-pad*sx,b[1]-pad*sy,sx,sy]))
 s['layers'].append({'type':'image','id':'rene-v16-provider-'+label,'src':name,'x':0,'y':0,'width':asset.width,'height':asset.height,'start':mt(pts[0][0]),'end':mt(1418),'keyframes':{k:tracks(pts,i) for i,k in enumerate(['x','y','scaleX','scaleY'])}})
 prov.append({'path':name,'frame':47.2,'box':cropbox,'kind':'bounded original 3D provider-icon artwork; independent native pose and lifecycle'})
# The next mascot is visible four frames earlier than our previous strip sampling began.
for l in s['layers']:
 if l.get('type')=='image' and l.get('src')=='assets/rene-mascot.png' and abs(l.get('start',0)-mt(1422))<1e-6:
  l['start']=mt(1418);asset=np.asarray(Image.open(D/l['src']).convert('RGBA'));ab=box(asset[:,:,3]>25);aw,ah=ab[2]-ab[0],ab[3]-ab[1]
  for row in reversed(provider):
   if row['frame']<1418 or 'mascot' not in row['parts']:continue
   b=row['parts']['mascot'];sx,sy=(b[2]-b[0])/aw,(b[3]-b[1])/ah
   for key,val in [('x',b[0]-ab[0]*sx),('y',b[1]-ab[1]*sy),('scaleX',sx),('scaleY',sy)]:l['keyframes'][key].insert(0,{'t':mt(row['frame']),'value':val,'ease':'linear'})
(D/'scene.json').write_text(json.dumps(s,indent=2)+'\n');(D/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
print('Native title and provider components fitted; final v16 ranges240:374,555:686,1151:1240')
