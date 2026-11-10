from pathlib import Path
from PIL import Image,ImageFont
import json,subprocess,io,numpy as np
R=Path('/workspace/imessage-recreations/references/02-danieltian');scene=json.loads((R/'scene.json').read_text());changes=[]
# Correct material-color coupling: the incoming UI helper had not recognized this outgoing blue hex.
def walk(l):
 if l.get('type')=='group' and any(c.get('type')=='rect' and c.get('fill','').lower()=='#3ca4f9' for c in l.get('children',[])):
  for c in l['children']:
   if c.get('type')=='text':c['fill']='#FFFFFF';changes.append(c['id'])
 for c in l.get('children',[]):walk(c)
for l in scene['layers']:walk(l)
font=ImageFont.truetype(str(R/'assets/Inter-400.ttf'),68)
def text(id,s,x,y,**kw):return dict(id=id,type='text',text=s,x=x,y=y,fontFamily='Photon Sans',fontSize=68,fontWeight=400,**({'fill':'#222222'}|kw))
def k(pts):return [dict(t=t,value=v,**({'ease':e} if e else {})) for t,v,e in pts]
L=scene['layers'];full='muse, my boss wants a team offsite\ntmr. can u help?'
old=[l for l in L if l.get('type')=='text' and l.get('x')==466 and l.get('y')==485 and l.get('text','').startswith('muse')];ids={l['id'] for l in old};L[:]=[l for l in L if l['id'] not in ids]
def time_at(n):
 if n<=31:return 3.14+n*(.86/31)
 if n<=39:return 4+(n-31)*(.5/8)
 if n<=45:return 4.5+(n-39)*(.5/6)
 return 5+(n-45)*(.4/6)
# Source4.0 literal31chars,4.5literal39chars,5.0literal45chars. Use one regular font scale throughout typing.
box=font.getbbox(full[:31]);sx=988/(box[2]-box[0]);sy=60/(box[3]-box[1]);comp=[]
for n in range(1,len(full)+1):
 st=time_at(n);end=time_at(n+1) if n<len(full) else 5.9
 comp.append(text(f'composer-v5-char-{n}',full[:n],318,496,start=st,end=end,scaleX=sx,scaleY=sy,lineHeight=96/sy,keyframes={'y':k([(3.14,496,None),(4.08,496,None),(4.4,457,'easeInOut'),(5.9,457,None)])}))
L.extend(comp)
for l in L:
 if l.get('type')=='group' and l.get('start')==2.2 and l.get('end')==5.9:
  for c in l.get('children',[]):
   if c.get('type')=='rect' and c.get('width')==1280:
    c['fill']='url(#composer-v5)';c['stroke']='#F3F3F3';c['keyframes']={'x':k([(2.2,420,None),(3.1,420,None),(3.35,220,'easeOut')]),'width':k([(2.2,1280,None),(3.1,1280,None),(3.35,1480,'easeOut')]),'y':k([(2.2,470,None),(3.35,460,'easeOut'),(4.08,460,None),(4.4,412,'easeInOut')]),'height':k([(2.2,150,None),(3.35,160,'easeOut'),(4.08,160,None),(4.4,256,'easeInOut')])}
   elif c.get('type') in ['circle','text']:c['end']=3.1
 if l.get('type')=='text' and l.get('text')=='iMessage' and l.get('start')==2.65:l['end']=3.14;l['fontWeight']=400
 if l.get('type')=='group' and l.get('x')==1550 and l.get('y')==492:l['keyframes']={'y':k([(3.12,484,None),(4.08,484,None),(4.4,533,'easeInOut')])}
scene['gradients'].append(dict(id='composer-v5',type='linear',stops=[dict(offset='0%',color='#F5F5F5'),dict(offset='26%',color='#FDFDFD'),dict(offset='100%',color='#FDFDFD')]))
L.append(dict(id='composer-v5-microphone',type='group',x=1614,y=496,start=2.65,end=3.14,children=[dict(id='mic-v5-capsule',type='rect',width=18,height=36,radius=9,fill='none',stroke='#D0D0D0',strokeWidth=4),dict(id='mic-v5-stand',type='path',d='M-7 22 V31 Q-7 47 9 47 Q26 47 26 31 V22 M9 47 V59 M-2 59 H20',fill='none',stroke='#D0D0D0',strokeWidth=4)]))
# Dynamically recenter the reasoning block as each new line appears.
reason=['Checking what I know about Photon...','👥 9 people · 📍880 Harrison St · ❤️Loves sushi','Offsite tomorrow. What do we need?','🏠 A place to stay','🚗 Rides','🍣 Food','Let me find agents who can help...'];timings=[8.7,9.3,9.55,9.8,10.05,10.3,10.8];pitch=106.8
oldReason=[l for l in L if l.get('type')=='text' and l.get('text') in reason];rids={l['id'] for l in oldReason};L[:]=[l for l in L if l['id'] not in rids]
# Static Apple emoji crops preserve icon artwork; text stays native and independently editable.
def crop(name,box):
 p=R/'assets'/name
 if not p.exists():Image.open(R/'keyframes/10.50.png').convert('RGBA').crop(box).save(p)
 return 'assets/'+name
