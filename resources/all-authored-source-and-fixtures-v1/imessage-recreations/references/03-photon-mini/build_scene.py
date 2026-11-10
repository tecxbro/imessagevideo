import json,math
from pathlib import Path
P=Path(__file__).parent
N=0
FONT='Recreation UI, Arial, sans-serif'
def uid():
 global N;N+=1;return 'p03-'+str(N)
def node(type,**kw):return {'id':uid(),'type':type,**kw}
def rect(x,y,w,h,fill='#fdfdfd',radius=0,**kw):return node('rect',x=x,y=y,width=w,height=h,fill=fill,radius=radius,**kw)
def circle(x,y,w,fill,**kw):return node('circle',x=x,y=y,width=w,height=w,fill=fill,**kw)
def text(s,x,y,fs=34,fill='#000000',weight=400,**kw):return node('text',text=s,x=x,y=y,fontSize=fs,fontFamily=FONT,fontWeight=weight,fill=fill,lineHeight=fs*1.17,**kw)
def img(s,x,y,w,h,**kw):return node('image',src='assets/'+s,x=x,y=y,width=w,height=h,**kw)
def path(d,fill='#000000',**kw):return node('path',d=d,fill=fill,**kw)
def group(children,x=0,y=0,**kw):return node('group',children=children,x=x,y=y,**kw)
def track(vals,ease='easeInOut'):return [{'t':t,'value':v,**({'ease':ease} if i else {})} for i,(t,v) in enumerate(vals)]
def show(n,start,end,dy=25,fade=.2):
 n.update(start=start,end=end);n['keyframes']={'opacity':track([(start,0),(start+fade,1)],'easeOut'),'y':track([(start,n.get('y',0)+dy),(start+fade,n.get('y',0))],'easeOut')};return n
def tail(x,y,w,h,blue=False):
 if blue:return path(f'M {x+w-34} {y+h-28} Q{x+w-25} {y+h+8} {x+w+1} {y+h+12} Q{x+w-10} {y+h-1} {x+w-3} {y+h-15} Z','url(#blue)')
 return path(f'M{x+25} {y+h-22} Q{x+27} {y+h+4} {x+13} {y+h+12} Q{x+48} {y+h+3} {x+55} {y+h-20} Z','#ececec')
def bubble(s,x,y,w,h,blue=False,fs=34,start=0,end=42):
 return group([tail(0,0,w,h,blue),rect(0,0,w,h,'url(#blue)' if blue else '#ececec',h/2 if h<90 else 42),text(s,26,14,fs,'#ffffff' if blue else '#000000')],x,y,start=start,end=end)
def miniicon(x,y,w=60,fill='#eeeeee'):
 return group([rect(0,0,w,w,fill,w*.3),path(f'M{w*.15} {w*.58} Q{w*.4} {w*.17} {w*.8} {w*.2} L{w*.75} {w*.75} Q{w*.56} {w*.67} {w*.15} {w*.58} Z',fill='none',stroke='#111111',strokeWidth=w*.07)],x,y)
def arrow(x,y,w=74,check=False):
 return group([circle(0,0,w,'#0898f5'),path(f'M{w*.32} {w*.48} L{w*.46} {w*.65} L{w*.72} {w*.34}' if check else f'M{w*.5} {w*.75} V{w*.27} M{w*.3} {w*.46} L{w*.5} {w*.25} L{w*.7} {w*.46}',fill='none',stroke='#ffffff',strokeWidth=w*.06)],x,y)
def hardware():
 return [rect(0,0,800,1658,'#111111',150),rect(28,30,744,1600,'#fdfdfd',120),img('phone-hardware.png',0,0,800,1658),rect(285,55,230,66,'#000000',35),circle(468,76,22,'#080a14'),circle(474,82,10,'#141b45')]
def header(team=False):
 title='Team Lunch' if team else 'Agent'; w=250 if team else 160
 return [circle(62,164,82,'#fdfdfd',shadow={'x':0,'y':2,'blur':3,'color':'#00000025'}),path('M106 192 L90 207 L106 222',fill='none',stroke='#444444',strokeWidth=4),circle(660,164,82,'#fdfdfd',shadow={'x':0,'y':2,'blur':3,'color':'#00000025'}),rect(684,193,27,23,'none',4,stroke='#444444',strokeWidth=3),path('M711 199 L721 193 V217 L711 211 Z',fill='none',stroke='#444444',strokeWidth=3),img('team.png' if team else'robot.png',346,160,110,110),rect(400-w/2,260,w,58,'#fdfdfd',29,shadow={'x':0,'y':2,'blur':3,'color':'#00000025'}),text(title,400,268,32,weight=600,textAnchor='middle'),text('›',400+w/2-26,262,44,'#999999'),text('Today 11:20 AM' if team else'Today 9:41 AM',400,344,23,'#949494',textAnchor='middle',start=2.8 if not team else 0)]
