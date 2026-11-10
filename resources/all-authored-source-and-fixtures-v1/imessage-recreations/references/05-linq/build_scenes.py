from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, random
ROOT=Path('/workspace/imessage-recreations')
A=ROOT/'references/05-linq'; B=ROOT/'references/06-gallery'
FONT='SF Pro Display, Liberation Sans, Arial, sans-serif'
seq=0

def uid(p):
 global seq
 seq+=1
 return f'{p}-{seq}'
def rect(x,y,w,h,fill='#ffffff',r=0,**kw): return dict(type='rect',id=uid('r'),x=x,y=y,width=w,height=h,fill=fill,radius=r,**kw)
def circle(x,y,d,fill='#ffffff',**kw): return dict(type='circle',id=uid('c'),x=x,y=y,width=d,height=d,fill=fill,**kw)
def text(s,x,y,size=32,fill='#111111',weight=400,**kw): return dict(dict(type='text',id=uid('t'),text=s,x=x,y=y,fontSize=size,fontFamily=FONT,fill=fill,fontWeight=weight,lineHeight=size*1.18),**kw)
def path(d,fill='#000000',**kw):return dict(type='path',id=uid('p'),d=d,fill=fill,**kw)
def img(src,x,y,w,h,**kw): return dict(type='image',id=uid('i'),src=src,x=x,y=y,width=w,height=h,**kw)
def group(children,x=0,y=0,**kw):return dict(type='group',id=uid('g'),x=x,y=y,children=children,**kw)
def k(*vals):return [dict(t=t,value=v,**({'ease':e} if e else {})) for t,v,*es in vals for e in [(es[0] if es else 'linear')]]
def show(children,start,end,entry=.18,dy=24,**kw):
 g=group(children,start=start,end=end,**kw)
 if entry:g['keyframes']={**({'y':k((start,g.get('y',0)+dy),(start+entry,g.get('y',0),'easeOut'))} if 'y' not in g.get('keyframes',{}) else {}),'opacity':k((start,0),(start+entry,1,'easeOut')),**g.get('keyframes',{})}
 return g
def center(s,y,size,w=960,fill='#000000',weight=400):return text(s,w/2,y,size,fill,weight,textAnchor='middle')
def bubble(s,x,y,w,h,size=36,blue=False,tail=True,fill=None):
 f=fill or ('#347ff1' if blue else '#e7e7e7'); ch=[rect(0,0,w,h,f,min(h/2,48))]
 if tail:
  d=f'M {w-45} {h-15} Q {w-26} {h+10} {w-18} {h+13} Q {w-32} {h-8} {w-18} {h-22} Z' if blue else f'M 18 {h-26} Q 46 {h-5} 10 {h+14} Q 27 {h+12} 48 {h-9} Z'
  ch.append(path(d,f))
 ch.append(text(s,30,20,size,'#ffffff' if blue else '#151515'))
 return group(ch,x,y)
def crop(root,frame,box,name,alpha=False,rounding=None):
 im=Image.open(root/f'keyframes/{frame}.png').convert('RGBA').crop(box)
 if alpha:
  pix=im.load()
  for yy in range(im.height):
   for xx in range(im.width):
    r,g,b,a=pix[xx,yy];pix[xx,yy]=(r,g,b,max(0,min(255,int((255-min(r,g,b))*2.8))))
 if rounding:
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,im.width-1,im.height-1),radius=rounding,fill=255);im.putalpha(mask)
 im.save(root/f'assets/{name}.png');return f'assets/{name}.png'

# Only actual static pictorial assets are cropped; no complete source frames or UI screenshots.
assets=[]
def ac(root,fr,box,name,**kw):
 src=crop(root,fr,box,name,**kw);assets.append(dict(root=root.name,path=src,frame=fr,box=box,kind='static pictorial crop'));return src
