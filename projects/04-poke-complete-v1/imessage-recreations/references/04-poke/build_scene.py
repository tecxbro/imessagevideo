"""Independent editable Poke motion reconstruction from measured native frame anchors.
No source-video or full-frame raster layers are used. See assets/provenance.json.
"""
from pathlib import Path
import json,copy,math
P=Path(__file__).parent
fps=30000/1001
D=1283/fps
L=[]; uid=0
FONT='Arial, sans-serif'
fontfiles=[]
for fn,family,weight in [('SF-Pro-Display-Regular.otf','SF Pro Display',400),('SF-Pro-Display-Medium.otf','SF Pro Display',500),('SF-Pro-Display-Semibold.otf','SF Pro Display',600),('SF-Pro-Display-Bold.otf','SF Pro Display',700)]:
 if (P/'assets'/fn).exists():fontfiles.append({'family':family,'src':'assets/'+fn,'weight':weight});FONT='SF Pro Display'

for style,weight in [('Regular',400),('Semibold',600),('Bold',700)]:
 if (P/'assets'/f'SF-Pro-Text-{style}.otf').exists():fontfiles.append({'family':'SF Pro Text','src':f'assets/SF-Pro-Text-{style}.otf','weight':weight})

def node(typ,**kw):
 global uid
 uid+=1;return dict(type=typ,id=f'p{uid:04}',**kw)
def rect(x,y,w,h,fill='#ffffff',r=0,**kw):return node('rect',x=x,y=y,width=w,height=h,fill=fill,radius=r,**kw)
def text(x,y,s,size=48,fill='#000000',weight=400,family=None,**kw):return node('text',x=x,y=y,text=s,fontSize=size,fill=fill,fontFamily=(family or ('SF Pro Text' if weight<600 and FONT!='Arial, sans-serif' else FONT)),fontWeight=weight,**kw)
def path(d,fill='#000000',**kw):return node('path',d=d,fill=fill,**kw)
def img(name,x,y,w,h,**kw):return node('image',src='assets/'+name+'.png',x=x,y=y,width=w,height=h,**kw)
def grp(children,x=0,y=0,**kw):return node('group',children=children,x=x,y=y,**kw)
def k(pairs,ease='easeInOut'):return [dict(t=t,value=v,**({'ease':ease} if i else {})) for i,(t,v) in enumerate(pairs)]
def anim(layer,**tracks):layer['keyframes']={a:k(b) for a,b in tracks.items()};return layer
def put(layer,start,end):layer['start']=start;layer['end']=end;L.append(layer);return layer
def fade(layer,start,end,span=.22):
 layer.setdefault('keyframes',{})['opacity']=k([(start,0),(start+span,1),(end-span,1),(end,0)])
 return layer

def bubble(x,y,w,h,s='',fs=60,fill='#ececec',right=False,fg='#000000',tail=True,padx=42,pady=34):
 c=[rect(0,0,w,h,fill,min(h/2,76))]
 if tail:
  if right:c.append(path(f'M {w-102} {h-22} Q {w-37} {h-4} {w-42} {h+27} Q {w-76} {h+30} {w-126} {h-4} Z',fill))
  else:c.append(path(f'M 28 {h-45} Q 75 {h-5} 35 {h+24} Q 88 {h+24} 118 {h-13} Z',fill))
 if s:c.append(text(padx,pady,s,fs,fg))
 return grp(c,x,y)
def checkrow(x,y,label,fs=36):
 return grp([rect(0,0,112,74,'#ffffff',37,stroke='#9c9c9c',strokeWidth=4),path('M 34 36 L 48 51 L 74 18','none',stroke='#9c9c9c',strokeWidth=6),text(142,16,label,fs,'#999999',600)],x,y)

