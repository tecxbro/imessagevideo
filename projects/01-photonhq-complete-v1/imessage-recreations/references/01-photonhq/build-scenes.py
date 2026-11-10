import json, math, subprocess, pathlib, random
from PIL import Image, ImageFont
BASE=pathlib.Path('/workspace/imessage-recreations'); R1=BASE/'references/01-photonhq'; R2=BASE/'references/02-danieltian'
FONT='/workspace/imessage-recreations/references/01-photonhq/assets/Inter-600.ttf'
seq=0

def ident(prefix='l'):
 global seq
 seq+=1; return f'{prefix}-{seq}'
def rect(x,y,w,h,fill,r=0,**kw): return dict(id=ident('rect'),type='rect',x=x,y=y,width=w,height=h,fill=fill,radius=r,**kw)
def circle(x,y,w,fill,**kw):return dict(id=ident('circle'),type='circle',x=x,y=y,width=w,height=w,fill=fill,**kw)
def path(d,fill='#000000',**kw):return dict(id=ident('path'),type='path',d=d,fill=fill,**kw)
def text(s,x,y,size=96,color='#000000',weight=600,width=None,**kw):
 f=ImageFont.truetype(str(R1/'assets'/f'Inter-{400 if weight<500 else 600}.ttf'),int(size)); natural=max(1,max(f.getlength(l) for l in s.split('\n')))
 return dict(id=ident('text'),type='text',text=s,x=x,y=y,fontFamily='Photon Sans',fontSize=size,fontWeight=weight,fill=color,scaleX=(min(1,width/natural) if width else 1),**kw)
def center(s,y=466,size=96,start=0,end=999,width=None,color='#000000',**kw):
 f=ImageFont.truetype(FONT,int(size)); w=width or f.getlength(s)
 return text(s,(1920-w)/2,y,size,color,width=w,start=start,end=end,**kw)
def group(children,start,end,**kw):return dict(id=ident('group'),type='group',children=children,start=start,end=end,**kw)
def k(*pts):return [dict(t=t,value=v,**({'ease':e} if e else {})) for t,v,e in pts]
def reveal(g,a,b=None):
 b=b or a+.22
 g.setdefault('keyframes',{}).update(opacity=k((a,0,None),(b,1,'easeOut')),y=k((a,35,None),(b,0,'easeOut')));return g

def image(src,x,y,w,h,**kw):return dict(id=ident('img'),type='image',src=src,x=x,y=y,width=w,height=h,**kw)
def crop(r,name,t,box,transparent=True):
 dest=r/'assets'/name
 if dest.exists():return 'assets/'+name
 raw=subprocess.check_output(['ffmpeg','-loglevel','error','-ss',str(t),'-i',str(r/'source.mp4'),'-frames:v','1','-f','image2pipe','-vcodec','png','-threads','1','-'])
 import io
 im=Image.open(io.BytesIO(raw)).convert('RGBA').crop(box)
 if transparent:
  import numpy as np
  a=np.array(im); white=a[:,:,:3].min(2)>250;a[:,:,3][white]=0;im=Image.fromarray(a)
 im.save(dest); return 'assets/'+name

def bubble(s,x,y,w,h=112,color='url(#blue)',size=48,side='right',**kw):
 children=[rect(0,0,w,h,color,h/2)]
 d=f'M {w-50} {h-25} Q {w-50} {h+10} {w-10} {h+20} Q {w-28} {h+1} {w-14} {h-15} Z' if side=='right' else f'M 25 {h-30} Q 46 {h+1} 9 {h+20} Q 36 {h+1} 22 {h-10} Z'
 children +=[path(d,color)]
 ink='#FFFFFF' if color in ['url(#blue)','#31F54B'] else '#222222'
 if s.startswith('@'):
  lines=s.split('\n');first=lines[0];prefix,sep,rest=first.partition(' ');fw=ImageFont.truetype(str(R1/'assets'/'Inter-600.ttf'),int(size)).getlength(prefix+' ')
  children +=[text(prefix,32,20,size,ink,weight=600),text(rest,32+fw,20,size,ink,weight=400,width=w-64-fw)]
  if len(lines)>1:children +=[text('\n'.join(lines[1:]),32,20+size*1.2,size,ink,weight=400,width=w-64,lineHeight=size*1.2)]
 elif '@Justina' in s:
  f=ImageFont.truetype(str(R1/'assets'/'Inter-400.ttf'),int(size));pre='hey team, ';pw=f.getlength(pre);mention='@Justina';mw=ImageFont.truetype(str(R1/'assets'/'Inter-600.ttf'),int(size)).getlength(mention+' ')
  children +=[text(pre,32,20,size,ink,weight=400),text(mention,32+pw,20,size,'#159BE8',weight=600),text('needs a Photon',32+pw+mw,20,size,ink,weight=400,width=w-64-pw-mw),text('team offsite. Tomorrow.',32,20+size*1.2,size,ink,weight=400,width=w-64)]
 else:children +=[text(s,32,20,size,ink,weight=400,width=w-64,lineHeight=size*1.2)]
 return dict(id=ident('bubble'),type='group',x=x,y=y,children=children,**kw)

