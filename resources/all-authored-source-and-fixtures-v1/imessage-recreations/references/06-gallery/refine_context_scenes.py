from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path('/workspace/imessage-recreations');d=root/'references/06-gallery';s=json.loads((d/'scene.json').read_text());prov=json.loads((d/'assets/asset-provenance.json').read_text());n=0

def ident(p):
 global n;n+=1;return f'context-v8-{p}-{n}'
def rect(x,y,w,h,fill='#ffffff',radius=0,**kw):return dict(type='rect',id=ident('rect'),x=x,y=y,width=w,height=h,fill=fill,radius=radius,**kw)
def txt(t,x,y,z=32,fill='#111111',weight=400,**kw):return dict(type='text',id=ident('text'),text=t,x=x,y=y,fontFamily='SF Pro Display',fontSize=z,fontWeight=weight,lineHeight=z*1.18,fill=fill,**kw)
def img(src,x,y,w,h):return dict(type='image',id=ident('image'),src=src,x=x,y=y,width=w,height=h)
def circ(x,y,w,fill,**kw):return dict(type='circle',id=ident('circle'),x=x,y=y,width=w,height=w,fill=fill,**kw)
def path(p,**kw):return dict(type='path',id=ident('path'),d=p,**kw)
def tr(*ps):return [{'t':t,'value':v,'ease':'easeOut'} for t,v in ps]
def crop(fr,box,name,rounding=None):
 im=Image.open(d/f'keyframes/{fr}.png').convert('RGBA').crop(box)
 if rounding:
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,im.width-1,im.height-1),radius=rounding,fill=255);im.putalpha(mask)
 src=f'assets/{name}.png';im.save(d/src);prov.append({'path':src,'source':'source.mp4','timestamp':float(fr),'box':box,'kind':'isolated static pictorialasset; outerUI native'});return src
avatar=crop('003.00',(892,235,1031,375),'cabin-group-avatar',69)
gift=crop('022.10',(1225,201,1283,259),'birthday-gift-emoji')
# Specific groupchatheader; no globalReneheader change.
for g in s['layers']:
 if g.get('start')==1.1:
  kept=[]
  for q in g['children']:
   remove=(q.get('src')=='assets/rene-mascot.png' or (q.get('type')=='circle' and q.get('x')==286 and q.get('y')==124) or (q.get('type')=='rect' and q.get('x')==278 and q.get('y')==225) or q.get('text')=='Cabin trip 🏕️' or (q.get('type')=='path' and q.get('d','').startswith('M 380 245')))
   if not remove:kept.append(q)
  kept +=[img(avatar,294,136,115,116),rect(240,240,225,62,'#ffffff',31),txt('Cabin trip 🏕️',352,252,31,'#000000',700,textAnchor='middle'),path('M 441 255 L 448 266 L 441 277',fill='none',stroke='#aaaaaa',strokeWidth=5)]
  g['children']=kept
# Source17–18nativephonecamera pullsback whiledraftarrives; source18background isinboxrows.
for g in s['layers']:
 if g.get('start')==16.7:
  g.update(x=559,y=58)
  g['keyframes']={'x':tr((16.7,559),(17.15,559),(18.0,623)),'y':tr((16.7,58),(17.15,58),(18.0,105)),'scaleX':tr((16.7,1.13),(17.15,1.13),(18,0.91)),'scaleY':tr((16.7,1.13),(17.15,1.13),(18,0.91))}
  for b in g['children']:
   if b.get('type')!='group':continue
   texts=[q.get('text','') for q in b.get('children',[]) if q.get('type')=='text']
   st=''.join(texts)
   if st.startswith('Heads up'):
    b['children'][0]['width']=473
   elif st.startswith('3 similar'):
    b['children'][0]['width']=474
   elif st=='Yes plz':
    b['x']=497;b['children'][0]['width']=140
   elif st.startswith('It’s in your drafts'):
    b['y']=738;b['children'][0]['width']=480;b['start']=17.6;b['keyframes']={'opacity':tr((17.6,0),(17.8,1))}