def phone(w=1000,h=2160):
 # Editable device hardware, including chrome ribs, bezel, island, controls.
 c=[rect(0,0,w,h,'#676969',158),rect(5,4,w-10,h-8,'url(#chrome)',155),rect(13,10,w-26,h-20,'#1d1d1e',148),rect(25,23,w-50,h-46,'#090909',139),rect(36,36,w-72,h-72,'#ffffff',128)]
 for x in [-6,w-1]:
  for y,hh in [(430,102),(600,150),(820,150)]:c.append(rect(x,y,8,hh,'url(#chrome)',5))
 c += [rect(w/2-142,68,284,82,'#000000',41),node('circle',x=w/2+93,y=94,width=22,height=22,fill='#151719'),text(148,90,'9:43',42,weight=600),rect(w-170,96,48,26,'#000000',6),rect(w-174,92,56,34,'none',7,stroke='#999999',strokeWidth=2),rect(w-115,104,4,10,'#999999',2)]
 for i in range(4):c.append(rect(w-294+i*12,123-(i+1)*8,8,(i+1)*8,'#000000',2))
 c += [path(f'M {w-231} 111 Q {w-208} 89 {w-185} 111','none',stroke='#000000',strokeWidth=5),path(f'M {w-224} 119 Q {w-208} 105 {w-193} 119','none',stroke='#000000',strokeWidth=5),node('circle',x=w-212,y=123,width=9,height=9,fill='#000000')]
 c.append(img('phone-upper-ring',0,0,1000,1046.51))
 return grp(c)

def edge(x=38,w=1380):
 c=[rect(x,-300,30,1800,'url(#chrome)',6),rect(x+30,-300,24,1800,'#000000'),rect(x+54,-300,w-108,1800,'#ffffff'),rect(x+w-54,-300,24,1800,'#000000'),rect(x+w-30,-300,30,1800,'url(#chrome)',6)]
 for yy in [50,380,720]:c.append(rect(x-7,yy,10,180,'url(#chrome)',5))
 return grp(c)

def composer(x,y,w,fs=60):
 c=[rect(0,0,110,145,'#ffffff',55,shadow={'x':0,'y':8,'blur':30,'color':'#f3f3f3'}),rect(138,0,w-138,145,'#fdfdfd',70,shadow={'x':0,'y':8,'blur':30,'color':'#f3f3f3'}),rect(38,50,58,9,'#000000',4),rect(62,26,9,58,'#000000',4),text(212,18,'Message Poke',fs,'#c7c7c7',family='SF Pro Display')]
 c += [rect(w-98,27,20,44,'none',10,stroke='#d5d5d5',strokeWidth=5),path(f'M {w-108} 52 L {w-108} 63 Q {w-108} 87 {w-88} 87 Q {w-67} 87 {w-67} 63 L {w-67} 52','none',stroke='#d5d5d5',strokeWidth=5),rect(w-91,87,5,18,'#d5d5d5'),rect(w-107,104,38,5,'#d5d5d5',2)]
 return grp(c,x,y)
def keyboard(x,y,w):
 c=[rect(0,0,w,750,'#dedee3',80),text(w/2,45,'➤ Current Location',58,textAnchor='middle',start=15.4,end=17.7)]
 rows=['qwertyuiop','asdfghjkl','zxcvbnm'];pitch=w/10;kw=pitch-19
 for row,s in enumerate(rows):
  offset=(w-len(s)*pitch)/2
  for col,ch in enumerate(s):
   xx=offset+col*pitch+10;yy=178+row*192
   c += [rect(xx,yy,kw,158,'#ffffff',28),text(xx+kw/2,yy+16,ch,98,'#555555',textAnchor='middle')]
 return grp(c,x,y)

# ----- 0–4.4: favorite-avatar camera and Messages inbox -----
poster=grp([img('poke-square',460,220,522,524),text(686,778,'Poke',72,'#858585',textAnchor='middle'),img('verified',783,788,57,58)]);put(poster,0,.067)
for name,x,y,side in [('braden',192,398,-1),('sydney',976,430,1)]:
 g=grp([img(name,-137,-137,274,274),text(0,151,name.title(),46,'#858585',textAnchor='middle')],x+137,y+137)
 anim(g,x=[(.067,x+137),(.6,x+137),(1.1,x+137),(2,-20 if side<0 else 1465),(3.2,-20 if side<0 else 1465),(3.8,435 if side<0 else 1000),(4.3,435 if side<0 else 1000)],y=[(.067,y+137),(.5,y+137),(1.1,y+137),(2,410),(3.2,410),(3.8,482),(4.3,482)],scaleX=[(.067,1),(.5,1),(1.1,1),(2,1.73),(3.2,1.73),(3.8,.69),(4.3,.69)],scaleY=[(.067,1),(.5,1),(1.1,1),(2,1.73),(3.2,1.73),(3.8,.69),(4.3,.69)],opacity=[(.067,0),(.3,1),(1.15,1),(1.9,.16),(3.3,.16),(3.85,1),(4.3,1)])
 put(g,.067,4.35)