def composer():return [circle(60,1440,74,'#fbfbfb'),text('+',97,1447,49,'#444444',textAnchor='middle'),rect(153,1440,580,74,'#fdfdfd',37,stroke='#dddddd',strokeWidth=2),text('iMessage',443,1458,31,'#c7c7c7',textAnchor='middle'),text('♩',694,1453,35,'#c7c7c7')]
def mailcard(y=670):
 return group([tail(0,0,517,370),rect(0,0,517,370,'#e6e6e6',43),group([rect(0,0,517,274,'url(#mail)',43),miniicon(12,12,56),rect(41,90,435,220,'#fdfdfd',30),text('To: Alice',60,110,19,weight=600),text('Subject: Dinner this week',60,140,18),text('Hi Alice,',60,177,20,'#999999'),text('Could you please provide me with the\nradius rate for the bottom corner? Thank',60,221,19,'#999999')],clip={'width':517,'height':274,'radius':43}),text('Mail',23,291,30,weight=600),text('To: Alice',23,329,23,'#aaaaaa')],62,y)
def emailsheet():
 ch=[rect(29,25,742,1608,'#000000',120),rect(50,180,700,1400,'#858585',78),rect(29,196,742,1450,'#fafafa',78),rect(348,207,104,6,'#aaaaaa',3),circle(64,232,78,'#dddddd'),text('×',103,239,55,'#888888',textAnchor='middle'),arrow(658,232,78),text('Dinner This Week',65,344,61,weight=650),text('To:',65,473,28,'#aaaaaa'),text('Alice',112,473,28,'#329cca'),rect(65,525,670,1,'#dddddd'),text('Cc/Bcc, From: ryan@photon.codes',65,558,28,'#aaaaaa'),rect(65,610,670,1,'#dddddd'),text('Subject:',65,642,28,'#aaaaaa'),text('Dinner This Week',178,642,28),rect(65,695,670,1,'#dddddd'),text('Hi Alice,',65,748,28),text("Just wanted to check if we're still on for dinner this\nweek. I'm free Thursday or Friday evening. Let me\nknow what works best for you.",65,813,28,end=8.8),text("Just wanted to check if we're still on for dinner this\nweek. I'm free Saturday or Sunday evening. Let me\nknow what works best for you.",65,813,28,start=8.8),text('Looking forward to catching up.',65,943,28),text('Best,',65,1009,28),text('Ryan',65,1076,28)]
 # Measured editing highlight / caret, modeled separately from text.
 ch += [rect(190,849,335,36,'#91cfff',2,opacity=.55,start=8.0,end=8.72),rect(410,850,2,33,'#111111',start=8.85,end=9.8)]
 return group(ch,start=6.65,end=11.8)
def phone1():
 ch=hardware()+header()
 ch.append(show(bubble('Draft an email to Alice about\nour dinner.',225,390,517,116,True),3.08,11.8,18,.3))
 ch.append(group([circle(0,0,14,'#bbbbbb'),circle(26,0,14,'#bbbbbb'),circle(52,0,14,'#bbbbbb')],82,564,start=4.1,end=4.67))
 ch.append(show(bubble('Working on it.',62,545,267,74),4.7,11.8,20,.2))
 card=show(mailcard(),5.45,13.8,30,.4);card['keyframes']['y']=track([(5.45,680),(5.85,640),(11.8,640),(11.95,670)],'easeOut');ch.append(card)
 ch.append(emailsheet())
 ch.append(show(bubble('Sent.',62,1076,140,74),11.95,13.8,20,.2))
 ch.append(show(bubble("I'll let you know when she replies.",62,1190,450,68,fs=26),12.2,13.8,20,.3))
 ts=[(1.65,.8,1080),(2.05,.98,86),(2.5,1,79),(3,1.12,-36),(4,1.36,-95),(5,1.5,-175),(5.5,1.17,-230),(6,1.23,-332),(6.7,1.02,-180),(8,1.03,-181),(9.5,.99,-147),(10.25,.95,-125),(10.6,2.2,50),(11,2.2,50),(11.25,.77,-110),(11.7,.76,-110),(12.3,1.28,-830),(13.35,1.3,-850),(13.8,1.3,-850)]
 return group(ch,start=1.65,end=13.8,keyframes={'scaleX':track([(t,s)for t,s,y in ts]),'scaleY':track([(t,s)for t,s,y in ts]),'x':track([(t,-580 if 10.6<=t<=11 else (960-400*s))for t,s,y in ts]),'y':track([(t,y)for t,s,y in ts])})
