from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from collections import Counter
import json,copy
root=Path('/workspace/imessage-recreations');d=root/'references/05-linq';s=json.loads((d/'scene.json').read_text());prov=json.loads((d/'assets/asset-provenance.json').read_text());counter=0

def ident(n):
 global counter;counter+=1;return f'broad-v5-{n}-{counter}'
def rect(x,y,w,h,fill='#ffffff',radius=0,**kw):return dict(type='rect',id=ident('rect'),x=x,y=y,width=w,height=h,fill=fill,radius=radius,**kw)
def txt(t,x,y,z=32,fill='#111111',weight=400,**kw):return dict(type='text',id=ident('text'),text=t,x=x,y=y,fontFamily='SF Pro Display',fontSize=z,fontWeight=weight,lineHeight=z*1.18,fill=fill,**kw)
def img(src,x,y,w,h,**kw):return dict(type='image',id=ident('image'),src=src,x=x,y=y,width=w,height=h,**kw)
def group(ch,a,b,**kw):return dict(type='group',id=ident('group'),children=ch,start=a,end=b,**kw)
def tr(*pairs):return [{'t':t,'value':v,'ease':'easeOut'} for t,v in pairs]
def pic(fr):return Image.open(d/f'keyframes/{fr}.png').convert('RGBA')
def asset(im,name,fr,box,kind='bounded static internal app artwork'):
 src=f'assets/{name}.png';im.save(d/src);prov.append({'path':src,'timestamp':float(fr),'box':box,'kind':kind});return src
def crop(fr,box,name,kind='bounded static internal app artwork'):return asset(pic(fr).crop(box),name,fr,box,kind)
def blue(fr,box):
 vals=Counter(p for p in pic(fr).convert('RGB').crop(box).getdata() if p[0]<100 and p[2]>180);c=vals.most_common(1)[0][0];return '#'+''.join(f'{x:02x}' for x in c)
def bubble(t,x,y,w,h,z,bluefill=None):
 fill=bluefill or '#e7e7e7';tail=f'M {w-45} {h-15} Q {w-26} {h+10} {w-18} {h+13} Q {w-32} {h-8} {w-18} {h-22} Z' if bluefill else f'M 18 {h-26} Q 46 {h-5} 10 {h+14} Q 27 {h+12} 48 {h-9} Z'
 return dict(type='group',id=ident('bubble'),x=x,y=y,children=[rect(0,0,w,h,fill,min(h/2,48)),dict(type='path',id=ident('tail'),d=tail,fill=fill),txt(t,30,20,z,'#ffffff' if bluefill else '#151515')])
def sprite(im):
 # Close neutral bright outlines, then flood the exterior; keep their enclosed dark interiors.
 p=im.convert('RGB');mask=Image.new('L',im.size);mp=mask.load();pp=p.load()
 for yy in range(im.height):
  for xx in range(im.width):
   r,g,b=pp[xx,yy];mp[xx,yy]=255 if max(r,g,b)-min(r,g,b)<65 and (r+g+b)/3>120 else 0
 mask=mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
 ImageDraw.floodfill(mask,(0,0),128,thresh=0);v=mask.load()
 for yy in range(im.height):
  for xx in range(im.width):v[xx,yy]=0 if v[xx,yy]==128 else 255
 im=im.copy();im.putalpha(mask.filter(ImageFilter.GaussianBlur(.25)));return im