for name,st,en,opa in [('poke-circle',.067,2.65,[(.067,0),(.3,1),(2.1,1),(2.65,0)]),('poke-square',2.15,4.35,[(2.15,0),(2.65,1),(4.35,1)])]:
 g=grp([img(name,-238,-238,476,476)],720,410)
 anim(g,x=[(.067,720),(3.25,720),(3.95,720)],y=[(.067,570),(.5,570),(1.05,570),(2,405),(3.25,405),(3.95,482)],scaleX=[(.067,.48),(.5,.52),(1.1,.52),(2,1),(3.25,1),(3.95,.40)],scaleY=[(.067,.48),(.5,.52),(1.1,.52),(2,1),(3.25,1),(3.95,.40)],opacity=opa)
 put(g,st,en)
label=text(720,703,'Poke',70,'#858585',textAnchor='middle')
anim(label,y=[(.067,703),(1.1,703),(2,668),(3.2,668),(3.95,590)],fontSize=[(.067,46),(1.1,46),(2,72),(3.2,72),(3.95,34)],opacity=[(.067,0),(.35,1),(4.35,1)])
put(label,.067,4.35)
badge=img('verified',823,682,57,58);anim(badge,x=[(2.5,823),(3.2,823),(3.95,766)],y=[(2.5,682),(3.2,682),(3.95,594)],scaleX=[(2.5,1),(3.2,1),(3.95,.47)],scaleY=[(2.5,1),(3.2,1),(3.95,.47)],opacity=[(2.5,0),(2.75,1),(4.35,1)]);put(badge,2.5,4.35)
# Inbox hardware appears behind avatar layer during pullback. Ordered before avatars below.
inbox=[]
inbox += [phone(),text(500,205,'Messages',45,weight=600,textAnchor='middle'),text(112,205,'Edit',38)]
inbox += [text(215,631,'Nikki Freeman',45,weight=600),text(215,688,'hey when are you coming home 😳',42,'#858585'),text(745,634,'1:50 AM',40,'#999999'),rect(220,815,690,2,'#e6e6e6'),text(215,844,'Jony',45,weight=600),text(215,901,"ngl i should’ve been sober when\ndesigning that car",42,'#858585',lineHeight=49),text(745,844,'12:15 AM',40,'#999999')]
inbox += [img('braden',97,643,92,92),img('sydney',97,855,92,92)]
p=grp(inbox,250,90,start=3.35,end=4.45)
anim(p,scaleX=[(3.35,1.4),(3.95,.94),(4.45,.90)],scaleY=[(3.35,1.4),(3.95,.94),(4.45,.90)],x=[(3.35,15),(3.95,250),(4.45,270)],y=[(3.35,-190),(3.95,90),(4.45,110)],opacity=[(3.35,0),(3.7,1),(4.3,1),(4.45,0)])
# hardware sits behind the independently animated avatars
L.insert(1,p)
preview=bubble(568,370,307,112,'sarah wants to\ngrab dinner tmrw',33,fill='#fbfbfb',right=True,padx=43,pady=18)
fade(preview,3.65,4.5,.12);put(preview,3.65,4.5)
# Faded inbox suggestions below favorite row while zoomed in
faint=grp([text(45,916,'Nikki Freeman',92,'#cfcfcf',600),text(1250,930,'1:50',86,'#e4e4e4'),text(45,1035,'hey when are you coming home',82,'#ececec')]);fade(faint,1.1,3.4,.3);put(faint,1.1,3.4)
# ----- 4.45–8.75: message and native calendar sheet -----
intro=bubble(126,485,1188,172,'sarah wants to grab dinner tmrw',72,padx=50,pady=36)
intro['children'].append(rect(740,120,398,3,'#9c9c9c'))
anim(intro,scaleX=[(4.45,.45),(4.9,1),(5.6,1)],scaleY=[(4.45,.45),(4.9,1),(5.6,1)],x=[(4.45,450),(4.9,126)],y=[(4.45,420),(4.9,485)])
put(intro,4.45,8.78)
scrim=rect(0,0,1440,1080,'#000000');anim(scrim,opacity=[(5.65,0),(5.95,.25),(8.55,.25),(8.78,0)]);put(scrim,5.65,8.78)
sheet=[rect(0,0,1064,1700,'#ffffff',108),rect(483,12,100,13,'#bebec1',7),text(50,95,'Dinner with Sarah',56,weight=700),text(50,168,'Pick a Time',36,'#999999',family='SF Pro Display'),rect(0,252,1064,2,'#ededed')]
def day(y,label,times,selected=None):
 out=[text(50,y,label,58,weight=600),text(1014,y+8,'Show Less',34,'#1598e8',textAnchor='end',family='SF Pro Display')]
 for j,ss in enumerate(times):
  w=298 if len(times)==3 else 324;xx=50+j*(w+32);out += [rect(xx,y+92,w,102,'#0a98ef' if ss==selected else '#ffffff',17,stroke='#1598e8',strokeWidth=2),text(xx+w/2,y+113,ss,46,'#ffffff' if ss==selected else '#1598e8',textAnchor='middle',family='SF Pro Display')]
 return out