def foodcard(y=1000):
 return group([tail(0,0,520,370),rect(0,0,520,370,'#e6e6e6',42),group([img('pizza-photo.png',0,0,520,278),miniicon(12,12,56),rect(41,89,439,230,'#ffffff',28),text('Lanespan Pizza & Pub\n(Emeryville)',60,109,27,weight=600),text('★4.6 (200+ ratings)•Pizza•$$',60,194,21),text('Open until 3:00 AM\nTap for hours info and more',60,223,18,'#888888'),text('›',436,212,40)],clip={'width':520,'height':278,'radius':42}),text('Uber Eats',23,292,30,weight=600),text('Lanespan Pizza & Pub (Emeryville)',23,331,21,'#aaaaaa')],150,y)
def foodsheet():
 ch=[rect(29,25,742,1608,'#000000',120),rect(50,120,700,1400,'#858585',78),rect(29,170,742,1460,'#fafafa',78),rect(348,181,104,6,'#aaaaaa',3),text('Uber Eats',400,217,31,weight=600,textAnchor='middle'),text('Lanespan Pizza & Pub (Emeryville)',400,258,23,'#888888',textAnchor='middle'),arrow(657,207,75,True),rect(30,309,740,1,'#cccccc')]
 names=['Grilled Chicken Rice Bowl','Roasted Veggie Grain Bowl','Chicken Caesar Salad','Turkey Avocado Wrap','Falafel Pita Pocket','Tomato Soup & Side Salad'];prices=['$15.4','$13.2','$17.9','$19.3','$16.4','$19.4'];desc=['Chicken, rice, broccoli,\nsesame sauce','Quinoa, roasted vegetables,\nchickpeas, tahini','Chicken, romaine, parmesan,\nCaesar dressing','Turkey, avocado, lettuce,\ntomato','Falafel, pita, hummus,\nmixed salad','Tomato soup with\na fresh side salad']
 rows=[]
 for i,name in enumerate(names):
  y=348+i*236
  rows += [text(name,72,y,32,weight=600),text(prices[i],72,y+44,32),text(desc[i],72,y+92,32,'#b4b4b4'),img(['food-chicken.png','food-veggie.png','food-salad.png'][i%3],553,y,176,176),circle(663,y+111,52,'#ffffff'),text('+',689,y+112,47,'#000000',600,textAnchor='middle'),rect(68,y+205,661,2,'#dddddd')]
 ch.append(group(rows,keyframes={'y':track([(20.6,0),(21.6,0),(22.7,0),(23.4,-180)])}))
 return group(ch,start=20.6,end=23.45,keyframes={'y':track([(20.6,1200),(20.9,0)],'easeOut')})
def lunchphone():
 ch=hardware()+header(True)+[group(composer(),start=23.7,end=26.7)]
 ch += [text('Alice',178,390,23,'#999999'),img('alice.png',58,438,76,76),bubble('Can someone order lunch for us?',150,420,568,74),text('Bob',178,530,23,'#999999'),img('bob.png',58,578,76,76),bubble('Vegetarian for me.',150,560,350,74)]
 ch += [show(bubble('Something light.',430,697,308,74,True),17.0,26.7,35,.3),text('Agent',178,816,23,'#999999',start=17.8),show(bubble("Taking everyone’s preferences\ninto account, I found a few good\noptions.",150,846,550,154,fs=32),17.8,26.7,30,.3),show(foodcard(1025),18.3,26.7,30,.4),img('robot.png',58,1340,76,76)]
 ch.append(foodsheet())
 ts=[(15.0,2.3,-700),(15.55,1.05,40),(16.5,1.035,35),(17.6,1.03,-140),(18.5,1.02,-270),(20.0,1.01,-500),(20.7,.875,80),(21.5,.875,80),(22.5,.875,-128),(23.4,.875,-128),(24.2,.65,-56),(25.0,.6,30),(26.7,.63,15)]
 return group(ch,start=15.0,end=26.7,keyframes={'scaleX':track([(t,s)for t,s,y in ts]),'scaleY':track([(t,s)for t,s,y in ts]),'x':track([(t,960-400*s)for t,s,y in ts]),'y':track([(t,y)for t,s,y in ts])})