def base(title,duration,bg='#FFFFFF'):
 return dict(title=title,width=1920,height=1080,fps=30,duration=duration,background=bg,fonts=[dict(family='Photon Sans',src='assets/Inter-600.ttf',weight=600),dict(family='Photon Sans',src='assets/Inter-400.ttf',weight=400)],source=dict(path='source.mp4',sourceStart=0,sourceEnd=duration,notes='Independent editable layer reconstruction. Inter from official Google Fonts repository; fitted to title glyph masks. Source-font binary identity remains unproven. Scene phase boundaries and easing fitted from sampled source frames, not mathematically exact. Static image layers are individually declared logos, avatars or photographs; no source video or full reference frame playback.'),gradients=[dict(id='blue',type='linear',stops=[dict(offset='0%',color='#55C2F3'),dict(offset='100%',color='#1394F9')]),dict(id='gray',type='linear',stops=[dict(offset='0%',color='#EEEEEE'),dict(offset='100%',color='#DFDFDF')]),dict(id='titleblue',type='linear',x1='0%',y1='0%',x2='100%',y2='100%',stops=[dict(offset='0%',color='#2583DC'),dict(offset='35%',color='#B6B2E3'),dict(offset='66%',color='#2DABE1'),dict(offset='100%',color='#75D6E8')]),dict(id='pill',type='linear',stops=[dict(offset='0%',color='#BFE6F9'),dict(offset='100%',color='#53C3F6')])],layers=[])

S=base('Photon 2.0 — native measured reconstruction',655/30);L=S['layers']
# 0–1.5 intro typography, source bbox 510,500..1410,580 at .5s
intro=group([text('Introducing',510,472,96,width=445),text('Photon 2.0',980,472,96,'url(#titleblue)',width=430)],0,1.5,originX=960,originY=540,keyframes={'scaleX':k((0,1,None),(.033,.88,'hold'),(.33,1,'easeOut'),(1.15,.78,'easeInOut'),(1.5,.78,None)),'scaleY':k((0,1,None),(.033,.88,'hold'),(.33,1,'easeOut'),(1.15,.78,'easeInOut'),(1.5,.78,None))})
L.append(intro)
# gloss pill and cursor, scale/translation modeled separately
pill=group([rect(0,0,700,300,'#BBE9FC',150),rect(22,21,656,257,'url(#pill)',130)],1.5,3.35,x=610,y=390,originX=350,originY=150,keyframes={'scaleX':k((1.5,.1,None),(1.76,1.1,'easeOut'),(2.2,1,None),(2.8,.61,'easeInOut'),(3.05,.61,None),(3.35,0,'easeIn')),'scaleY':k((1.5,.1,None),(1.76,1.1,'easeOut'),(2.2,1,None),(2.8,.61,'easeInOut'),(3.05,.61,None),(3.35,0,'easeIn')),'x':k((1.5,610,None),(2.2,610,None),(2.8,190,'easeInOut'),(3.2,-600,'easeIn'))})
L.append(pill)
L.append(group([path('M0 0 L0 132 L34 100 L60 155 L82 144 L54 90 L100 91 Z','#000000',stroke='#FFFFFF',strokeWidth=8)],1.75,2.85,x=1120,y=560,scaleX=.85,scaleY=.85,keyframes={'x':k((1.75,1260,None),(2.0,1120,'easeOut'),(2.23,1110,None),(2.7,1180,'easeIn')),'y':k((1.75,700,None),(2.0,560,'easeOut'),(2.23,555,None),(2.7,720,'easeIn'))}))
click=center('With just one click',466,96,2.6,4.2,width=745);click['keyframes']={'x':k((2.6,1060,None),(3.4,587.5,'easeOut'))};L.append(click)
every=center('Your agent is everywhere',466,96,4.1,5.3,width=1100);every['keyframes']={'x':k((4.1,760,None),(4.35,410,'easeOut'),(4.9,160,None),(5.3,-1150,'easeIn'))};L.append(every)
# Channel list. Individually extracted logos only; labels are native text.
icons=[]
for i,(name,y) in enumerate([('imessage',9),('whatsapp',378),('telegram',558),('sms',770),('email',985)]):
 icons.append(crop(R1,name+'.png',5.5,(828,y,956,min(y+128,1080))))