sheet += day(300,'Thursday, June 4',['6:00 PM','6:45 PM','7:00 PM'])
sheet += [text(50,532,'There are 4 events scheduled, and the first one starts at\n3:00 PM',37,'#999999',lineHeight=41,family='SF Pro Display'),text(50,646,'View in Calendar...',38,'#1598e8',family='SF Pro Display'),rect(0,728,1064,2,'#ededed')]
sheet += day(785,'Friday, June 5',['7:30 PM','10:30 PM'])
selected=rect(50,877,324,102,'#0a98ef',17);selected['start']=7.8;sheet.append(selected)
selectedtxt=text(212,898,'7:30 PM',46,'#ffffff',textAnchor='middle',start=7.8,family='SF Pro Display');sheet.append(selectedtxt)
sheet += [rect(0,1028,1064,2,'#ededed')]+day(1085,'Saturday, June 6',['8:00 PM','9:15 PM'])
g=grp(sheet,188,222)
anim(g,y=[(5.68,1200),(6.1,560),(6.7,222),(7.1,222),(7.75,-374),(8.45,-374),(8.78,1200)],opacity=[(5.68,1),(8.6,1),(8.78,0)])
put(g,5.68,8.78)
# ----- 8.78–17.7: food choice conversation and keyboard -----
e=edge();put(e,8.78,15.65)
# First two message bubbles scroll by measured vertical anchors.
locked=bubble(257,353,528,180,'locked friday',72,padx=42,pady=36)
anim(locked,y=[(8.78,450),(9,353),(9.45,111),(10,111),(10.7,-200)])
put(locked,8.78,10.7)
mood=bubble(244,323,918,180,'what r u in the mood for?',72,padx=50,pady=36)
anim(mood,y=[(9.45,500),(9.85,323),(10.05,323),(10.85,-80),(12.3,-280)])
put(mood,9.45,12.3)
options=[]
for j,(s,ic) in enumerate([('Mexican','taco'),('Japanese','sushi'),('Italian','pasta'),('Indian','indian'),('Chinese','noodles'),('Surprise me','dice')]):
 options += [img(ic,50,50+j*108,58,55),text(125,40+j*108,s,60,'#1999ec')]