preview=crop('005.70',(351,107,861,500),'chess-preview-card-exact')
pawn_icon=crop('006.50',(345,572,370,611),'reply-pawn-icon','isolated monochrome chess icon')
# Initial chessboard: actual static board, with the two moving pawns removed and separately animated.
board=pic('008.20');fbox=(557,433,635,511);ebox=(480,279,558,357)
white=sprite(board.crop(fbox));black=sprite(board.crop(ebox));board.paste(board.crop((403,279,481,357)),fbox[:2]);board.paste(board.crop((326,279,404,357)),ebox[:2])
board_src=asset(board.crop((152,0,810,720)),'chess-board-without-moving-pawns','008.20',(152,0,810,720),'static board artwork; moving pawn pixels removed')
white_src=asset(white,'white-pawn-sprite','008.20',fbox,'isolated animated pawn sprite');black_src=asset(black,'black-pawn-sprite','008.20',ebox,'isolated animated pawn sprite')
flight_top=crop('012.00',(188,98,772,720),'flight-initial-header-card')
grid=crop('020.00',(198,0,763,720),'jewelry-grid-internal')
logo=crop('024.20',(138,349,226,378),'apple-cash-brand-label','isolated brand label')
reaction=pic('025.00').crop((498,282,594,381));pp=reaction.load()
for yy in range(reaction.height):
 for xx in range(reaction.width):
  r,g,b,a=pp[xx,yy]
  keep=(b>100 and b>r*1.6) or (r-b>35 and g>70)
  if not keep:pp[xx,yy]=(r,g,b,0)
react=crop('025.00',(498,282,594,381),'payment-reaction-original','isolated message reaction')
reaction.save(d/react)
# App game: one real static app board, one queen sprite, native dimming and winning overlay.
game=pic('029.00');queenbox=(463,136,519,194);queen=sprite(game.crop(queenbox));game.paste(game.crop((463,249,519,307)),queenbox[:2])
game_src=asset(game.crop((275,0,759,720)),'chess-game-without-moving-queen','029.00',(275,0,759,720),'static game artwork with moving queen removed')
queen_src=asset(queen,'black-queen-sprite','029.00',queenbox,'isolated animated queen sprite')
win=crop('030.50',(341,315,617,405),'chess-winning-label')
interior=crop('038.00',(319,263,763,596),'restaurant-interior-full')
food='assets/restaurant-food.png'
orderphone=crop('042.00',(30,0,301,301),'gallery-order-extended')
topcenter=crop('041.50',(345,0,617,44),'gallery-top-center-part')
topright=crop('042.00',(662,0,932,18),'gallery-top-right-part')
bottomcenter=crop('042.00',(345,685,618,720),'gallery-bottom-center-part')
bottomright=crop('041.50',(663,663,932,720),'gallery-bottom-right-part')