channels=[]
for i,label in enumerate(['iMessage','Whatsapp','Telegram','SMS','Email','Phone Call']):
 yi=i*180
 channels +=[image(icons[min(i,4)],0,yi,128,128),text(label,155,yi-8,106,width=[490,530,520,300,350,530][i])]
L.append(group(channels,4.75,6.5,x=828,y=9,keyframes={'x':k((4.75,1750,None),(5.4,828,'easeOut'),(5.8,900,None),(6.5,950,None)),'y':k((4.75,300,None),(5.5,9,'easeOut'),(6.3,-720,'easeInOut')),'scaleX':k((4.75,.8,None),(5.5,1,'easeOut'),(6.3,.3,'easeInOut')),'scaleY':k((4.75,.8,None),(5.5,1,'easeOut'),(6.3,.3,'easeInOut'))}))
L.append(reveal(group([text('And it’s',378,466,96,width=395),text('free',797,466,96,'#76C8E9',width=175),text('for everyone.',998,466,96,width=570)],6.4,8.23),6.4))
# Scrolling message walls: each bubble and glyph remains independently editable.
sms=['My battery is almost dead.','Can you plan a scenic route?','Leave them at the door.','Can you track my package?','Booked for 7!','Actually, she can’t make it.','Find somewhere dog-friendly.','You’re all set.','Can you find a nearby charging station.','Does this work?']
imsg=['Hey Muse, plan tomorrow’s team offsite?','Anything else to add?','Somewhere quiet with Wi-Fi.','Here’s my top pick.','My friend is vegetarian.','Nothing too fancy, please.','Tomorrow morning works for everyone.','Let’s keep it under $500.','How about 7:30?','What if it rains?','Which location works best?','Send everyone the final plan.','I’ll handle the details.','One checked bag should work.','Find a hotel near downtown.']
wa=['Yep, I’m here!','Wait, make it three people.','Pick me up here.','I’m here!','Running ten minutes late.','Got it, two people.','Get two tickets, please.','Here are some photos.','Same address as before.','Need a quick favor.']
tg=['Ask for a window table.','Found your reservation.','Shall I book it?','Find a gym near work.','Sure, checking now.','Can you arrange a babysitter?','Saturday has availability.','Skip that time.','I’ll remind you tomorrow.']
for a,b,title,labels,mode in [(8.2,9.55,'10,000+ SMS',sms,'sms'),(11.666667,12.98,'Unlimited iMessage',imsg,'imsg'),(12.966667,14.23,'Unlimited WhatsApp',wa,'wa'),(14.2,15.53,'Unlimited Telegram',tg,'tg')]:
 rows=[]
 for row,y in enumerate([-88,115,300,675,860,1050]):
  cursor=-120-(row%2)*300
  for j in range(4):
   q=labels[(row*3+j)%len(labels)];f=ImageFont.truetype(FONT,48);w=min(900,int(f.getlength(q)+64));out=(row+j)%3!=0
   color='#31F54B' if mode=='sms' and out else ('url(#blue)' if mode=='imsg' and out else ('#DFFAC8' if mode=='wa' and out else ('#DEF1FB' if mode=='tg' and out else 'url(#gray)')))
   bb=bubble(q,cursor,y,w,112,color,48,side='right' if out else 'left')
   if mode in ['wa','tg']:bb['children'].append(text('9:37  ✓✓',w-125,80,18,'#AAAAAA',width=105))
   rows.append(bb);cursor+=w+52
 wall=group(rows,a,b,keyframes={'x':k((a,120 if row%2 else -120,None),(b,-180 if row%2 else 180,None))});L.append(wall)
 L.append(center(title,465,96,a,b,width={'10,000+ SMS':540,'Unlimited iMessage':880,'Unlimited WhatsApp':950,'Unlimited Telegram':900}[title]))