def mini_card(label,sub,color,art=None,w=390,h=280):
 top=h-74; fs=w/390
 ch=[rect(0,0,w,h,'#e7e7e7',30)]
 body=[rect(0,0,w,top,color,30)]
 def tt(st,x,y,size=18,col='#111111',bold=400):return text(st,x*fs,y*fs,size*fs,col,bold)
 if art:
  body.append(img(art,0,0,w,top))
 elif label=='Marriott Stay':
  body += [img('fall-trees.png',0,0,w,top),rect(38*fs,67*fs,310*fs,150*fs,'#b85b39',18*fs),tt('Sarah',290,99,16,'#ffffff'),tt('214061328',185,130,23,'#ffffff'),tt('Member',280,166,15,'#ffffff')]
 elif label=='Spectrum mini Apps':
  body=[rect(0,0,w,top,'#000000',30)]
  for j,col in enumerate(['#5da3b8','#a1d4db','#eff2df','#d8f0b9','#bfdc8a','#d2ae64','#de7d60','#ca3d4c']):body.append(rect(0,(58+j*19)*fs,w,24*fs,col,0))
  body.append(tt('Find your most used\nAI mini apps',80,91,24,'#000000',600))
 elif label=='Coding Agent':
  body=[rect(0,0,w,top,'#080a0f',30),rect(25*fs,52*fs,340*fs,132*fs,'#11121b',12),circle(35*fs,74*fs,23*fs,'#55c995'),tt('✓',47,73,21,'#ffffff',600),tt('Pull Request is ready!',67,75,21,'#ffffff',600),tt('All checks passed and ready for review.',38,109,15,'#bbbbbb'),rect(33*fs,146*fs,320*fs,38*fs,'#6438ec',10),tt('Create Pull Request',110,155,18,'#ffffff')]
 elif label=='Your spending in August':
  body=[rect(0,0,w,top,'#ffffff',30),tt('▢',183,43,33,'#235b7e'),tt('Spending',154,91,18),tt('£16.59',105,127,57)]
 elif label=='Weekend Plan':
  body=[rect(0,0,w,top,'#ffffff',30)]
  for j,(t1,t2)in enumerate([('Senso-ji Temple','Asakusa'),('Lunch at Sushi Dai','Tsukiji Outer Market'),('Shibuya Walking Tour','Shibuya Crossing, Hachiko')]):
   body += [tt(t1,24,31+j*62,18,'#111111',500),tt(t2,24,57+j*62,13,'#888888'),tt('›',350,34+j*62,23)]
 elif label=='DoorDash Order':
  body=[rect(0,0,w,top,'#fdfdfd',30),tt('Preparing your order',30,38,21,'#111111',600),tt('Arriving in 20–30 minutes',30,69,17,'#888888'),path(f'M{50*fs} {132*fs} H{340*fs}',fill='none',stroke='#444444',strokeWidth=4*fs)]
  for j,ico in enumerate(['●','▣','▰','♟']):body+=[circle((40+j*88)*fs,117*fs,28*fs,'#333333'if j<2 else'#dddddd'),tt(ico,45+j*88,120,16,'#ffffff')]
  body.append(tt('Burger King is preparing your order.',30,176,14,'#666666'))
 elif label=='Check-In':
  body=[rect(0,0,w,top,'#103461',30),rect(45*fs,52*fs,325*fs,160*fs,'#2075a4',20),rect(45*fs,38*fs,325*fs,27*fs,'#d31140',0),tt('BOARDING PASS',63,71,13,'#b2dbe8'),tt('NIKKI PARKER',64,104,20,'#ffffff'),tt('△ DELTA',237,104,19,'#ffffff'),tt('SFO      →      ATL',65,147,24,'#ffffff'),tt('DL409   May22,2024',220,184,12,'#ffffff')]
 elif label=='Starbucks Pickup':
  body=[rect(0,0,w,top,'#194f3e',30),rect(38*fs,25*fs,314*fs,180*fs,'#fdfdfd',8),tt('STARBUCKS',94,43,26,'#174e3a',600),tt('Venti',65,105,18),tt('3/4 Inch Splash of Oatmilk',65,135,14),tt('Personal Cup',65,161,14)]
 elif label=='Love2night':
  body=[rect(0,0,w,top,'#f4e9fa',30),img('alice.png',115*fs,20*fs,160*fs,160*fs),tt('Emily, 27',155,174,19,'#111111',600)]
 elif label=='Uber Ride':
  body=[rect(0,0,w,top,'#e8edeb',30)]
  for j in range(5):body.append(path(f'M0 {(j*40+10)*fs} L{w} {(j*28+35)*fs}',fill='none',stroke='#ffffff',strokeWidth=10*fs))
  body += [rect(23*fs,65*fs,344*fs,140*fs,'#ffffff',16),tt('PIN for this trip',43,88,16),tt('MH02FB2843',43,123,26,'#111111',600),tt('Bajaj Re Compact',43,164,17,'#777777')]
 elif label=='Figma':
  body=[rect(0,0,w,top,'#111111',30)]
  for j,col in enumerate(['#fa6b3e','#b292c5','#e9b4b8','#6744ea']):
   for k in range(5):body.append(circle((20+j*90+k%2*20)*fs,(15+k*30)*fs,29*fs,col))
  body += [rect(28*fs,77*fs,334*fs,150*fs,'#ffffff',20),tt('Spectrum mini App',54,99,16),tt('Barry Shawn',70,146,28,'#111111',600)]
 else:
  body.append(rect(30*fs,66*fs,w-60*fs,top,'#fdfdfd',19*fs))
  if label=='Zoom Meeting':
   body += [tt('Zoom Meeting Invitation',49,83,13),tt('Midweek Check-in',49,113,22,'#111111',600),tt('1:00–1:30PM\nMeeting ID: 978-443-6176',49,150,17,'#888888')]
  elif label=='OpenTable Reservation':
   body += [tt('● OpenTable',49,84,17),tt('Restaurant Nova',49,118,25,'#111111',600),tt('✓ Reservation confirmed',49,155,16,'#479768'),tt('♙ 2  ▣ Fri, Jun19 at6:00PM',49,180,15)]
  elif label=='Wolf Inn Hotel':
   body += [tt('Wolf Inn Hotel',49,84,20,'#111111',600),tt('Mar19–20 · $55.85',49,114,17),tt('Confirmed',49,142,15,'#48936c'),tt('• Check-in from3:00PM\n• Check-out by11:00AM',49,174,15)]
  elif label=='Mail':
   body += [tt('To: Alice',49,85,17),tt('Subject: Dinner this week',49,114,17),tt('Hi Alice,',49,147,17,'#777777'),tt('Could you please provide me with the',49,180,15,'#777777')]
  elif label=='Apartment in New York':
   body += [tt('311EAST91STREET',49,82,15,'#777777'),tt('⌂ House manual',49,123,21,'#111111',500),tt('Instructions and house rules',49,158,16,'#777777')]
  elif label=='Blue Bottle order':
   body += [tt('WINTER LATTE',98,90,17,'#111111',500),tt('$8.00',285,90,16),tt('12oz · Hayes Valley Espresso',98,122,13),tt('Standard – Oat (Default)\nRegular Ice · White Pink',98,146,13)]
  elif label=='eBay':
   body += [tt('Delivery info',49,92,23,'#111111',600),tt('Arrives Feb26 – Mar4,2026',49,130,17),tt('Tracking available shortly',49,165,15,'#777777')]
 # Native fallback artwork stays beneath measured original individual app-art crops.
 artmap={x['label']:x['file'] for x in json.loads((P/'card-art-provenance.json').read_text())} if (P/'card-art-provenance.json').exists() else {}
 if label in artmap:
  body.append(node('image',src=artmap[label],x=0,y=0,width=w,height=top))
 # Small asset-specific icon is native unless the mini-app paper-plane icon is appropriate.
 if label not in artmap and label not in ['Spectrum mini Apps','Coding Agent','Your spending in August','Weekend Plan']:
  body += [circle(9*fs,9*fs,39*fs,'#ffffff'),tt({'Marriott Stay':'M','Zoom Meeting':'zoom','OpenTable Reservation':'●','Starbucks Pickup':'★','Uber Ride':'Uber','Check-In':'△','Mail':'➤','Jump Jump':'➤','Apartment in New York':'⌂'}.get(label,'●'),28,16,17,'#216fae'if label!='Marriott Stay'else'#b41e3d',600)]
 footer={'Check-In':('Delta Check-In','Flight DL287 · Seat 12A'),'Weekend Plan':('Tokyo Weekend Plan','Starts at June 15'),'Figma':('Figma Comment','3 new comments from Barry'),'Blue Bottle order':('Your Blue Bottle order','Winter Latte, 12oz'),'Uber Ride':('Uber Ride','Pickup: Blue Bottle Coffee'),'Zoom Meeting':('Zoom Meeting','Join in 5 minutes'),'Marriott Stay':('Marriott Stay','Tokyo · Jun 21–24'),'OpenTable Reservation':('OpenTable Reservation','3 new comments from Barry')}.get(label,(label,sub))
 ch += [group(body,clip={'width':w,'height':top,'radius':0}),text(footer[0],18*fs,top+10*fs,24*fs,weight=600),text(footer[1],18*fs,top+45*fs,19*fs,'#b1b1b1')]
 return group(ch,clip={'width':w,'height':h,'radius':30})