menu=bubble(227,105,606,685,tail=True)
menu['children'] += options
anim(menu,y=[(10.15,700),(10.65,255),(11.5,105),(12.05,105),(12.45,-700)],scaleX=[(10.15,1),(11.5,1),(12.05,1),(12.45,.8)],scaleY=[(10.15,1),(11.5,1),(12.05,1),(12.45,.8)])
put(menu,10.15,12.45)
# Dinner Choice selected confirmation
selection=bubble(360,177,958,208,tail=True,right=True,padx=0)
selection['children'] += [img('indian',50,59,58,55),text(110,43,'Indian',56,weight=600),text(50,113,'Selected option',52,'#777777',family='SF Pro Display')]
anim(selection,y=[(12.35,500),(12.8,177),(13.05,177),(14,54),(15, -30),(15.7,-400)])
put(selection,12.35,15.7)
choice=checkrow(177,54,'Dinner Choice',36);anim(choice,y=[(12.35,400),(12.8,54),(13.05,54),(14,-69)]);put(choice,12.35,14)
spot=bubble(190,498,707,140,'want me to find a spot?',60,padx=35,pady=27)
anim(spot,y=[(12.65,700),(13,498),(13.4,498),(14,368),(15,286),(15.65,-200)])
put(spot,12.65,15.65)
thumb=grp([node('circle',x=0,y=0,width=96,height=96,fill='#08a6ed'),node('circle',x=64,y=72,width=30,height=30,fill='#08a6ed'),node('circle',x=92,y=105,width=14,height=14,fill='#08a6ed'),img('thumb',25,15,54,53)],856,332)
anim(thumb,y=[(13.2,462),(14,332),(15,249)],scaleX=[(13.2,0),(13.35,1.15),(13.55,1),(15,1)],scaleY=[(13.2,0),(13.35,1.15),(13.55,1),(15,1)])
put(thumb,13.2,15.65)
where=bubble(197,553,533,145,'where are you rn?',60,padx=38,pady=28)
anim(where,x=[(13.55,197),(15,185),(16,116),(17,153),(18,239),(18.4,239)],y=[(13.55,760),(14,553),(15,460),(16,66),(17,97),(18,117),(18.4,-300)],scaleX=[(13.55,1),(15,1),(16,1.14),(17,1.02),(18,.74)],scaleY=[(13.55,1),(15,1),(16,1.14),(17,1.02),(18,.74)])
put(where,13.55,18.4)
comp=composer(125,750,1190,60)
anim(comp,x=[(11.5,160),(13,125),(14,125),(15,100),(16,42),(17,80)],y=[(11.5,1000),(13,750),(14,750),(15,690),(16,330),(17,975)],scaleX=[(11.5,1),(15,1),(16,1.14),(17,1)],scaleY=[(11.5,1),(15,1),(16,1.14),(17,1)])
put(comp,11.5,17.7)
kb=keyboard(94,940,1250)
anim(kb,x=[(12.3,94),(15,80),(16,0),(17,50)],y=[(12.3,940),(14,940),(15,885),(16,537),(17,1200)],scaleX=[(12.3,1),(15,1),(16,1.14),(17,1)],scaleY=[(12.3,1),(15,1),(16,1.14),(17,1)])
put(kb,12.3,17.7)
# ----- 17.7–23.5: Location and restaurant picker -----
mapc=bubble(604,274,554,700,right=True,fill='#e5e5e2')
mapc['children'] += [img('location-map',0,0,554,560),text(32,583,'Shared Location',40,weight=500),text(32,635,'Palo Alto, CA',34,'#777777')]
anim(mapc,y=[(17.65,1200),(18,274),(18.4,-220),(19.3,-220),(20.6,-500)],x=[(17.65,604),(18.4,604)],scaleX=[(17.65,.95),(18,1)],scaleY=[(17.65,.95),(18,1)])
put(mapc,17.65,20.6)
found=bubble(153,726,945,140,'found a few solid spots near you',60,padx=58,pady=27)
anim(found,y=[(18.25,1200),(18.85,722),(19.5,722),(20.3,900),(22.4,318),(23.3,318),(24,565)],x=[(18.25,153),(23.3,153),(24,445)],scaleX=[(18.25,.8),(18.85,.8),(22.4,1),(23.3,1),(24,.5)],scaleY=[(18.25,.8),(18.85,.8),(22.4,1),(23.3,1),(24,.5)])
found.setdefault('keyframes',{})['opacity']=k([(18.25,1),(19.25,1),(19.3,0),(22.2,0),(22.4,1),(24.5,1)]);put(found,18.25,24.5)
scrim=rect(0,0,1440,1080,'#000000');anim(scrim,opacity=[(19.3,0),(19.65,.25),(22.1,.25),(22.4,0)]);put(scrim,19.3,22.4)
r=[rect(0,0,940,1900,'#ffffff',100),rect(427,10,86,12,'#bdbdc1',6),text(64,78,'Anything catching your eye?',53,weight=700),rect(0,175,940,105,'#f4f3f6'),text(44,226,'ITALIAN NEAR YOU',32,'#999999')]
for i,(label,sub,photo) in enumerate([('Ettan','Italian / Wine · 0.03 mi','ettan-photo'),('Khazana','Indian Restaurant · 0.11 mi','khazana-photo'),("Zareen’s",'Indian and Pakistani · 0.16 mi','zareen-photo'),('Darbar','South Indian · 0.28 mi','darbar-photo')]):
 yy=320+i*255;r += [img(photo,44,yy,168,168),text(238,yy+39,label,38,weight=600),text(238,yy+94,sub,32,'#999999'),node('circle',x=839,y=yy+56,width=56,height=56,fill='#ffffff',stroke='#666666',strokeWidth=1)]
 if i==2:r += [node('circle',x=839,y=yy+56,width=56,height=56,fill='#0b9ae9',start=21.5),text(867,yy+62,'✓',37,'#ffffff',textAnchor='middle',start=21.5)]