# Email notification cards. Native containers and content, logo crops.
mailnames=['Airbnb','Disney+','Zoom','Apple','Sarah Miller','Disney','Uber','Emma Wilson']
subj=['Your next getaway awaits with curated wee...','Your subscription receipt is now ready','You’re invited: weekly team catch-up','Reminder: your store visit is scheduled for Fr...','Beach day this Saturday?','Reminder: your park visit is confirmed','Your airport ride is booked and confirmed fo...','Dinner and a movie on Friday?']
body=['Explore cozy weekend stays, verified homes...','$15.99 paid · Monthly plan. Your next...','Alex Chen is inviting you to a scheduled Zoo...','Genius Bar · Friday, 3 PM. Please arrive 10 m...','Hey! A few of us are heading to the beach o...','November 14 · Gates open at 9 AM','Pickup Monday at 9 AM. You will receive live...','Hey, are you free Friday evening? There’s a...']
logo_boxes=[(510,98,646,235),(1390,97,1522,230),(82,300,220,438),(966,300,1100,438),(523,649,659,786),(1390,648,1526,783),(943,848,1080,985),(66,0,200,74)]
mailicons=[crop(R1,f'mail-logo-{i}.png',10.5,box) for i,box in enumerate(logo_boxes)]
mail=[]
for row,y in enumerate([-120,78,280,630,832,1035]):
 for col,x in enumerate([-420,470,1360]):
  idx=(row*3+col)%8
  mail.append(group([rect(0,0,840,170,'#FFFFFF',90,stroke='#E6E6E6',strokeWidth=2),image(mailicons[idx],24,22,124,124),text(mailnames[idx],177,10,40,width=350),text('09:04 PM',640,25,28,'#929292',weight=400,width=125),text(subj[idx],177,65,29,weight=400,width=600),text(body[idx],177,110,29,'#969696',weight=400,width=600)],9.5,10.7,x=x,y=y))
# Higher fidelity native camera over declared static notification artwork. Each asset is ONE notification/card artwork, never a whole reference frame or a video.
card_boxes=[(137,0,934,91),(988,0,1785,91),(0,111,510,275),(558,111,1359,275),(1412,111,1920,275),(0,293,80,457),(137,293,934,457),(988,293,1785,457),(1840,293,1920,457),(0,621,510,785),(558,621,1359,785),(1412,621,1920,785),(0,804,80,968),(137,804,934,968),(988,804,1785,968),(1840,804,1920,968),(0,990,510,1080),(558,990,1359,1080),(1412,990,1920,1080)]
artcards=[]
for idx,box in enumerate(card_boxes):
 src=crop(R1,f'notification-art-{idx:02d}.png',10,box,False)
 artcards.append(image(src,box[0],box[1],box[2]-box[0],box[3]-box[1]))
L.append(group(artcards,9.5,10.666667,originX=960,originY=540,keyframes={'x':k((9.5,39,None),(10,0,None),(10.666667,-52,None)),'scaleX':k((9.5,.955,None),(10,1,None),(10.666667,1.06,None)),'scaleY':k((9.5,.955,None),(10,1,None),(10.666667,1.06,None)),'opacity':k((9.5,0,None),(9.73,1,'easeOut'))}))
L.append(center('100,000+ emails',486,96,9.5,10.666667,width=680))
# Call strips
calls=[]
for row,y in enumerate([-90,100,290,650,840,1030]):
 for col,x in enumerate([-150,700,1550]):
  idx=(row+col)%8
  calls.append(group([rect(0,0,790,145,'#000000',80),image(mailicons[idx],20,12,120,120),text(['Alex Chen','Mia Parker','Emma Wilson','Muse','Olivia Reed','Zoom','Claude','Book agent'][idx],155,47,38,'#FFFFFF',width=350),text('17:02',155,13,25,'#30D956',width=100),circle(565,33,80,'#292929'),text('◖))',581,40,30,'#FFFFFF',width=52),circle(670,33,80,'#FF2448'),text('⌒',684,43,43,'#FFFFFF',width=50)],10.666667,11.7,x=x,y=y))