bridge=ac(A,'011.50',(99,237,629,550),'golden-gate-photo',rounding=30)
neck=ac(A,'021.20',(316,0,643,548),'necklace-product')
food=ac(A,'037.00',(201,303,534,636),'restaurant-food',rounding=20)
interior=ac(A,'037.00',(558,303,773,636),'restaurant-interior',rounding=20)
messages=ac(A,'044.00',(285,304,337,355),'messages-icon',rounding=12)
linqmark=ac(A,'046.50',(322,322,383,390),'linq-mark',alpha=True)
mascot=ac(B,'048.50',(664,437,839,631),'rene-mascot',alpha=True)
qr=ac(B,'053.00',(613,479,735,603),'rene-qr')
marcus=ac(B,'000.50',(294,452,451,608),'marcus-memoji',rounding=78)
priya=ac(B,'006.50',(428,426,522,519),'priya-memoji',rounding=46)
ball=ac(B,'034.50',(1752,374,1887,508),'soccer-ball',alpha=True)
faceboxes=[(710,136,901,329),(1030,185,1249,407),(549,402,757,612),(1247,445,1409,610),(877,556,1131,804),(660,738,851,928),(1105,729,1284,909),(872,808,1003,945)]
faces=[ac(B,'021.50',bb,f'portrait-{i}',rounding=min(bb[2]-bb[0],bb[3]-bb[1])//2) for i,bb in enumerate(faceboxes)]
(A/'assets/asset-provenance.json').write_text(json.dumps([x for x in assets if x['root']==A.name],indent=2))
(B/'assets/asset-provenance.json').write_text(json.dumps([x for x in assets if x['root']==B.name],indent=2))

# LINQ
L=[]
# Input field and type reveal, source bounds x180..782, y319..402.
composer=[circle(180,321,78,'#ffffff',shadow={'x':0,'y':3,'blur':8,'color':'#0000000b'}),rect(273,320,509,82,'#ffffff',41,shadow={'x':0,'y':4,'blur':14,'color':'#0000000c'}),text('+',201,331,52,'#555555'),dict(circle(688,332,77,'#0088ff'),height=57),path('M 727 375 L 727 345 M 714 358 L 727 345 L 740 358','none',stroke='#ffffff',strokeWidth=5)]
L.append(show(composer,0,3.5,0))
phrase="Yo i'm bored, chess battle?"
for i in range(len(phrase)+1):
 a=.3+i*.092; b=.3+(i+1)*.092 if i<len(phrase) else 3.5
 L.append(show([text(phrase[:i] if i else 'iMessage',305,344,32,'#222222' if i else '#bcbcbc'),rect(305+i*13.68,340,2,42,'#4ba9f9')],a,b,0))
# app drawer
menu=[]
for i,(name,col,icon) in enumerate([('Photos','#e6788a','✿'),('Apple Cash','#000000',''),('Polls','#6ba3ee','▤'),('Store','#2087ef','A'),('GamePigeon','#64bf5c','♟'),('Threadsby','#000000','@'),('Star Flights','#69b7f5','✈')]):
 y=i*94;menu += [rect(0,y,560,94,'#ffffff'),rect(30,y+16,62,62,col,15),text(icon,43,y+20,40,'#ffffff'),text(name,122,y+25,36)]
g=group(menu,200,-95,start=3.5,end=4.33,keyframes={'y':k((3.5,-50),(4.1,-330,'easeInOut'))});L.append(g)
# chess grid preview native gameboard
pieces=['♜♞♝♛♚♝♞♜','♟♟♟♟♟♟♟♟','        ','        ','        ','        ','♙♙♙♙♙♙♙♙','♖♘♗♕♔♗♘♖']
def chess(x,y,size=560,start=0,end=60,preview=False):
 ch=[rect(-12,-12,size+24,size+24,'#e5bd83',3)]
 cell=size/8
 for row in range(8):
  for col in range(8):
   ch.append(rect(col*cell,row*cell,cell,cell,'#bd8751' if (row+col)%2 else '#f1c88f'))
   pc=pieces[row][col]
   if pc!=' ':ch.append(text(pc,col*cell+cell*.07,row*cell-cell*.01,cell*.89,'#171b22' if row<2 else '#ffffff',400,stroke='#777777',strokeWidth=.8))
 return group(ch,x,y,start=start,end=end)
# Game picker tiles
pick=[]
for i,(label,symbol) in enumerate([('8 BALL','●'),('CHESS','♜'),('FOUR IN A ROW','🔴'),('WORD GAMES','ABC'),('CRAZY 8','8'),('CUP PONG','▽')]):
 xx=(i%3)*185;yy=(i//3)*220;pick +=[rect(xx,yy,175,200,'#f0f0f0',16),text(symbol,xx+45,yy+30,75),text(label,xx+88,yy+155,15,textAnchor='middle')]
L.append(show(pick,4.33,4.93,.08,x=206,y=115))
preview=[rect(0,0,520,438,'#f3f3f3',50),chess(95,15,330),circle(204,137,110,'#83b625',stroke='#d4e8ac',strokeWidth=5),path('M 246 163 L 246 217 L 286 190 Z','#ffffff'),center("LET'S PLAY CHESS!",380,24,520,weight=700)]
L.append(show(preview,4.93,6.97,.16,x=390,y=95))
L.append(show([bubble("Yo i'm bored, chess battle?",390,550,520,85,30,True)],5.35,6.97,.18))
L.append(show([bubble('Always down ♟',95,620,300,76,30)],6.1,6.97,.18))
L.append(chess(190,-24,580,start=6.97,end=8.57))
# pawn motion layer, replacing square in board
L.append(show([rect(362,485,72.5,72.5,'#6aa6ff',opacity=.5),text('♙',365,480,64,'#ffffff')],7.2,8.57,.05))
L.append(show([bubble('hey can you find me a one\nway flight from Atlanta to San\nFrancisco in July? looking for\nsomething cheap',326,262,536,211,40,True)],8.57,10.57,.2))
L.append(show([bubble("On it! 👀 Found a few options,\nhere's the cheapest one way:",95,74,537,133,36,False,False),rect(99,237,530,438,'#d8d8d8',36),img(bridge,99,237,530,313),text('✈',125,258,53),text('Cheap flight from ATL to SFO',123,571,30,weight=700),text('Tap for details',124,623,25,'#8b8b8b')],10.57,12.07,.18))
# Airline fare cards
fare=[rect(0,0,582,1000,'url(#flight-sky)'),text('Flight Details',292,25,30,'#ffffff',700,textAnchor='middle'),rect(22,85,538,206,'#ffffff',25),text('ATL  →  SFO',52,110,44,weight=700),text('Frontier     July 2, 2026',52,176,22,'#555555'),text('5h 35m (non stop)',52,225,18,'#888888'),text('$199',470,219,32,weight=700)]
for xx,label in [(-140,'Basic'),(220,'Economy')]:
 fare += [rect(xx,320,338,560,'#ffffff',28),text(label,xx+25,343,34,weight=700),text('Cabin: Coach',xx+25,399,20,'#888888'),text('Baggage',xx+25,464,18),text('🟢  Personal item included\n🟢  Carry-on bag for a fee*\n⊕   First checked bag for a fee*\n⊕   Second checked bag for a fee*\n⊕   Third checked bag for a fee*',xx+25,503,17,'#888888',lineHeight=32),text('Seat',xx+25,665,18),text('🟢  Seat selection for a fee*',xx+25,704,17,'#888888'),text('Voluntary Change',xx+25,751,18),text('🟢  Changeable*',xx+25,789,17,'#888888'),rect(xx+25,815,286,47,'#3b83ef',24),text('Select',xx+167,825,20,'#ffffff',700,textAnchor='middle')]
L.append(show(fare,12.07,13.9,.18,x=188,y=-190,clip={'width':582,'height':1000}))
# seat screen
seat=[rect(0,0,582,1000,'#397ce9'),center('Select your seat',24,30,582,'#ffffff',700)]
for row in range(12):
 for col in range(6):
  xx=115+col*46+(35 if col>=3 else 0);yy=91+row*42
  seat +=[rect(xx,yy,30,31,'#e8f4fa',6),text('×',xx+8,yy+1,26,'#b6c7d6')]
 seat.append(text(str(row+5),275,91+row*42,16,'#dce7f5'))
seat +=[rect(28,557,526,191,'#ffffff',30),text('Selected Seat             Passenger               Class',52,578,14,'#888888'),text('10C                         1                    Economy',52,606,20),text('Total',52,662,16,'#888888'),text('$235',52,686,25,weight=700),rect(402,679,110,43,'#3787f3',24),text('Book',457,687,19,'#ffffff',700,textAnchor='middle')]
L.append(show(seat,13.9,15.63,.16,x=188,y=-59))
L.append(show([bubble('Your flight is booked! ✈️\nFrontier Airlines\nJuly 2 | 1 passenger\nAircraft: Airbus A321',95,180,540,230,35)],15.63,17.1,.18))
L.append(show([bubble('i wanna check out some necklaces',370,120,500,92,28,True)],17.1,18.0,.18))
L.append(show([bubble("Here's what's hot right now 🔥",95,160,540,90,32,False,False),bubble("♧  Men's Jewelry\n    Tap for details",95,280,360,134,30)],18.0,19.3,.18))
# necklace detailed sheet with native captions/button
L.append(show([rect(198,-15,565,780,'#ffffff'),img(neck,316,0,327,548),text('VIVIENNE WESTWOOD',225,590,13,weight=700),text('Carmelo Bas Relief Pendant Necklace',225,612,12),text('$320 USD',670,590,13),text('Duties calculated at checkout.',561,613,12,'#888888'),rect(225,660,454,68,'#000000',35),text('Add to Bag',452,678,26,'#ffffff',textAnchor='middle'),text('♡',704,674,40)],19.3,21.55,.18))
L.append(show([bubble("Order confirmed, I'll ping you\nwhen tracking's ready 📦",95,270,570,145,34)],21.55,22.85,.18))
L.append(show([bubble('can you order my\nweekly groceries?',430,80,360,130,34,True)],22.85,25.33,.18))
L.append(show([bubble("Sure, it'll be $166.89",112,232,380,86,32,False,False),rect(112,346,430,348,'#171717',43),text('Cash',140,371,24,'#ffffff'),text('$166.89 Request',160,448,39,'#ffffff'),rect(232,577,188,88,'#ffffff',46),text('Pay',326,597,37,'#111111',textAnchor='middle'),circle(501,315,62,'#1887f5'),text('👍',510,320,36)],23.7,25.33,.18))
L.append(show([circle(180,170,72,'#ffffff'),text('+',201,178,45),rect(270,168,510,76,'#ffffff',36),text('iMessage',295,192,28,'#cccccc'),rect(185,260,590,461,'#0d0d0d',70),rect(451,277,54,5,'#555555',3),text('−',260,378,40,'#ffffff'),center('$166.89',382,70,960,'#ffffff'),text('+',656,378,40,'#ffffff'),center('Show Keypad',519,18,960,'#777777'),rect(231,611,240,70,'#252525',35,stroke='#777777',strokeWidth=1),rect(493,611,240,70,'#252525',35,stroke='#777777',strokeWidth=1),text('Request',350,631,25,'#ffffff',textAnchor='middle'),text('Send',610,631,25,'#ffffff',textAnchor='middle')],25.33,27.67,.12))
L.append(show([bubble('Got it, ordering now 🛒',95,285,510,110,35)],27.67,28.83,.18))
# game 2
L.append(show([rect(237,0,486,720,'#f6e4be'),text('You                         MyAI',280,31,23),chess(251,125,458)],28.83,31.37,.12))
L.append(show([rect(348,330,275,90,'#ffdf00',10),text('YOU WON!!',485,357,32,'#000000',700,textAnchor='middle')],30.2,31.37,.08))
rng=random.Random(51)
conf=[]
for i in range(95):
 xx=rng.randrange(30,930);yy=rng.randrange(-250,710);q=rect(xx,yy,5,14,['#fa3254','#43bef2','#f7b62a','#45c579'][i%4],1,rotation=rng.randrange(180),keyframes={'y':k((30.2,yy-350),(31.37,yy+180))});conf.append(q)
L.append(show(conf,30.2,31.37,0))
# four in row native board
four=[rect(0,0,490,720,'#141721'),text('You                 Friday',42,24,25,'#ffffff'),text('● Red                      ● Yellow',42,65,16,'#aaaaaa'),rect(20,141,450,510,'#1b2234',30)]
for rr in range(6):
 for cc in range(7):
  col='#111722'
  if rr>=2 and cc in [1,2,3,4] and rr+cc>5:col='#ff3853' if (rr+cc)%2 else '#ffd642'
  four.append(circle(39+cc*59,161+rr*73,47,col))
L.append(show(four,31.37,33.17,.1,x=235))
# food order list
order=[rect(192,0,580,780,'#ffffff'),text('Foodash',215,18,32,weight=700),text('Shake Shack SoHo',215,72,26),text('Group order',215,110,19,'#888888')]
for i,(n,d,p) in enumerate([('Dakota','ShackBurger + Fries','$17'),('Jamie(you)','Chick’n Shack + Lemonade','$16'),('Dillion','Veggie Shack','$12'),('Priya','is choosing...',''),('Carlos','is choosing...',''),('Siobhan','is choosing...','')]):
 yy=169+i*80;order +=[text(n,219,yy,22),text(d,219,yy+31,17,'#888888'),text(p,680,yy,22)]
order +=[rect(220,666,520,1,'#cccccc'),text('Subtotal(3 orders)                      $45',219,686,20),text('Tips                                         $0',219,719,20)]
L.append(show(order,33.17,35.63,.18))
# restaurant UI / photo carousel
rest=[rect(190,-10,584,740,'#ffffff'),text('Boqueria Soho',196,18,33),text('Open now',424,27,21,'#579b50'),text('4.6 ★ (3,893) · $$ · Spanish Restaurant',196,75,24,'#555555'),rect(196,122,357,69,'#111111',36),text('Directions',374,145,24,'#ffffff',textAnchor='middle'),rect(579,123,62,66,'#ffffff',20,stroke='#dddddd',strokeWidth=2),text('♧',594,134,31),rect(663,123,65,66,'#ffffff',20,stroke='#dddddd',strokeWidth=2),text('◎',678,136,30),text('Overview       Reserse       Menu       Reviews',196,243,24,'#777777'),rect(196,280,95,2,'#333333'),img(food,201,303,333,333),img(interior,558,303,215,333),text('♧  171 Spring St, New York, NY 10012',202,691,23)]
L.append(show(rest,35.63,38.13,.1))
L.append(show([bubble('Oh, and check-in just opened for\nyour July 2 flight to SFO! Gate 37,\nSeat 10C — tap to get your\nboarding pass. ✈️',95,238,625,255,35)],38.13,39.5,.16))
# boarding pass
bp=[rect(0,0,960,900,'#3b526f'),text('Atlanta, GA\nTerminal B',57,61,35,'#ffffff'),text('San Francisco, CA\nTerminal D',899,61,35,'#ffffff',textAnchor='end'),text('ATL',55,170,128,'#ffffff'),text('✈',444,198,89,'#ffffff'),text('SFO',640,170,128,'#ffffff'),rect(38,382,880,650,'#ffffff',40),text('Passenger',82,430,32,'#888888'),text('Gate',530,430,32,'#888888'),text('Seat',777,430,32,'#888888'),text('Nikki Hanse',82,498,49,weight=700),text('37',530,498,49,weight=700),text('10C',777,498,49,weight=700),rect(82,601,787,310,'#f0f0f0',33),text('Date                         Boarding',126,650,32,'#888888'),text('2 July 2026                  2:50pm',126,709,42)]
L.append(show(bp,39.5,40.63,.13))
# native phone gallery miniatures; detailed source artwork intentionally not rasterized.
for i in range(8):
 xx=(i%4)*259-85;yy=(i//4)*620-180
 children=[rect(0,0,245,531,'#999999',43),rect(4,4,237,523,'#050505',39),rect(12,12,221,507,'#ffffff',34),rect(83,20,85,25,'#000000',15),text('9:41',30,22,13),text('Rene' if i%2 else 'My AI',122,73,22,textAnchor='middle'),bubble('hey! can you help?',47,148,170,65,16,True),bubble('Of course. What do\nyou need today?',22,242,180,87,16)]
 L.append(show(children,40.63,42.27,.1,x=xx,y=yy,keyframes={'y':k((40.63,yy+100),(42.27,yy-100))}))
L.append(show([img(messages,286,305,50,50),text('iMessage Apps',355,304,44)],42.27,44.6,.15))
L.append(show([center('that supercharge your 🤖 agents',359,44)],43.42,44.6,.18))
L.append(show([center('What will you build?',334,44)],44.6,45.93,.16))
L.append(show([img(linqmark,322,322,61,68),text('linq',394,330,49)],45.93,48,.15))
for gg in L:
 for child in gg.get('children',[]):
  if child.get('type')=='group':
   for tx in child.get('children',[]):
    if tx.get('type')=='text' and tx.get('text','').startswith('hey can you find me a one'):
     tx['lineHeight']=42;tx['y']=24
linq=dict(title='Linq iMessage Apps — native independent reconstruction',width=960,height=720,fps=30,duration=48.6,background='#ffffff',layers=L,source={'path':'source.mp4','sourceStart':0,'sourceEnd':48.6,'notes':'Independent editable geometric reconstruction. Full graphic timeline covered. Validated official SF Pro Display embedded; original font identity still inferred from pixels. Timings fit observed keyframes, not exact recovered curves. Assets are declared photo/logo crops only. No original video or complete source frames in layers.'})
linq['gradients']=[{'id':'flight-sky','type':'linear','stops':[{'offset':'0%','color':'#347feb'},{'offset':'100%','color':'#a2d0e0'}]}]
linq['fonts']=[{'family':'SF Pro Display','src':'assets/sf-pro-display-used-'+style.lower()+'.otf','weight':weight} for style,weight in [('Regular',400),('Medium',500),('Semibold',600),('Bold',700)]]
(A/'scene.json').write_text(json.dumps(linq,indent=2))

# RENE
# Extract only the physical hardware ring: native screen pixels are fully transparent.
hw=Image.open(B/'keyframes/026.50.png').convert('RGBA').crop((620,0,1301,1080))
mask=Image.new('L',hw.size,0);dr=ImageDraw.Draw(mask);dr.rounded_rectangle((0,0,680,1490),radius=145,fill=255);dr.rounded_rectangle((29,24,650,1460),radius=122,fill=0);hw.putalpha(mask);hw.save(B/'assets/phone-hardware-ring.png')
prov=json.loads((B/'assets/asset-provenance.json').read_text());prov.append({'path':'assets/phone-hardware-ring.png','frame':'026.50','box':[620,0,1301,1080],'kind':'physical phone bezel only; entire screen alpha-masked'});(B/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2))
R=[];CUT=181/30
# Source-native to graphics-only output mapping.
def mt(t):return t if t<41 else t-CUT

def rs(ch,a,b,entry=.18,**kw):
 aa,bb=mt(a),mt(b);g=show(ch,aa,bb,entry,**kw);R.append(g);return g

def phone(children,title='Rene'):
 return [rect(27,24,625,1456,'#fbfbfb',122),img('assets/phone-hardware-ring.png',0,0,681,1080),rect(242,48,194,55,'#000000',31),text('12:02',107,57,29,weight=700),rect(482,74,5,9,'#000000',1),rect(490,68,5,15,'#000000',1),rect(498,62,5,21,'#000000',1),rect(506,57,5,26,'#000000',1),path('M 524 65 Q 538 53 552 65 M 529 71 Q 538 63 547 71','none',stroke='#000000',strokeWidth=4),circle(535,75,7,'#000000'),rect(562,60,37,22,'none',4,stroke='#888888',strokeWidth=2),rect(565,63,31,16,'#000000',1),rect(601,67,3,8,'#999999',1),circle(405,66,10,'#141027'),circle(57,136,83,'#f8f8f8'),text('‹',85,143,55,'#444444'),circle(543,136,83,'#f8f8f8'),rect(563,157,31,28,'none',6,stroke='#444444',strokeWidth=3.8),path('M 594 165 L 605 159 L 605 183 L 594 177 Z','none',stroke='#444444',strokeWidth=3.5),circle(286,124,108,'#ffffff',stroke='#dddddd',strokeWidth=2),img(mascot,306,141,72,79),rect(278,225,125,59,'#ffffff',30),text(title,331,242,31,weight=700,textAnchor='middle'),path('M 380 245 L 386 254 L 380 264','none',stroke='#aaaaaa',strokeWidth=5)]+children
# opening isolated measured bubble at .5sec
rs([text('Marcus',569,342,48,'#888888'),img(marcus,294,452,157,156),bubble("We’ve been talking about\nthis trip since January",494,414,1080,263,80)],0,1.1,.04)
# full group conversation, exact reference rest at source3s
conv=[text('Marcus',140,312,17,'#888888'),img(marcus,47,352,52,52),bubble("We’ve been talking about\nthis trip since January",113,338,361,88,27),text('Priya',140,451,17,'#888888'),img(priya,47,506,52,52),bubble("Someone just pick a weekend,\nI’m not the mom of this group",113,475,413,88,27),text('Dan',140,588,17,'#888888'),circle(47,643,52,'#e4d6ff'),text('👨',49,646,40),bubble('Not me, I organized the last\none',113,611,373,88,27),text('Rene',140,726,17,'#888888'),img(mascot,56,776,36,42),bubble('Oct 17 is the first weekend\nall of you are free',113,748,373,88,27)]
g=rs(phone(conv,'Cabin trip 🏕️'),1.1,3.6,.2,x=535,y=70);g['keyframes']={'scaleX':k((1.1,1.55),(2.3,1.214,'easeOut')),'scaleY':k((1.1,1.55),(2.3,1.214,'easeOut')),'x':k((1.1,417),(2.3,535,'easeOut')),'y':k((1.1,-180),(2.3,70,'easeOut'))}
# lower phone crop, native bubble text and keyboard
lower=[rect(0,-600,1240,2300,'#aaaaaa',140,stroke='#dedede',strokeWidth=5),rect(13,-586,1214,2270,'#080808',130),rect(37,-572,1166,2240,'#ffffff',115),img(mascot,95,210,57,64),bubble('Want me to book the\nlakeside cabin Dan sent?\nBefore someone “gets\nbusy” again 👀',200,32,655,273,48),text('Priya',242,351,29,'#888888'),img(priya,78,427,94,94),bubble('Ok we gotta commit 😭',200,393,580,110,48),bubble('Let’s go! Book it',697,563,434,111,48,True),circle(85,772,120,'#fcfcfc'),text('+',126,796,69),rect(230,770,900,130,'#fdfdfd',65),text('iMessage',270,807,52,'#cccccc'),rect(42,942,1155,360,'#e9e9ee',76),text('“The”                 the                 to',175,988,49,'#666666')]
rs(lower,3.6,7.2,.18,x=350)
rs([bubble('Done. In your calendars 🏕️',550,440,780,140,48)],7.2,8,.15)
# type cards
rs([center('Introducing',465,118,1920)],8,9.5,.3)
rs([text('Introducing',425,461,118),img(mascot,1089,421,152,169),text('Rene',1264,429,157,fontFamily='Times New Roman, serif')],9.5,10.5,.22)
rs([text('The',187,378,120,weight=500),text('best contact',404,378,120,'#218567',500),text('in your phone',1056,378,120,weight=500)],10.5,12.5,.2)
rs([center('with multiplayer mode',510,120,1920,weight=500)],11.7,12.5,.24)
rs([center('Watches your inbox',465,118,1920)],12.5,13.8,.22)
# lockscreen native wallpaper and translucent notification
lock=[rect(0,-550,1140,1555,'#a9a9a9',175),rect(14,-536,1112,1527,'#000000',164),rect(43,-510,1054,1472,'#095d89',146),path('M 43 -510 L 1097 -510 L 1097 340 Q 430 530 43 710 Z','#329b99'),path('M 43 700 Q 620 600 1097 180 L 1097 962 L 43 962 Z','#06245d'),rect(78,430,980,183,'#62bfd5',60,opacity=.42,stroke='#83d2e1',strokeWidth=2),circle(115,454,94,'#ffffff'),img(mascot,132,465,61,68),text('Rene',231,458,39,'#d6eff1'),text('now',958,460,29,'#d6eff1'),text("Heads up : Your landlord emailed about the\nrenewal. Rent’s going up 8%",231,507,34,'#d6eff1'),circle(135,722,163,'#072c6c',opacity=.6),text('♜',192,769,58,'#c6e4ea'),circle(839,722,163,'#116798',opacity=.8),text('▣',889,768,59,'#d7e9ed')]
rs(lock,13.8,15.37,.2,x=391,keyframes={'y':k((13.8,-270),(14.6,0,'easeOut'))})
rs([bubble("Heads up : Your landlord emailed\nabout the renewal. Rent’s going\nup 8%",355,388,1120,322,66,False,False),bubble('3 similar units in your building are\nlisted lower. Want me to write a\npushback?',355,762,1120,330,66)],15.37,16.7,.16)
land=[bubble("Heads up : Your landlord emailed\nabout the renewal. Rent’s going\nup 8%",48,328,461,132,29,False,False),bubble('3 similar units in your building are\nlisted lower. Want me to write a\npushback?',48,469,485,138,29),bubble('Yes plz',527,635,126,68,28,True),bubble("It’s in your drafts. Friendly but firm.\nYou’ve got this",48,751,523,107,28)]
rs(phone(land),16.7,18.5,.2,x=612,y=24)
rs([center('Remembers your people',477,118,1920)],18.5,22.9,.3)
for i,((xx,yy,xe,ye),f) in enumerate(zip(faceboxes,faces)):
 w=xe-xx;h=ye-yy;aa=mt(20.5+i*.045);g=show([img(f,0,0,w,h)],aa,mt(22.9),.22,x=xx,y=yy);g['keyframes']={'x':k((aa,960-w/2),(aa+.45,xx,'easeOut')),'y':k((aa,540-h/2),(aa+.45,yy,'easeOut')),'scaleX':k((aa,.3),(aa+.45,1,'easeOut')),'scaleY':k((aa,.3),(aa+.45,1,'easeOut'))};R.append(g)
rs([rect(575,710,795,155,'#eeeeee',42,opacity=.92),img(mascot,603,735,81,90),text('Rene',712,733,32),text('Emma’s birthday is Saturday 🎁',712,780,36)],22.1,22.9,.2)
# Birthday phone measured native local content
birthday=[bubble('Emma’s birthday is Saturday 🎁',45,328,447,73,29,False,False)]
for aa,ch in [(23.8,bubble('She’s been wanting to try film\nphotography – found a Fuji half\nframe, $189, arrives Friday',45,407,497,139,29)),(24.5,bubble('Wait, you remember that?',270,573,366,73,29,True,False)),(24.9,bubble('Order it. She’s gonna cry',277,652,359,73,29,True)),(25.5,bubble('Done. Gift wrap on 🎉',45,739,310,70,29,False,False)),(26,bubble('I remember everything 😌',45,816,365,73,29))]:
 ch['start']=mt(aa);birthday.append(ch)
g=rs(phone(birthday),22.9,27.25,.18,x=621,y=0);g['keyframes']={'y':k((mt(22.9),150),(mt(23.7),0,'easeOut'))}
rs([center('Tracks what',414,240,1920)],27.25,28.2,.18)
rs([center('you',404,280,1920)],28.2,29.7,.16)
lg=rs([text('l',682,405,280),img(ball,757,450,154,154,end=30.8),text('ve',934,421,265)],29.7,31.8,.08);lg['keyframes']={'x':k((29.7,0),(31.0,0),(31.8,-1800,'easeInOut')),'opacity':k((29.7,0),(29.8,1))}
# soccer messaging with bouncing independent pictorial ball
sg=rs([bubble('It’s official: United signed their\nstriker. Announced 2 min ago 🚨',0,0,896,211,56)],31.4,34.9666667,.08,x=257,y=170);sg['keyframes']={'x':k((31.4,1500),(31.7,754),(32.45,257,'easeOut')),'y':k((31.4,400),(31.7,404),(32.45,170,'easeOut')),'scaleX':k((31.4,1.17),(31.7,1.17),(32.45,1,'easeOut')),'scaleY':k((31.4,1.17),(31.7,1.17),(32.45,1,'easeOut'))}
rs([bubble('LETS GOOOO',1165,445,460,150,56,True,False)],32.5,34.9666667,.16)
rs([bubble('€85M, five years. You called\nthis back in June, btw',258,668,833,220,56)],34.0,34.9666667,.25)
g=rs([img(ball,0,0,135,135)],30.8,34.9666667,0);g['keyframes']={'x':k((30.8,757),(31.7,820),(32.4,1430),(33.5,1108),(34.5,1752)),'y':k((30.8,450),(31.7,242),(32.4,360),(33.5,62),(34.5,374)),'rotation':k((30.8,0),(34.96,720))}
# graphics after excluded live-action sequence
rs([rect(0,0,1920,1080,'#080808'),center('Does the  ▣  work for you',485,118,1920,'#ffffff')],41,43.35,.16)
rs([rect(0,0,1920,1080,'#080808'),center('Lives where you',485,118,1920,'#ffffff')],43.35,44.4,.16)
rs([center('already',485,118,1920)],44.4,45.5,.16)
# app icons native editable geometry with custom logos
app=[text('already',335,485,118),rect(796,455,180,180,'#54df67',38),circle(816,491,139,'#ffffff'),path('M 840 605 L 839 625 L 870 602 Z','#ffffff'),circle(1025,469,160,'#2ba3dc'),path('M 1049 549 L 1155 500 L 1134 594 L 1098 569 L 1080 584 L 1087 557 Z','#ffffff'),rect(1235,455,180,180,'#50db72',38),circle(1264,484,121,'none',stroke='#ffffff',strokeWidth=8),text('☎',1276,485,94,'#ffffff'),text('text',1450,485,118)]
rs(app,45.5,47.4,.18)
rs([img(mascot,664,437,175,194),text('Rene',893,447,170,fontFamily='Times New Roman, serif')],47.4,49.1,.2)
rs([center('Just like a friend',485,118,1920)],49.1,50.55,.15)
rs([center('Start now',485,118,1920)],50.55,51.55,.15)
rs([img(qr,613,479,122,124),rect(788,501,2,80,'#cccccc'),text('rene.co',832,460,155,weight=700)],51.55,55.4666667,.4)
def rene_colors(nodes):
 for n in nodes:
  if n.get('fill')=='#e7e7e7':n['fill']='#ededed'
  if n.get('fill')=='#347ff1':n['fill']='#2397f9'
  if n.get('type')=='group' and n.get('children') and n['children'][0].get('type')=='rect' and n['children'][0].get('fill') in ['#e7e7e7','#ededed','#347ff1','#2397f9']:
   for tx in n['children']:
    if tx.get('type')=='text':tx['y']-=4
  if n.get('type')=='group':rene_colors(n.get('children',[]))
rene_colors(R)
rene=dict(title='Rene — independent graphics-only native reconstruction',width=1920,height=1080,fps=30,duration=1483/30,background='#ffffff',layers=R,source={'path':'source.mp4','sourceStart':0,'sourceEnd':1664/30,'notes':'Graphics-only edit; live action [34.9666667,41) excluded. See segments.json for alignment. Native text/bubbles/phone/layout and explicit pictorial assets. Validated SF Pro Display embedded; unrecovered original easing and blur are approximate. No source-video layer or complete reference-frame layer.'})
rene['fonts']=[{'family':'SF Pro Display','src':'assets/sf-pro-display-used-'+style.lower()+'.otf','weight':weight} for style,weight in [('Regular',400),('Medium',500),('Semibold',600),('Bold',700)]]
(B/'scene.json').write_text(json.dumps(rene,indent=2))
(B/'segments.json').write_text(json.dumps([{'name':'graphics-before-live-action','reference_start':0,'candidate_start':0,'duration':1049/30},{'name':'graphics-after-live-action','reference_start':41,'candidate_start':1049/30,'duration':434/30}],indent=2))
print(json.dumps({'linq_layers':len(L),'rene_layers':len(R),'linq_duration':linq['duration'],'rene_duration':rene['duration'],'assets':len(assets)}))