g=grp(r,250,163)
anim(g,y=[(19.3,1200),(19.8,163),(20.25,163),(21,-405),(21.3,-405),(21.8,-231),(22.1,-231),(22.4,1200)])
put(g,19.3,22.4)
ck=checkrow(180,516,'anything catching your eye?',38);anim(ck,y=[(22.3,760),(22.7,516),(23.3,516),(24,663)],x=[(22.3,180),(23.3,180),(24,460)],scaleX=[(22.3,1),(23.3,1),(24,.5)],scaleY=[(22.3,1),(23.3,1),(24,.5)]);put(ck,22.3,24.7)
result=bubble(589,778,768,180,right=True,fill='#e4e4e7')
result['children'] += [img('zareen-card-photo',39,17,141,143),text(204,49,"Zareen’s",38,weight=600),text(204,93,"I’ll take it from here.",34,'#999999')]
anim(result,y=[(22.5,1100),(23,778),(23.35,778),(24,740),(24.7,315)],x=[(22.5,589),(23.35,589),(24,662),(24.7,662)],scaleX=[(22.5,1),(23.35,1),(24,.5),(24.7,.5)],scaleY=[(22.5,1),(23.35,1),(24,.5),(24.7,.5)])
put(result,22.5,25.4)
# ----- 23.5–29.6: phone pullback then audio-message camera -----
hardware=phone();g=grp(hardware['children'],398,80)
anim(g,x=[(23.4,40),(24,398),(26,398),(26.6,165),(27.2,160),(28.3,160),(29,120),(29.6,120)],y=[(23.4,-1700),(24,80),(26,60),(26.6,-1100),(27.2,-1100),(28.3,-1100),(29,-1100),(29.6,-1100)],scaleX=[(23.4,1.36),(24,.694),(26,.694),(26.6,1.2),(27.2,1.2),(28.3,1.2),(29,1.2)],scaleY=[(23.4,1.36),(24,.694),(26,.694),(26.6,1.2),(27.2,1.2),(28.3,1.2),(29,1.2)],opacity=[(23.4,0),(23.8,1),(29.1,1),(29.6,0)])
# Insert device underneath existing scene23.5 layers
L.insert(0,g);g.update(start=23.4,end=29.6)
header=grp([node('circle',x=0,y=0,width=120,height=120,fill='#ffffff'),path('M 71 35 L 48 60 L 71 85','none',stroke='#555555',strokeWidth=6),img('poke-square',350,-6,164,164),img('verified',346,169,41,42),text(402,169,'Poke ›',43,weight=700)],440,215)
fade(header,23.5,26.6,.2);header['scaleX']=.694;header['scaleY']=.694;put(header,23.5,26.6)
zmap=bubble(460,430,390,388,fill='#e3e3e0',tail=False)
zmap['children'] += [img('zareen-map',0,0,390,295),text(23,310,"Zareen’s",28),text(23,347,'maps.apple.com',23,'#888888')]
anim(zmap,y=[(24.45,1100),(25,430),(25.7,340),(26.3,-60),(26.8,-400)],x=[(24.45,460),(25.7,460),(26.3,285),(26.8,285)],scaleX=[(24.45,1),(25.7,1),(26.3,1.6),(26.8,1.6)],scaleY=[(24.45,1),(25.7,1),(26.3,1.6),(26.8,1.6)])
put(zmap,24.45,29.4)
away=bubble(460,810,430,78,'only 0.16 mi away from you',30,padx=23,pady=17)
anim(away,x=[(25.2,460),(26,460),(26.8,288),(28.3,288),(29,241)],y=[(25.2,880),(25.7,810),(26.8,231),(28.3,231),(29,68)],scaleX=[(25.2,1),(26,1),(26.8,1.45),(29,1.45)],scaleY=[(25.2,1),(26,1),(26.8,1.45),(29,1.45)])
put(away,25.2,29.5)
audio=bubble(499,397,746,282,right=True,fill='#a0a4af')
audio['children'] += [node('circle',x=54,y=31,width=76,height=76,fill='#ffffff'),path('M 79 52 L 79 88 Q 79 92 83 90 L 108 74 Q 113 70 108 67 L 84 52 Q 79 49 79 52 Z','#a0a4af'),text(633,47,'0:04',34,'#dce0e6'),text(54,146,'Please remind me about this dinner 1\nhour before.',34,'#d1d5dd',lineHeight=37)]
heights=[18,16,40,22,72,32,52,25,55,20,47,25,19,34,30,22,44,28,55,18,42,20,48,16,24,28,30,55,19,25,27,29,22,31,17,28,26,23,24,21,27,20,25,22]
for i,hh in enumerate(heights):audio['children'].append(rect(159+i*10,69-hh/2,4,hh,'#ffffff',2))
anim(audio,x=[(26.4,650),(26.85,499),(28.3,499),(29,450)],y=[(26.4,900),(26.85,397),(28.3,397),(29,221)],opacity=[(26.4,0),(26.65,1),(29.2,1),(29.6,0)])
put(audio,26.4,29.6)
reply=bubble(253,544,651,113,'sure, i’ll remind you on time',49,padx=38,pady=25)
anim(reply,y=[(28.45,720),(29,544)],opacity=[(28.45,0),(28.7,1),(29.15,1),(29.6,0)]);put(reply,28.45,29.6)
comp2=composer(442,870,1190,60);anim(comp2,x=[(23.7,442),(26,442),(26.8,275),(28.3,275),(29,230)],y=[(23.7,890),(26,870),(26.8,735),(28.3,735),(29,735)],scaleX=[(23.7,.52),(26,.52),(26.8,.84),(29,.84)],scaleY=[(23.7,.52),(26,.52),(26.8,.84),(29,.84)],opacity=[(23.7,0),(24,1),(29.2,1),(29.6,0)]);put(comp2,23.7,29.6)
kb2=keyboard(423,962,1250);kb2['children']=[v for v in kb2['children'] if v.get('type')!='text' or v.get('text')!='➤ Current Location'];anim(kb2,x=[(23.7,423),(26,423),(26.8,213),(28.3,213),(29,165)],y=[(23.7,980),(26,962),(26.8,872),(29,872)],scaleX=[(23.7,.514),(26,.514),(26.8,.88),(29,.88)],scaleY=[(23.7,.514),(26,.514),(26.8,.88),(29,.88)],opacity=[(23.7,0),(24,1),(29.2,1),(29.6,0)]);put(kb2,23.7,29.6)
# ----- 29.6–36.6: measured feature-card scrolling -----
# bounding boxes measured by connected-component analysis in native reference anchors.
featuredata=[
('Email','Send, reply, and forward messages','feature-mail',[(29.6,300,1090,840),(30,243,635,953),(31,215,356,1010),(32,265,142,910),(33,298,-95,844),(33.5,298,-230,844)]),
('Calendar','View, create, and reschedule events','feature-calendar',[(29.6,300,1350,840),(30,299,895,842),(31,238,610,964),(32,209,380,1021),(33,262,156,916),(34,298,-70,844),(34.5,298,-230,844)]),
('Reminders','Schedule one-time reminders','feature-clock',[(30,300,1350,840),(31,293,872,854),(32,243,636,954),(33,207,393,1026),(34,254,190,932),(35,298,-42,844),(35.5,298,-240,844)]),
('Automations','Create and manage automations','feature-clock',[(31,300,1350,840),(32,298,897,844),(33,247,651,946),(34,199,428,1042),(35,253,197,935),(36,298,-50,844),(36.5,298,-280,844)]),
('Image Search & Generation','Find images and generate new ones','feature-image',[(32,300,1350,840),(33,298,911,844),(34,254,689,932),(35,199,435,1041),(36,253,194,934),(36.7,298,-180,844)]),
('Web Search & Browse','Look things up and visit websites','feature-search',[(33,300,1350,840),(34,298,948,844),(35,256,697,929),(36,200,432,1040),(36.7,270,120,900),(37,298,-100,844)])]
for label,sub,ico,anchors in featuredata:
 c=bubble(0,0,1040,198,tail=True)
 c['children'] += [text(42,54,label,35,'#222222',500,family='SF Pro Display'),text(42,99,sub,34,'#888888',family='SF Pro Display'),img(ico,837,20,156,156)]
 anim(c,x=[(a[0],a[1]) for a in anchors],y=[(a[0],a[2]) for a in anchors],scaleX=[(a[0],a[3]/1040) for a in anchors],scaleY=[(a[0],a[3]/1040) for a in anchors],opacity=[(anchors[0][0],0),(anchors[0][0]+.3,1),(36.3,1),(36.7,0)])
 put(c,anchors[0][0],min(anchors[-1][0],36.7))