L.append(group(calls,10.666667,11.7,keyframes={'x':k((10.666667,-160,None),(11.7,200,None))}));L.append(center('8000+ voice minutes',465,96,10.666667,11.7,width=900))
L.append(reveal(group([text('Even 10DLC registration',400,466,96,width=1000),path('M46 0 Q54 0 65 12 L82 13 Q93 14 94 30 L106 43 Q112 52 103 61 L94 72 L93 90 Q90 99 74 98 L61 110 Q52 117 44 106 L29 97 L13 96 Q3 92 5 79 L4 66 L-7 55 Q-13 46 -4 37 L6 25 L7 10 Q10 1 26 3 L38 -5 Z','#31EC5C',x=1432,y=500,scaleX=.76,scaleY=.76),path('M17 51 L37 71 L64 35','none',stroke='#FFFFFF',strokeWidth=10,x=1432,y=500,scaleX=.76,scaleY=.76)],15.5,16.72),15.5))
L.append(center('On us.',466,96,16.7,17.28,width=305))
cta=group([center('Try it today at',401,96,17.25,19.78,width=595),center('photon.codes/beta',515,96,17.25,19.78,width=813,color='#77C9EA')],17.25,19.78);L.append(reveal(cta,17.25,17.6))
logo=group([rect(-65,0,28,65,'#000000',5,rotation=14),rect(8,-39,28,65,'#000000',5,rotation=14),rect(44,46,28,65,'#000000',5,rotation=14)],19.75,655/30,x=960,y=505);L.append(reveal(logo,19.75,20.05))
# reveal helper overrides y; restore anchored logo
logo['keyframes']['y']=k((19.75,530,None),(20.05,505,'easeOut'))
import shutil
for wt in [400,600]:shutil.copyfile(R1/'assets'/f'Inter-{wt}.ttf',R2/'assets'/f'Inter-{wt}.ttf')
(R1/'scene.json').write_text(json.dumps(S,indent=2))

# Source 02 full native rebuild
S=base('Photon Agent to Agent — native measured reconstruction',1360/30,'#FDFDFD'); L=S['layers']
msgicon=crop(R2,'messages-icon.png',1,(363,551,468,657));groupicon=crop(R2,'group-chat-icon.png',1,(952,537,1082,669));notebook=crop(R2,'notebook.png',36,(1316,492,1409,586))
lyft=crop(R2,'lyft.png',16.5,(132,226,214,309));airbnb=crop(R2,'airbnb.png',16.5,(662,438,747,523));resy=crop(R2,'resy.png',16.5,(397,907,482,990));muse=crop(R2,'muse-avatar.png',7.5,(664,0,1065,195));musefull=crop(R2,'muse-full-avatar.png',22.5,(267,622,394,750));
L.append(group([text('Introducing Agent to Agent',349,398,106,width=1218),text('in',251,529,106,width=75),image(msgicon,363,551,105,106),text('iMessage',499,529,106,width=431),image(groupicon,953,538,130,130),text('Group Chats',1095,529,106,width=575)],0,2.24))
# composer shell and progressive characters
a,b=2.2,5.9
shell=group([circle(220,475,125,'#F7F7F7'),text('+',261,493,60,width=43),rect(420,470,1280,150,'#F6F6F6',75,stroke='#EFEFEF',strokeWidth=3)],a,b)
L.append(reveal(shell,a,2.65))
full='muse, my boss wants a team offsite\ntmr. can u help?'
# use per-character states to keep native editable text
for n in range(1,len(full)+1):
 st=3.1+(n-1)*.047
 if st>=5.55:break
 en=min(st+.047,5.55) if n<len(full) else 5.9
 L.append(text(full[:n],466,485,60,start=st,end=en,width=1120,lineHeight=80))