# Native editable inbox list forms backdrop; opacity+blurreproduceobserveddepth.
rows=[]
senders=['Google Docs','Sarah Kim','Mike Johnson','Apple Mail','Emma Lee','Chris Wong','Anna Smith','James Brown','Microsoft Teams','Rachel White','Slack','David Green','Laura Black','Tom Clark']
subjects=['Discussion points for the next team meeting','Budget adjustments needed','Please review the document','By Friday','Team outing discussion','New project timeline','Feedback on design','Important deadline update','Budget meeting questions','Update from the team','Planning session','Upcoming product launch','Project next month','Meeting notes']
colors=['#b4bbe8','#e6a0ca','#e89879','#76d9a0','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8','#b4bbe8']
for i,(name,subject,col) in enumerate(zip(senders,subjects,colors)):
 yy=-110+i*91;rows +=[txt(name,65,yy+13,29,'#777777'),rect(420,yy,480,50,col,9,opacity=.7),txt(f'{i+1}: {subject}',430,yy+6,30,'#6e6e6e'),txt(f'—  {name} commented',1020,yy+9,35,'#777777'),txt('2:19 PM',1800,yy+17,25,'#aaaaaa')]
back={'id':ident('inbox'), 'type':'group','start':17.3,'end':18.5,'x':0,'y':0,'blur':2.5,'children':rows,'keyframes':{'opacity':tr((17.3,0),(17.75,.55),(18.2,.55),(18.5,0)),'y':tr((17.3,65),(18.5,-15))}}
idx=next(i for i,g in enumerate(s['layers']) if g.get('start')==16.7);s['layers'].insert(idx,back)
# Measuredportraitdrift21.5→22.1 (thecard'srestpositionisextractedat22.1).
face_dest={0:(710,136,1),1:(980,270,1),2:(527,400,.88),3:(1220,490,1.13),4:(773,588,.94),5:(623,725,.88),6:(1042,770,.97),7:(849,797,1)}
for g in s['layers']:
 cc=g.get('children',[])
 if len(cc)==1 and cc[0].get('type')=='image' and 'portrait-' in cc[0].get('src',''):
  ix=int(cc[0]['src'].split('portrait-')[-1].split('.')[0]);xx,yy,sc=face_dest[ix];kf=g.setdefault('keyframes',{})
  for prop,val in [('x',xx),('y',yy),('scaleX',sc),('scaleY',sc)]:
   prior=kf.get(prop,[{'t':21.5,'value':g.get(prop,1 if prop.startswith('scale') else 0)}]);settle=prior[-1]['value'];prior +=[{'t':21.5,'value':settle},{'t':22.1,'value':val,'ease':'easeOut'}];kf[prop]=prior
# Replaceerroneouslylowbirthdaynotification withsource-nativeglasscard attop.
s['layers']=[g for g in s['layers'] if g.get('start')!=22.1]
card=[rect(356,62,1208,260,'#ffffff',102,opacity=.93,stroke='#bfbfbf',strokeWidth=1.2),circ(401,111,160,'#ffffff',stroke='#dddddd',strokeWidth=5),img('assets/rene-mascot.png',429,139,106,118),img('../05-linq/assets/messages-icon.png',504,210,68,68),txt('Rene',592,121,54,'#000000',700),txt('now',1410,118,52,'#888888'),txt('Emma’s birthday is Saturday',592,193,54,'#000000'),img(gift,1225,201,58,58)]
s['layers'].append({'id':ident('birthday-card'),'type':'group','start':21.9,'end':22.9,'children':card,'keyframes':{'y':tr((21.9,-360),(22.1,0)),'opacity':tr((21.9,0),(22.02,1))}})
s['source']['notes']+=' Finalv8fixesCabintripgroupavatar/titlepill, measuredlandlordphonecamera/drafttimingwithnativeblurredinboxbackdrop, andbirthdaynotificationtoplayout/portraitdrift fromactualframes.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2));(d/'revision-v8.json').write_text(json.dumps({'changes_vs_v4_output_ranges':[[1.1,3.6],[16.7,18.5],[21.5,22.9],[28.2,31.8]],'changed_frame_ranges_inclusive':[[33,107],[501,554],[645,686],[846,953]],'evidence_frames':[3,17,18,21.5,22.1,29.4,29.7]},indent=2));print('Concretecontextscenesv8written')