new=[];fare=None;detail=None;rest=None;gallery=None;bridge=None
for l in s['layers']:
 a=l.get('start')
 if a==4.93:
  new.append(group([img(preview,351,107,510,393)],4.93,6.97,keyframes={'y':tr((4.93,35),(5,25),(5.7,0),(6.1,0),(6.45,-61)),'opacity':tr((4.93,0),(4.98,1))}));continue
 if a==5.35:
  b=bubble('Yo i’m bored, chess battle?',391,511,470,83,38,blue('005.70',(400,520,850,590)));b['children'][-1]['x']=27
  new.append(group([b],5.3,6.97,keyframes={'y':tr((5.3,20),(5.5,0),(6.1,0),(6.45,-61)),'opacity':tr((5.3,0),(5.48,1))}));new.append(group([txt('Delivered',709,607,26,'#8a8a8a',700)],5.6,6.1));continue
 if a==6.1:
  b=bubble('Always down',95,554,308,84,38);b['children'][-1]['y']=16;b['children'].append(img(pawn_icon,250,18,25,39))
  new.append(group([b],6.1,6.97,keyframes={'opacity':tr((6.1,0),(6.4,1)),'y':tr((6.1,100),(6.45,0))}));continue
 if a==6.97:
  ch=[img(board_src,0,0,658,720),img(white_src,405,510,78,78,keyframes={'y':tr((6.97,510),(7.35,510),(7.65,433))}),img(black_src,328,125,78,78,keyframes={'y':tr((6.97,125),(7.8,125),(8.05,279))}),rect(405,510,78,78,'#5ca8ff',opacity=0,keyframes={'opacity':tr((7.12,0),(7.18,.3),(7.35,.3),(7.5,0))})]
  new.append(group(ch,6.97,8.57,x=152,keyframes={'opacity':tr((6.97,0),(7,.7),(7.15,1)),'y':tr((6.97,15),(7,15),(7.35,0))}));continue
 if a==8.57:
  for b in l.get('children',[]):
   if b.get('type')=='group':
    for q in b.get('children',[]):
     if q.get('fill')=='#347ff1':q['fill']=blue('009.20',(330,270,850,470))
     if q.get('type')=='text':q['x']=33;q['y']=22
 if a==10.57:bridge=copy.deepcopy(l);l['end']=11.8666667
 if a==12.07:fare=l;continue
 if a==19.3:detail=l;continue
 if a==22.85:
  b=bubble('can you order my\nweekly groceries?',509,49,359,124,40,blue('024.20',(520,60,850,160)));b['children'][-1].update(x=28,y=18,lineHeight=42)
  new.append(group([b],22.85,25.33,keyframes={'opacity':tr((22.85,0),(23.03,1)),'y':tr((22.85,24),(23.03,0))}));continue
 if a==23.7:
  sure=bubble('Sure, it’ll be $166.89',110,206,385,87,36);sure['children'][-1].update(x=32,y=23)
  ch=[sure,rect(110,324,431,348,'#202020',43),dict(type='path',id=ident('cash-tail'),fill='#202020',d='M 133 643 Q 149 671 131 687 Q 152 683 170 665 Z'),img(logo,138,349,88,29),txt('$166.89 Request',155,429,45.5,'#ffffff'),rect(229,557,193,89,'#ffffff',46),txt('Pay',326,577,42,'#111111',400,textAnchor='middle'),img(react,498,282,96,99,start=24.4)]
  new.append(group(ch,23.7,25.33,keyframes={'opacity':tr((23.7,0),(23.88,1)),'y':tr((23.7,24),(23.88,0))}));continue
 if a==28.83:
  ch=[img(game_src,0,0,484,720),img(queen_src,188,136,56,58,keyframes={'x':tr((28.83,188),(29.35,188),(29.65,417)),'y':tr((28.83,136),(29.35,136),(29.65,365))}),rect(0,0,484,720,'#000000',opacity=0,keyframes={'opacity':tr((28.83,0),(29.75,0),(29.95,.32))})]
  new.append(group(ch,28.83,31.37,keyframes={'x':tr((28.83,500),(29,275),(29.5,237))}));continue
 if a==30.2 and any(q.get('type')=='text' and q.get('text')=='YOU WON!!' for q in l.get('children',[])):
  new.append(group([img(win,341,315,276,90)],30.25,31.37,keyframes={'opacity':tr((30.25,0),(30.4,1))}));continue
 if a==35.63:rest=l;continue
 if a==39.5:
  for q in l.get('children',[]):
   if q.get('type')=='rect' and q.get('width')==960:q['fill']='url(#boarding-gradient)'
 if a==40.63:gallery=l;continue
 if a==44.6:
  for q in l.get('children',[]):
   if q.get('text')=='What will you build?':q.update(fontSize=48.7,y=329)
 new.append(l)
# Flight stage: actual first state, native fast entrance, diagonal pan into final fare state.
if bridge:
 bridge['id']=ident('flight-backdrop');bridge.update(start=11.8666667,end=15.63,blur=10,opacity=.75,keyframes={})
 def rename(q):
  q['id']=ident('background')
  for z in q.get('children',[]):rename(z)
 rename(bridge);new.append(bridge)
new.append(group([img(flight_top,188,98,584,622)],11.8666667,12.75,clip={'x':188,'y':0,'width':584,'height':720},keyframes={'y':tr((11.8666667,580),(11.9333333,0),(12.3,0),(12.7,-260)),'opacity':tr((11.8666667,0),(11.9333333,1),(12.35,1),(12.75,0))}))
if fare:
 fare.update(start=12.35,end=13.9);fare['keyframes']={'opacity':tr((12.35,0),(12.75,1)),'x':tr((12.35,100),(13.3,0))};new.append(fare)