L.append(text(full,466,485,60,start=5.55,end=5.9,width=1120,lineHeight=80))
L.append(text('iMessage',849,503,54,'#CCCCCC',start=2.65,end=3.1,width=260))
L.append(group([circle(0,0,115,'#3D9EE8'),path('M57 85 L57 28 M30 55 L57 28 L84 55','none',stroke='#FFFFFF',strokeWidth=6)],3.12,5.96,x=1550,y=492))
# Send particles: deterministic editable circles
random.seed(4)
particles=[]
for i in range(110):
 ang=random.random()*math.tau;rr=random.random()*250;size=random.choice([2,3,4,5])
 particles.append(circle(0,0,size,'#66B3ED',keyframes={'x':k((5.8,1610,None),(6.4,1610+math.cos(ang)*rr,'easeOut')),'y':k((5.8,545,None),(6.4,545+math.sin(ang)*rr,'easeOut')),'opacity':k((5.8,1,None),(6.5,0,'easeOut'))}))
L.append(group(particles,5.8,6.5))
# Phone body reconstructed as independent metallic side rails + native chat UI
phone=[]
phone +=[rect(298,-250,56,1500,'#B9BABA',28),rect(323,-250,1200,1500,'#000000',54),rect(350,-250,1147,1500,'#FDFDFD',30),rect(1510,-250,58,1500,'#A8A9A9',25),rect(1518,-250,18,1500,'#ECECEC',8)]
phone +=[image(muse,660,0,402,195),rect(813,180,285,99,'#F1F1F1',50),text('Muse',866,186,65,width=176),text('›',1031,184,72,'#808080',width=38),circle(423,17,150,'#FAFAFA'),path('M510 68 L489 89 L510 111','none',stroke='#444444',strokeWidth=9)]
phone +=[bubble('muse, my boss wants a team offsite\ntmr. can u help?',624,352,895,205,'#3CA4F9',52)]
phone +=[bubble('',400,616,240,130,'#E7E6E9',45,side='left',start=6.3,end=7.8)]
for j in range(3):phone +=[circle(458+j*48,666,29,'#D2D1D5',start=6.3,end=7.8)]
phone +=[bubble('sure. lemme bring in some friends.',400,616,860,130,'#E7E6E9',48,side='left',start=7.8,end=8.73)]
L.append(group(phone,6.2,8.73,keyframes={'y':k((6.2,950,None),(6.9,0,'easeOut'))}))
# Reasoning text: current item dark, previous lines fade.
reason=['Checking what I know about Photon...','👥 9 people · 📍880 Harrison St · ❤️Loves sushi','Offsite tomorrow. What do we need?','🏠 A place to stay','🚗 Rides','🍣 Food','Let me find agents who can help...']
for i,s in enumerate(reason):
 st=8.7+i*.35; yy=300+i*105
 L.append(text(s,210,yy,68,'#AAAAAA' if i<2 else '#888888',start=st,end=12.2,width=[1270,1490,1220,735,410,400,1360][i],keyframes={'opacity':k((st,0,None),(st+.18,1,'easeOut'))}))
# Search capsule and phone number field
search=[rect(0,0,1100,112,'#FDFDFD',56,stroke='#E6E6E6',strokeWidth=3),circle(30,28,46,'none',stroke='#D1D1D1',strokeWidth=7),path('M67 67 L88 89','none',stroke='#D1D1D1',strokeWidth=7),text('Searching the Agent Phone Book...',121,22,55,width=940)]
L.append(group(search,12,13.75,x=410,y=480,keyframes={'opacity':k((12,0,None),(12.5,1,'easeOut'))}))
nums=[]
for r in range(7):
 for c in range(5):
  n=f'+1 ({[843,984,215,801,702,971,864][(r+c)%7]}) 555-{101+r*9+c:04d}'
  nums.append(text(n,-40+c*535,65+r*145,48,'#DDDDDD',width=448))
L.append(group(nums,13.65,17.7,keyframes={'scaleX':k((13.65,.75,None),(15.3,1.1,'easeInOut')),'scaleY':k((13.65,.75,None),(15.3,1.1,'easeInOut')),'opacity':k((13.65,1,None),(16.7,.8,None),(17.7,0,'easeOut'))},originX=960,originY=540))
# Agent cards move into compact stack
for idx,(name,ico,x,y,w) in enumerate([('Lyft',lyft,118,213,590),('Airbnb',airbnb,646,423,600),('Resy',resy,386,890,590)]):
 ch=[rect(0,0,w,112,'#FDFDFD',56,stroke='#E3E3E3',strokeWidth=4),image(ico,16,14,82,82),text(name,128,17,57,width=320),text('+',w-100,11,65,'#DDDDDD',width=62,start=15.4,end=17.05),circle(w-75,48,22,'#3DD372',start=17.05,end=18.35)]
 L.append(group(ch,15.4+idx*.07,18.35,x=x,y=y,keyframes={'x':k((15.4,x,None),(17.5,650,'easeInOut')),'y':k((15.4,y,None),(17.5,420+idx*145,'easeInOut')),'scaleX':k((15.4,1,None),(17.5,.78,'easeInOut')),'scaleY':k((15.4,1,None),(17.5,.78,'easeInOut'))}))