def montage():
 ch=hardware()+header(True)+composer()
 c1=mini_card('Jump Jump','Pho Ga · Preparing','#e3a8d9','jump-art.png',w=520,h=370);c1.update(x=150,y=450,start=26.7,end=27.5);ch.append(c1)
 c2=mini_card('Zoom Meeting','Join in 5 minutes','#133484',w=520,h=370);c2.update(x=150,y=885,start=26.7,end=27.5);ch.append(c2)
 # Native game scene, isometric geometry is editable.
 game=[rect(29,170,742,1460,'#d2d4e4',78),text('Jump Jump',400,226,31,weight=600,textAnchor='middle'),text('4',400,330,58,weight=600,textAnchor='middle')]
 for x,y,c in [(120,1180,'#444444'),(390,1400,'#444444'),(260,1050,'#bbbbbb'),(650,820,'#72ab27')]:
  game += [path(f'M{x} {y} l130 -73 l130 73 l-130 73 Z',c),path(f'M{x} {y} l130 73 v130 l-130 -73 Z',c),path(f'M{x+130} {y+73} l130 -73 v130 l-130 73 Z','#777777')]
 game += [circle(340,1010,36,'#44376c'),path('M346 1055 Q350 1035 370 1055 L382 1130 Q360 1144 338 1130 Z','#44376c'),circle(585,1190,70,'none',stroke='#7a9ef4',strokeWidth=5)]
 ch.append(group([rect(29,25,742,1608,'#000000',120),group(game,clip={'x':29,'y':25,'width':742,'height':1608,'radius':120})],start=27.5,end=28.25))
 # Driver / ride app native preview.
 driver=[rect(29,170,742,1460,'#f7f7f7',78),text('Uber Driver',400,226,31,weight=600,textAnchor='middle'),text('You’re online',400,330,48,weight=600,textAnchor='middle'),rect(65,430,670,750,'#e1e7df',30)]
 for j in range(7):driver.append(path(f'M75 {470+j*100} L730 {510+j*70}',fill='none',stroke='#ffffff',strokeWidth=25))
 driver += [circle(370,770,60,'#111111'),text('Finding your next trip',400,1250,35,textAnchor='middle')]
 ch.append(group([rect(29,25,742,1608,'#000000',120),group(driver,clip={'x':29,'y':25,'width':742,'height':1608,'radius':120})],start=28.25,end=28.75))
 # Health native dashboard.
 health=[rect(29,170,742,1460,'#f3f3f7',78),text('Health',400,226,31,weight=600,textAnchor='middle'),rect(65,310,74,74,'#e42236',16),text('H',102,318,49,'#ffffff',textAnchor='middle'),text('Health Check',157,324,36),text('Tuesday, June 16',65,423,21,'#888888'),text('Today’s Health',65,470,54),rect(65,555,670,440,'#ffffff',20),circle(130,655,228,'none',stroke='#37d65b',strokeWidth=27),text('92',245,708,91,textAnchor='middle'),text('Readiness',245,808,23,'#777777',textAnchor='middle'),text('Normal range',433,610,24,'#408958'),text('Vitals look steady',433,685,29),text('Resting heart rate,\noxygen saturation, and\nsleep are aligned with\nyour baseline.',433,771,25,'#777777')]
 for i,(label,val,col)in enumerate([('Heart Rate','72','#e12d3a'),('Blood Oxygen','98','#088cef'),('HRV','48','#a951c4'),('Sleep','7:42','#46bba9')]):
  x=65+(i%2)*350;y=1030+(i//2)*225;health +=[rect(x,y,320,195,'#ffffff',16),text(label,x+22,y+25,22,'#777777'),text(val,x+22,y+82,55)]
  for j in range(7):health.append(rect(x+25+j*27,y+160,20,13,col,5))
 ch.append(group([rect(29,25,742,1608,'#000000',120),group(health,clip={'x':29,'y':25,'width':742,'height':1608,'radius':120})],start=28.75,end=29.25))
 manus=[rect(29,170,742,1460,'#ffffff',78),text('Manus',400,226,31,weight=600,textAnchor='middle'),text('What can I do for you?',400,690,51,weight=500,textAnchor='middle'),rect(80,825,640,250,'#f8f8f8',40,stroke='#dddddd',strokeWidth=2),text('Give Manus a task to work on...',108,866,27,'#999999')]
 ch.append(group([rect(29,25,742,1608,'#000000',120),group(manus,clip={'x':29,'y':25,'width':742,'height':1608,'radius':120})],start=29.25,end=29.7))
 ts=[(26.7,.63,15),(27.5,.58,60),(28.2,.57,66),(28.75,.55,80),(29.25,.55,80),(29.7,.55,80)]
 return group(ch,start=26.7,end=29.7,keyframes={'scaleX':track([(t,s)for t,s,y in ts]),'scaleY':track([(t,s)for t,s,y in ts]),'x':track([(t,960-400*s)for t,s,y in ts]),'y':track([(t,y)for t,s,y in ts])})
L=[]
# Intro native type and true static icon assets.
L.append(text('Introducing API for',960,426,84,weight=650,textAnchor='middle',start=0,end=1.65))
L.append(group([img('app-store.png',0,0,108,91),text('Mini Apps',126,0,82,weight=650),text('in',526,0,82,weight=650,start=.25),img('messages.png',617,-6,93,93,start=.45),text('iMessage',735,0,82,weight=650,start=.55)],396,548,start=0,end=1.65))
L.append(phone1())
# Group-avatar camera bridge.
# Four independently cropped high-resolution avatar assets, measured at14.5s.
for file,x,y,w,h,dx,dy in [('bob-large.png',0,0,1110,830,922,210),('laptop-person.png',1140,0,640,416,968,232),('robot-large.png',1320,430,600,650,968,268),('alice-large.png',400,820,720,260,920,267)]:
 L.append(img(file,x,y,w,h,start=13.8,end=15.25,originX=0,originY=0,keyframes={'x':track([(13.8,x-60),(14.5,x),(15.25,dx)]),'y':track([(13.8,y-50),(14.5,y),(15.25,dy)]),'scaleX':track([(13.8,1.15),(14.5,1),(15.25,.045)]),'scaleY':track([(13.8,1.15),(14.5,1),(15.25,.045)])}))
L.append(lunchphone())
# Selection avatars and shopping cart.
for name,positions,st,en in [('alice.png',[(20.7,840,78),(21.5,845,75),(22.5,1180,240),(23.4,1120,180)],20.7,23.45),('bob.png',[(20.7,490,500),(21.5,490,500),(22.5,1100,460),(23.4,1120,450)],20.7,23.45),('laptop-person.png',[(20.7,1330,590),(21.5,1330,590),(22.5,1175,650),(23.4,1140,620)],20.7,23.45)]:
 L.append(img(name,0,0,100,100,start=st,end=en,keyframes={'x':track([(t,x)for t,x,y in positions]),'y':track([(t,y)for t,x,y in positions])}))
L.append(bubble('🛒 1',1310,618,145,85,fs=46,start=22.2,end=23.4))
# Emoji celebratory motion; genuine Apple emoji unavailable, explicitly fallback emoji.
for i,(s,x,y,size)in enumerate([('🍕',400,160,120),('🍕',760,-40,170),('🍜',1100,250,155),('🍕',1230,580,60),('🥗',510,820,85)]):
 L.append(text(s,x,y,size,start=23.4,end=26.7,keyframes={'y':track([(23.4,y-500),(24.5,y),(26.7,y+600)]),'rotation':track([(23.4,-20+i*8),(26.7,30-i*8)])}))
for i,(x,y)in enumerate([(520,360),(570,580),(1080,800)]):L.append(show(bubble('Order!',x,y,110,62,fs=30),23.7+i*.15,26.6,20,.25))
L.append(montage())
# Independently editable card collage.
labels=[('Love2night','Your match for tonight','#f4e9fa'),('Apartment in New York','Your reservation details','#b6c9a7'),('DoorDash Order','Burger King · Whopper Meal','#f24d42'),('Starbucks Pickup','Order #4821','#006c45'),('Mail','To: Alice','#3aa8e5'),('Check-In','Flight · Seat12A','#103461'),('Marriott Stay','Tokyo · Jun21–24','#8c2238'),('Zoom Meeting','Join in5minutes','#184aab'),('OpenTable Reservation','3new comments from Barry','#bd1141'),('Wolf Inn Hotel','View your booking details','#174d96'),('Weekend Plan','Tokyo · 2days','#fdfdfd'),('Jump Jump','Pho Ga · Preparing','#dd83ce'),('Spectrum mini Apps','Find your most used AI mini apps','#997bea'),('Coding Agent','Pull Request Ready','#080a0f'),('Your spending in August','View your spending summary','#ffffff'),('Uber Eats','Lanespan Pizza & Pub','#dec091'),('eBay','View your delivery details','#3163db'),('Figma','Barry Shawn','#111111'),('Blue Bottle order','Pickup at9:30AM','#ffffff'),('Uber Ride','Your ride is here','#111111')]
coll=[]
for i,(lab,sub,col)in enumerate(labels):
 row=i//5;column=i%5
 c=mini_card(lab,sub,col,'jump-art.png'if lab=='Jump Jump'else('pizza-photo.png'if lab=='Uber Eats'else None),w=390,h=280)
 positions31=[(-80,-70),(382,-104),(844,-130),(1308,-149),(1756,-175),(-133,277),(329,249),(789,220),(1258,197),(1714,180),(-183,627),(277,603),(735,578),(1206,552),(1668,529),(-230,971),(232,952),(685,933),(1152,908),(1612,877)]
 positions318=[(-49,224),(-550,-300),(679,-6),(1055,-115),(1428,-181),(25,500),(-300,300),(751,275),(1130,166),(1500,65),(96,777),(451,670),(825,559),(1204,448),(1575,343),(-330,1050),(526,950),(900,844),(1277,730),(1644,618)]
 x,y=positions31[i];xx,yy=positions318[i];c.update(x=x,y=y)
 widthfactor=[1,388/390,393/390,380/390,1,388/390,385/390,395/390,384/390,389/390,390/390,383/390,394/390,388/390,382/390,390/390,383/390,388/390,389/390,388/390][i]
 c['keyframes']={'x':track([(29.7,x),(31.35,x),(31.8,xx),(32.7,xx+2200)],'easeInOut'),'y':track([(29.7,y),(31.35,y),(31.8,yy),(32.7,yy-1400)],'easeInOut'),'scaleX':track([(29.7,widthfactor),(31.35,widthfactor),(31.8,widthfactor*.875),(32.7,widthfactor*.65)]),'scaleY':track([(29.7,1),(31.35,1),(31.8,.875),(32.7,.65)])}
 coll.append(c)
L.append(group(coll,start=29.7,end=32.9,originX=960,originY=540,keyframes={'scaleX':track([(29.7,5.5),(30.8,1),(32.9,1)]),'scaleY':track([(29.7,5.5),(30.8,1),(32.9,1)]),'x':track([(29.7,850),(30.8,0),(32.9,0)]),'y':track([(29.7,-100),(30.8,0),(32.9,0)]),'opacity':track([(29.7,1),(32.4,1),(32.9,0)])}))
# Kinetic category list with native icons and independently editable text.
L.append(text('Now your agent can send',270,493,80,start=32.8,end=36.5,keyframes={'x':track([(32.8,270),(34.0,270),(34.5,240)])}))
cats=['agentic apps','generative UIs','games','sign-in requests','live screen sharing','live delivery tracking','menus','dashboards','mini apps'];colors=['#ed6f80','#a983de','#62b9e3','#76cb80','#60c7e9','#deb36e','#888888','#9572df','#eeeeee'];symbols=['▦','◇','⌘','➜','▣','◆','•••','▥','']
active=[32.8,33.9,34.1,34.27,34.43,34.6,34.77,34.94,35.2]
for i,cat in enumerate(cats):
 y=505+i*92
 icon=miniicon(0,0,100)if i==8 else group([rect(0,0,100,80,colors[i],35),text(symbols[i],50,6,58,'#ffffff',textAnchor='middle')])
 ty=text(cat,127,0,80)
 ch=group([icon,ty],1160,y,start=32.8,end=36.5)
 times=active+[36.5]
 ys=[];ops=[]
 for j,t in enumerate(active):
  ys.append((t,505+(i-j)*92));ops.append((t,1 if i==j else (0 if t<33.8 else .1)))
  if j<len(active)-1:
   ys.append((active[j+1]-.10,505+(i-j)*92));ops.append((active[j+1]-.10,1 if i==j else (0 if active[j+1]-.10<33.8 else .1)))
 ys.append((36.5,505+(i-8)*92));ops.append((36.5,1 if i==8 else .05))
 ch['keyframes']={'y':track(ys,'easeOut'),'opacity':track(ops,'easeOut')}
 L.append(ch)
# CTA and Photon signature.
L.append(show(group([text('Available today at',0,0,76,weight=650),text('tryphoton.ai',633,0,76,'#57b5e2',650)],438,495),36.5,39.6,25,.35))
mark=[rect(0,31,21,48,'#000000',4,rotation=14),rect(53,0,21,48,'#000000',4,rotation=14),rect(84,65,21,48,'#000000',4,rotation=14)]
L.append(show(group([group(mark),text('Photon',140,-5,120,weight=650)],698,479),39.6,42,0,.35))
scene={'title':'Photon Mini Apps API — independent native reconstruction','width':1920,'height':1080,'fps':30,'duration':42,'background':'#fdfdfd','gradients':[{'id':'blue','type':'linear','stops':[{'offset':'0%','color':'#4cc0e8'},{'offset':'100%','color':'#078ff3'}]},{'id':'mail','type':'linear','stops':[{'offset':'0%','color':'#48b9e7'},{'offset':'100%','color':'#078ff3'}]}],'source':{'path':'source.mp4','sourceStart':0,'sourceEnd':42,'notes':'Full-timeline independent reconstruction; native chat/container/footer/type/camera layers; declared per-mini-app static artwork includes bitmap internal UI copy, plus photo/avatar/icon/hardware crops. Measurements from native diagnostic frames; many easing/camera timing points remain fitted estimates. SF Pro identity not proven. No audio. Not certified one-to-one.'},'layers':L}
# Actual font embeds are added only when verified assets exist.
fonts=[]
for family,file,weight in [('Recreation UI','SF-Pro-Display-Regular.otf',400),('Recreation UI','SF-Pro-Display-Semibold.otf',600),('Recreation UI','SF-Pro-Display-Bold.otf',700)]:
 q=P/'assets'/file
 if q.exists() and q.read_bytes()[:4] in [b'OTTO',b'\x00\x01\x00\x00']:fonts.append({'family':family,'src':'assets/'+file,'weight':weight})
if fonts:scene['fonts']=fonts
(P/'scene.json').write_text(json.dumps(scene,indent=2))
print('layers',N,'top',len(L),'fonts',fonts)