# Jewelry grid stays a grid before the measured detail zoom.
under=group([rect(95,160,540,90,'#e7e7e7',45),txt("Here's what's hot right now",125,182,32),rect(95,280,360,134,'#e7e7e7',40)],19.3,21.55,blur=10,opacity=.45);new.append(under)
inner=group([img(grid,0,0,565,720)],19.3,21.05,originX=141.25,originY=500,keyframes={'scaleX':tr((19.3,1),(20.25,1),(20.85,1.9)),'scaleY':tr((19.3,1),(20.25,1),(20.85,1.9)),'x':tr((19.3,0),(20.25,0),(20.85,141.25)),'y':tr((19.3,0),(20.25,0),(20.85,-140))})
new.append(group([inner],19.3,21.05,x=198,clip={'width':565,'height':720},keyframes={'opacity':tr((19.3,0),(19.5,1),(20.75,1),(21.05,0))}))
if detail:detail['keyframes']={'opacity':tr((19.3,0),(20.75,0),(21.05,1))};new.append(detail)
# Restaurant carousel: authentic landscape interior, independent horizontal pan, measured vertical camera shift.
if rest:
 rest['children'] +=[rect(190,303,584,333),group([img(food,201,303,333,333),img(interior,558,303,444,333)],35.63,38.13,keyframes={'x':tr((35.63,0),(37,0),(38,-239))},clip={'x':190,'y':303,'width':584,'height':333})]
 rest['keyframes']={'y':tr((35.63,0),(37,0),(38,-40))};rest['clip']={'x':190,'y':0,'width':584,'height':720};new.append(rest)
# Each column moves independently, matching the actual41.5→42s drift.
children=[]
for q in gallery.get('children',[]) if gallery else []:
 src=q.get('src','')
 if 'gallery-phone-order-part' in src:continue
 if 'gallery-phone-boarding' in src:dy=-16
 elif 'gallery-phone-music' in src or 'gallery-phone-chat' in src:dy=25
 else:dy=0
 y=q.get('y',0);q['keyframes']={'y':tr((40.63,y),(41.5,y),(42,y+dy),(42.27,y+dy*1.54))};children.append(q)
children +=[img(orderphone,30,0,271,301,keyframes={'y':tr((40.63,-25),(41.5,-25),(42,0),(42.27,13.5))}),img(topcenter,345,0,272,44,keyframes={'y':tr((40.63,0),(41.5,0),(42,-16),(42.27,-24.6))}),img(topright,662,0,270,18,keyframes={'y':tr((40.63,-25),(41.5,-25),(42,0),(42.27,13.5))}),img(bottomcenter,345,685,273,35,keyframes={'y':tr((40.63,707),(41.5,707),(42,685),(42.27,673.1))}),img(bottomright,663,663,269,57,keyframes={'y':tr((40.63,663),(41.5,663),(42,688),(42.27,701.5))})]
new.append(group(children,40.63,42.27,originX=480,originY=360,keyframes={'scaleX':tr((40.63,3.2),(41.0,1.15),(41.5,1)),'scaleY':tr((40.63,3.2),(41.0,1.15),(41.5,1))}))
s['layers']=new
s.setdefault('gradients',[]).append({'id':'boarding-gradient','type':'linear','stops':[{'offset':p,'color':c} for p,c in [('0%','#24406a'),('20%','#3d4872'),('40%','#545371'),('60%','#6c5c6e'),('80%','#87656a'),('100%','#a56e64')]]})
s['source']['notes']+=' Finalv5 repairs broad-QA scene-state errors: actual preview card/scroll/reply, independently animated pawns and queen over declared app art, measured flight entrance with initial/panned states, jewelry grid before detail, payment geometry/assets, restaurant carousel, separate phone-column drift, boarding gradient and final title size. Motion curves remain fitted where not measured.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2));(d/'revision-final-v5.json').write_text(json.dumps({'changed_time_ranges_vs_v4':[[4.93,10.57],[11.8666667,15.63],[19.3,21.55],[22.85,25.33],[28.83,31.37],[35.63,38.13],[39.5,42.27],[44.6,45.93]]},indent=2));print('Linq broad-QA corrections written')