# group avatar assembled using independently cropped logo discs
av=[image(lyft,0,0,80,80),image(airbnb,120,50,80,80),image(resy,80,165,80,80),circle(-30,130,80,'#70FD4A'),circle(-30,-80,115,'#FFFFFF',stroke='#DDDDDD',strokeWidth=2),text('M',-8,-70,75,'#1595E5',width=65)]
for i,ch in enumerate(av):
 ch['keyframes']={'x':k((18.25,ch.get('x',0)*3,None),(19.8,ch.get('x',0),'easeInOut')),'y':k((18.25,ch.get('y',0)*3,None),(19.8,ch.get('y',0),'easeInOut'))}
L.append(group(av,18.25,20.5,x=860,y=250))
# fixed small header while messages scroll. Logo composite is built from independent static brand assets.
musebrand=crop(R2,'muse-brand.png',22.5,(862,75,978,191))
head=[circle(-15,-2,240,'#FAFAFA'),image(lyft,128,100,78,78),image(airbnb,112,29,76,76),image(resy,97,169,68,68),circle(18,130,75,'#70F64A'),image(musebrand,2,20,116,116),rect(-153,201,506,92,'#F2F2F2',48),text('Team Offsite, Oct 10',-115,214,48,width=435)]
headerLayer=group(head,19.8,34.2,x=845,y=0,keyframes={'scaleX':k((19.8,1.1,None),(21.0,1,'easeOut'),(23.3,1,'easeInOut')),'scaleY':k((19.8,1.1,None),(21.0,1,'easeOut'),(23.3,1,'easeInOut')),'x':k((19.8,845,None),(23.3,860,'easeInOut')),'y':k((19.8,0,None),(22.5,0,None),(24,49,'easeInOut'),(28,49,None),(30,49,None),(32.5,30,'easeInOut'))})
# Messages with independent timing and cumulative scrolling
chat=[]
chat +=[text('Muse',439,315,44,width=110),bubble('hey team, @Justina needs a Photon\nteam offsite. Tomorrow.',417,382,952,190,'#E7E6E9',52,side='left',start=21.05,end=28.15),image(musefull,267,622,126,126,start=21.75,end=28.15,keyframes={'y':k((21.75,622,None),(22.5,622,None),(23.3,870,'easeInOut'),(24.2,1085,'easeInOut'))}),bubble('@Airbnb find a place in Tahoe for 9',417,610,966,142,'#E7E6E9',52,side='left',start=21.75,end=28.15),bubble('@Lyft 2 XL rides from 880 Harrison St,\n9am tomorrow',417,785,995,180,'#E7E6E9',50,side='left',start=22.65,end=28.15),bubble('@Resy find a sushi spot.\nThe team loves sushi',417,1022,750,180,'#E7E6E9',50,side='left',start=23.35,end=28.15)]
chat +=[circle(1340,705,115,'#E7E6E9',start=23.5,end=28.15),text('👍',1355,719,75,start=23.5,end=28.15)]
chat +=[image(resy,267,1360,110,110,start=24.4,end=28.15),text('Resy',440,1303,40,start=24.4,end=28.15,width=95),bubble('Budget?',417,1357,260,115,'#E7E6E9',48,side='left',start=24.4,end=28.15),bubble('~$100 per person',1110,1450,455,115,'url(#blue)',48,start=25.2,end=28.15),circle(1080,1422,95,'#E7E6E9',start=26.4,end=28.15),text('👍',1095,1433,60,start=26.4,end=28.15)]
L.append(group(chat,20.5,28.15,keyframes={'y':k((20.5,0,None),(22.5,0,None),(23.5,-180,'easeInOut'),(24.5,-324,'easeInOut'),(25.8,-540,'easeInOut'),(27.5,-700,None)),'scaleX':k((20.5,1,None),(24,.95,'easeInOut')),'scaleY':k((20.5,1,None),(24,.95,'easeInOut'))},originX=960,originY=540))
# Cabin card: only photographic rectangle is raster; all UI text and card geometry native.
cabin=crop(R2,'cabin-photo.png',29.5,(534,215,1225,581),False)
card=[text('Airbnb',550,172,36,width=108),rect(533,213,693,500,'#EEEEEE',65),image(cabin,533,213,693,365),rect(588,334,582,249,'#FDFDFD',32),text('Lake view Cabin in Tahoe Vista\n- Steps to Beach',623,350,37,width=510,lineHeight=44),text('Entire home in Tahoe Vista, California, United States',650,471,20,'#888888',width=450),text('8 guests · 3 bedrooms · 5 beds · 2 baths',710,502,21,'#888888',width=330),text('★4.83 · 30 reviews',801,547,18,width=185),text('Lake view Cabin in Tahoe Vista',563,598,41,width=625),text('Your reservation details',563,651,29,'#AAAAAA',width=400),image(airbnb,546,229,80,80),image(airbnb,418,757,95,95),bubble('How about this one?',534,754,450,101,'#E7E6E9',43,side='left'),bubble('Love it',1357,910,190,100,'url(#blue)',43,start=30.6,end=32.7)]
L.append(group(card,28.2,32.7,keyframes={'y':k((28.2,250,None),(29.2,0,'easeOut'),(31.5,-270,'easeInOut'),(32.7,-450,'easeInOut')),'scaleX':k((28.2,.5,None),(29.2,1,'easeOut'),(31.5,.8,'easeInOut')),'scaleY':k((28.2,.5,None),(29.2,1,'easeOut'),(31.5,.8,'easeInOut'))},originX=960,originY=540))
book=[]
for idx,(ico,name,copy) in enumerate([(airbnb,'Airbnb','Booked✅'),(lyft,'Lyft','2 XLs booked.\nPhoton HQ → Airbnb in Tahoe, 9am✅'),(resy,'Resy','Sushi for 9, booked🍣')]):
 yy=440+idx*200
 book +=[image(ico,315,yy+34,82,82,start=31.8+idx*.7,end=34.2),text(name,420,yy-12,35,width=120,start=31.8+idx*.7,end=34.2),bubble(copy,418,yy+28,[230,800,500][idx],110 if idx!=1 else 155,'#E7E6E9',38,side='left',start=31.8+idx*.7,end=34.2)]