# ----- 36.3–37.8: native service connection cards -----
for i,(label,domain,icon) in enumerate([('Gmail','gmail.com','gmail'),('Notion','notion.so','notion'),('Todoist','todoist.com','todoist')]):
 y=[161,372,588][i];c=grp([rect(0,0,671,172,'#e9e9eb',80),text(60,24,'Connect '+label,56),text(60,90,domain,46,'#858585'),img('connect-'+icon,533,35,98,98)],72,y)
 anim(c,y=[(36.05+i*.13,y+750),(36.7+i*.08,y),(37.55,y),(37.9,y-700)],opacity=[(36.05+i*.13,0),(36.45+i*.13,1),(37.65,1),(37.9,0)])
 put(c,36.05+i*.13,37.9)
connect=bubble(72,813,917,152,'connect all your favorite tools',60,padx=53,pady=30)
anim(connect,y=[(36.6,1200),(37.05,813),(37.55,813),(37.9,113)],opacity=[(36.6,0),(36.95,1),(37.65,1),(37.9,0)])
put(connect,36.6,37.9)
# ----- 37.8–40.6: independently positioned branded icon grid -----
rows=[['sonos','github','banana','asana','hex','strava'],['spiral','webflow','canva','todoist','oura','sonos'],['outlook','cursor','vercel','notion','gmail','spiral'],['netlify','linear','calendar','sonos','github','outlook']]
# Fill missing clipped edge logos from their other fully visible appearances.
for r,row in enumerate(rows):
 for col,name in enumerate(row):
  if not (P/'assets'/f'brand-{name}.png').exists():
   # Authentic static logo crops are available for every edge logo except Strava;
   # render its known wordmark in native geometry as a documented approximation.
   if name=='strava':c=grp([rect(0,0,225,225,'#f23b00',54),text(112,93,'STRAVA',43,'#ffffff',700,textAnchor='middle')])
   elif name=='sonos':c=grp([rect(0,0,225,225,'#000000',54),text(112,85,'SONOS',45,'#ffffff',600,textAnchor='middle')])
   elif name=='spiral':c=grp([rect(0,0,225,225,'#b5cc49',54),text(112,44,'◎',140,'#252626',600,textAnchor='middle')])
   elif name=='netlify':c=grp([rect(0,0,225,225,'#ffffff',54,stroke='#d9dfe2',strokeWidth=3),text(112,42,'✣',140,'#1cbaa9',textAnchor='middle')])
   elif name=='outlook':c=grp([rect(0,0,225,225,'#ffffff',54),rect(20,50,175,130,'#0788d9',10),text(63,68,'O',85,'#ffffff',600)])
   else:raise RuntimeError('Missing logo '+name)
  else:c=img('brand-'+name,0,0,225,225)
  xx=-78+col*272;yy=22+r*272
  g=grp([c],xx,yy)
  anim(g,x=[(37.8,720+(xx-720)*.6),(38.45,xx+20),(39,xx),(40.6,xx-15)],y=[(37.8,540+(yy-540)*.6),(38.45,yy+15),(39,yy),(40.6,yy-5)],scaleX=[(37.8,.6),(38.45,1),(40.6,1.03)],scaleY=[(37.8,.6),(38.45,1),(40.6,1.03)],opacity=[(37.8,0),(38.6,1),(40.6,1)])
  put(g,37.8,40.6)