icons={'people':crop('reason-people.png',(218,339,286,407)),'pin':crop('reason-pin.png',(644,336,687,405)),'heart':crop('reason-heart.png',(1258,336,1328,406)),'house':crop('reason-house.png',(205,550,277,622)),'car':crop('reason-car.png',(204,658,279,728)),'food':crop('reason-food.png',(205,765,277,834))}
for i,s in enumerate(reason):
 st=timings[i];top=490+i*pitch;track=[(8.7,top,None)]
 for j,t in enumerate(timings[1:],1):track.extend([(t-.08,top-(j-1)*pitch/2,None),(t+.12,top-j*pitch/2,'easeInOut')])
 color='#A4A4A4' if i>=2 else '#BDBDBD'
 if i==0:
  box=font.getbbox(s);node=text('reason-v5-line0',s,216,top,fill='#8D8D8D',scaleX=1244/(box[2]-box[0]),scaleY=68/(box[3]-box[1]))
 elif i==1:
  def tx(id,s,x):return text(id,s,x,0,fill='#BDBDBD')
  node=dict(id='reason-v5-line1',type='group',children=[dict(id='reason-v5-people',type='image',src=icons['people'],x=218,y=8,width=68,height=68),tx('reason-v5-people-copy','9 people ·',308),dict(id='reason-v5-pin',type='image',src=icons['pin'],x=644,y=5,width=43,height=69),tx('reason-v5-location-copy','880 Harrison St ·',697),dict(id='reason-v5-heart',type='image',src=icons['heart'],x=1258,y=5,width=70,height=70),tx('reason-v5-sushi-copy','Loves sushi',1335)])
 elif i in [3,4,5]:
  key=['house','car','food'][i-3];word=['A place to stay','Rides','Food'][i-3];node=dict(id=f'reason-v5-line{i}',type='group',children=[dict(id=f'reason-v5-emoji-{key}',type='image',src=icons[key],x=205,y=11,width=72,height=72),text(f'reason-v5-copy-{i}',word,291,0,fill=color)])
 else:node=text(f'reason-v5-line{i}',s,216,top,fill=color)
 node.update(start=st,end=12.2,keyframes={'y':k(track),'opacity':k([(st,0,None),(st+.18,1,'easeOut')])})
 if i in [1,3,4,5]:node['y']=top
 if i==0:node['keyframes']['fill']=k([(st,'#8D8D8D',None),(9.28,'#8D8D8D',None),(9.5,'#BDBDBD','easeOut')])
 L.append(node)
# Measured later reasoning composition contracts slightly after the final line appears.
reason_nodes=[l for l in L if l['id'].startswith('reason-v5-line')];reason_ids={l['id'] for l in reason_nodes};L[:]=[l for l in L if l['id'] not in reason_ids]
L.append(dict(id='reason-v5-measured-camera',type='group',start=8.7,end=12.2,originX=960,originY=540,children=reason_nodes,keyframes={'scaleX':k([(10.7,1,None),(11.65,.9775,'easeInOut')]),'scaleY':k([(10.7,1,None),(11.65,.9573,'easeInOut')]),'x':k([(10.7,0,None),(11.65,17,'easeInOut')]),'y':k([(10.7,0,None),(11.65,9,'easeInOut')])}))
# Match phone width and metal side hardware independently from its editable interface.
phone=next(l for l in L if l.get('type')=='group' and l.get('start')==6.2 and l.get('end')==8.73)
rail_source=Image.open(R/'keyframes/07.50.png').convert('RGB');rail_source.crop((296,0,362,1080)).save(R/'assets/phone-left-rail.png');rail_source.crop((1558,0,1623,1080)).save(R/'assets/phone-right-rail.png')
newchildren=[]
for c in phone['children']:
 if c.get('type')=='rect' and c.get('x') in [298,1510,1518]:continue
 if c.get('type')=='rect' and c.get('x')==323:c['width']=1270
 if c.get('type')=='rect' and c.get('x')==350:c['x']=357;c['width']=1206
 newchildren.append(c)
phone['children']=newchildren[:2]+[dict(id='phone-v5-left-hardware',type='image',src='assets/phone-left-rail.png',x=296,y=0,width=66,height=1080),dict(id='phone-v5-right-hardware',type='image',src='assets/phone-right-rail.png',x=1558,y=0,width=65,height=1080)]+newchildren[2:]
for g in phone['children']:
 if g.get('type')=='group' and any(c.get('type')=='rect' and c.get('fill','').lower()=='#3ca4f9' for c in g.get('children',[])):
  for c in g['children']:
   if c.get('type')=='rect':c['radius']=65
   if c.get('type')=='text':c['x']+=14;c['y']+=14
scene['source']['notes']+=' UI v5 corrects outgoing blue bubble white text, composer geometry/regular typing at measured character-count times, microphone, correct phone interior width and declared static metallic hardware rails, and recentered reasoning block with original Apple emoji artwork.'
(R/'scene-v5-ui.json').write_text(json.dumps(scene,indent=2));(R/'ui-v5-provenance.json').write_text(json.dumps({'corrected_white_text_nodes':changes,'composer_character_anchors':{'4.0':31,'4.5':39,'5.0':45,'5.4':51},'reasoning_heading_source_bbox_9s':[218,507,1462,575],'changed_intervals':[[2.2,12.2]],'known_limit':'Reasoning recenter/interpolation and body typography remain approximations; individual Apple emoji crops explicitly declared.'},indent=2));print('Wrote02 scene-v5-ui.json; blue text fixes',changes)