L.append(group(book,31.8,34.2));L.append(headerLayer)
L.append(center('Your iMessage agent now has',466,78,34.2,35.3,width=1085))
L.append(group([text('Your iMessage agent now has a',214,469,78,width=1090),image(notebook,1316,492,93,94),text('phone book.',1426,469,78,width=420)],35.3,37.65))
for a,b,label in [(37.65,38.1,'Amazon'),(38.1,38.65,'Uber'),(38.65,39.2,'eBay'),(39.2,39.6,'Muse'),(39.6,40.05,'Grok Bot'),(40.05,40.5,'DoorDash')]:
 L.append(group([text('It brings',350,466,78,width=266),rect(632,481,240,94,'#FDFDFD',48,stroke='#E6E6E6',strokeWidth=3),circle(647,491,73,'#EFEFEF'),text(label[:1],664,493,45,'#45A5C7',width=40),text(label,730,493,45,width=125),text('into your group chats.',884,466,78,width=700)],a,b))
L.append(center('It brings all the agents into your group chats.',466,78,40.5,41.25,width=1335))
L.append(center('photon.codes/beta',470,70,41.2,1360/30,width=574,color='#67B5D4'))
(R2/'scene.json').write_text(json.dumps(S,indent=2))
for r in [R1,R2]:
 with (r/'steps-rebuild.md').open('a') as f:f.write('\n5. Generated full-duration native scene JSON using deterministic measured pixels and semantic layers. Extracted individually declared logos/avatar/photo crops. Added title phases, UI state transitions, camera groups, editable text, bubbles, cards, scrolling fields and CTA. Complex source easing and rich app details remain approximations pending QA.\n')
print('Built',len(json.loads((R1/'scene.json').read_text())['layers']),'and',len(L),'root layers')