# ----- 40.6–end: exact standalone brand wordmark asset -----
put(img('poke-wordmark',499,492,428,84),40.6,D)
# Root scene
scene={'title':'Poke — Apple Messages launch / independent editable reconstruction','width':1440,'height':1080,'fps':fps,'duration':D,'background':'#ffffff','source':{'path':'source.mp4','sourceStart':0,'sourceEnd':D,'notes':'Independent native reconstruction; raster assets restricted to authentic static artwork listed in assets/provenance.json. Temporal anchors measured at native seconds, interpolated easing remains approximate. Full1283-frame timeline; no source-video overlay. Official SF Pro Text and Display are embedded. Family/style and optical-size matching remain measured approximations.'},'fonts':fontfiles,'gradients':[{'id':'chrome','type':'linear','x1':'0%','y1':'0%','x2':'100%','y2':'0%','stops':[{'offset':'0%','color':'#888a8b'},{'offset':'12%','color':'#f0f1f2'},{'offset':'25%','color':'#3c3d3e'},{'offset':'45%','color':'#bdbfc0'},{'offset':'68%','color':'#ffffff'},{'offset':'100%','color':'#555759'}]}],'layers':L}
(P/'scene.json').write_text(json.dumps(scene,indent=2))
print('Built',uid,'editable/native layers,',len(L),'top-level groups,',len(fontfiles),'fonts')
